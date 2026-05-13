import os
import cloudinary
import cloudinary.uploader
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required
from extensions import mysql
from utils import admin_required, registrar_log # 🛡️ Importamos el log
from recetas import calcular_costo_completo

productos_bp = Blueprint("productos_bp", __name__, url_prefix="/productos")

# CONFIGURACIÓN DE CLOUDINARY
cloudinary.config( 
  cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME'), 
  api_key = os.getenv('CLOUDINARY_API_KEY'), 
  api_secret = os.getenv('CLOUDINARY_API_SECRET'),
  secure = True
)

# ==========================================
# SUBIDA DE IMAGEN A LA NUBE
# ==========================================
@productos_bp.route("/upload-image", methods=["POST"])
@login_required
@admin_required
def upload_image():
    if 'imagen' not in request.files:
        return jsonify({"error": "No se envió ningún archivo"}), 400

    file = request.files['imagen']
    if file.filename == '':
        return jsonify({"error": "Nombre de archivo vacío"}), 400

    try:
        # 💡 SAAS-IFICATION: Aislamos las imágenes por tenant en Cloudinary.
        tenant_id = current_user.tenant_id
        
        upload_result = cloudinary.uploader.upload(
            file,
            folder=f"precivox/tenants/{tenant_id}/productos",
            resource_type="image"
        )
        secure_url = upload_result.get("secure_url")
        
        # 🛡️ AUDITORÍA: Registro de subida de archivos
        registrar_log(f"Subió nueva imagen a la nube: {file.filename}")
        
        return jsonify({
            "mensaje": "Imagen persistente en la nube ✅",
            "filename": secure_url
        }), 201

    except Exception as e:
        current_app.logger.error(f"Error en Cloudinary: {str(e)}")
        return jsonify({"error": "Fallo al subir a la nube"}), 500

# ==========================================
# GESTIÓN DE PRODUCTOS
# ==========================================

@productos_bp.route("/", methods=["GET"])
@login_required
def get_productos():
    cursor = mysql.connection.cursor()
    tenant_id = current_user.tenant_id
    
    try:
        # 💡 SAAS-IFICATION: Filtramos productos por el tenant_id del usuario logueado.
        cursor.execute("SELECT * FROM productos WHERE tenant_id = %s", (tenant_id,))
        rows = cursor.fetchall()
        return jsonify(list(rows))
    finally:
        if cursor: cursor.close()

@productos_bp.route("/", methods=["POST"])
@login_required
@admin_required
def add_producto():
    data = request.json
    nombre = data.get("nombre")
    tenant_id = current_user.tenant_id
    
    cursor = mysql.connection.cursor()
    try:
        # 💡 SAAS-IFICATION: Insertamos el tenant_id al crear un nuevo producto.
        cursor.execute("""
            INSERT INTO productos (nombre, categoria, descripcion, precio, imagen, stock, controla_stock, tenant_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (nombre, data.get("categoria"), data.get("descripcion"), 
              data.get("precio"), data.get("imagen"), data.get("stock", 0), data.get("controla_stock", False), tenant_id))
        mysql.connection.commit()
        
        # 🛡️ AUDITORÍA: Registro de creación
        registrar_log(f"Creó el producto: {nombre}")
        
        return jsonify({"mensaje": "Producto creado"}), 201
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor: cursor.close()

@productos_bp.route("/<int:id>", methods=["PUT"])
@login_required
@admin_required
def update_producto(id):
    data = request.json
    nombre = data.get("nombre")
    tenant_id = current_user.tenant_id

    cursor = mysql.connection.cursor()
    try:
        # 💡 SAAS-IFICATION: Aseguramos que solo se pueda actualizar un producto del tenant correcto.
        cursor.execute("""
            UPDATE productos
            SET nombre=%s, categoria=%s, descripcion=%s, precio=%s, imagen=%s,
                pax=%s, utilidad_porcentaje=%s, stock=%s, controla_stock=%s
            WHERE id_producto=%s AND tenant_id = %s
        """, (nombre, data.get("categoria"), data.get("descripcion"), 
              data.get("precio"), data.get("imagen"), data.get("pax"),
              data.get("utilidad_porcentaje"), data.get("stock"), data.get("controla_stock"), id, tenant_id))
        mysql.connection.commit()
        calcular_costo_completo(id, tenant_id)
        
        # 🛡️ AUDITORÍA: Registro de actualización
        registrar_log(f"Actualizó el producto ID {id}: {nombre}")
        
        return jsonify({"mensaje": "Producto actualizado"})
    finally:
        if cursor: cursor.close()

@productos_bp.route("/<int:id>", methods=["DELETE"])
@login_required
@admin_required
def delete_producto(id):
    tenant_id = current_user.tenant_id
    cursor = mysql.connection.cursor()
    try:
        # 💡 SAAS-IFICATION: Aseguramos que solo se pueda borrar un producto del tenant correcto.
        cursor.execute("DELETE FROM productos WHERE id_producto=%s AND tenant_id = %s", (id, tenant_id))
        mysql.connection.commit()
        
        # 🛡️ AUDITORÍA: Registro de eliminación
        registrar_log(f"Eliminó el producto ID {id}")
        
        return jsonify({"mensaje": "Eliminado"})
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor: cursor.close()

@productos_bp.route("/public", methods=["GET"])
def get_productos_public():
    # ⚠️ ADVERTENCIA DE SEGURIDAD MULTI-TENANT:
    # Este endpoint es para la landing page pública. En un sistema multi-tenant,
    # no podemos simplemente devolver todos los productos. Necesitamos saber de qué tenant
    # mostrar los productos.
    #
    # SOLUCIÓN TEMPORAL: Asumimos que la landing pública siempre corresponde al tenant con id=1 (Sweetland).
    # La solución definitiva implicaría usar subdominios (sweetland.precivox.com) o
    # un identificador en la URL para determinar el tenant dinámicamente.
    tenant_id_publico = 1
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("SELECT id_producto, nombre, categoria, descripcion, precio, imagen FROM productos WHERE tenant_id = %s ORDER BY nombre", (tenant_id_publico,))
        productos = cursor.fetchall()
        return jsonify({"success": True, "productos": list(productos)})
    finally:
        if cursor: cursor.close()