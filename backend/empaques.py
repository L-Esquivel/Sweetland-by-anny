from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from db import get_db # 🟢 Importamos el nuevo gestor de DB
from psycopg2.extras import DictCursor # 🟢 Para obtener resultados como diccionarios
import logging
from utils import admin_required # 💡 FIX: Importar el decorador de admin
from recetas import calcular_costo_completo # Importamos la función de costeo

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

empaques_bp = Blueprint("empaques", __name__, url_prefix="/empaques")

# ==================== CATÁLOGO GENERAL DE EMPAQUES ====================
# Estos son los que aparecerán en la nueva sección de "Insumos"

@empaques_bp.route("/", methods=["GET"])
@login_required
def get_empaques():
    tenant_id = current_user.tenant_id
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            # 💡 SAAS-IFICATION: Filtramos por tenant_id.
            # FIX: Se usa COALESCE para evitar precios nulos (NaN en frontend) y se convierte a dict.
            cursor.execute("""
                SELECT id_empaque, nombre, descripcion, COALESCE(precio, 0) as precio 
                FROM empaques WHERE tenant_id = %s ORDER BY nombre
            """, (tenant_id,))
            empaques_raw = cursor.fetchall()
            empaques = [dict(row) for row in empaques_raw]
            return jsonify(empaques)
    except Exception as e:
        logger.error(f"Error en get_empaques: {str(e)}")
        return jsonify({"error": "Error al obtener el catálogo de empaques"}), 500

@empaques_bp.route("/", methods=["POST"])
@admin_required # 💡 FIX: Se añade decorador para que solo admins puedan crear empaques.
def add_empaque():
    tenant_id = current_user.tenant_id
    conn = get_db()
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No se recibieron datos JSON"}), 400

        nombre = data.get("nombre")
        descripcion = data.get("descripcion", "")
        precio = float(data.get("precio") or 0)

        if not nombre:
            return jsonify({"error": "El nombre es obligatorio"}), 400

        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO empaques (nombre, descripcion, precio, tenant_id) VALUES (%s, %s, %s, %s)",
                (nombre, descripcion, precio, tenant_id)
            )
            conn.commit()
        return jsonify({"mensaje": "Empaque creado en el catálogo"}), 201
    except Exception as e:
        conn.rollback() # 💡 FIX: Se usa la conexión correcta para el rollback y se simplifica el manejo de errores.
        logger.error(f"Error en add_empaque: {e}", exc_info=True)
        return jsonify({"error": "Error interno al crear el empaque"}), 500

@empaques_bp.route("/<int:id>", methods=["PUT"])
@admin_required # FIX: Solo admins pueden modificar el catálogo.
def update_empaque(id):
    tenant_id = current_user.tenant_id
    try:
        data = request.get_json()
        nombre = data.get("nombre")
        descripcion = data.get("descripcion", "")
        precio = float(data.get("precio") or 0)

        if not nombre:
            return jsonify({"error": "El nombre es obligatorio"}), 400

        conn = get_db()
        try:
            with conn.cursor() as cursor:
                # 💡 SAAS-IFICATION: Aseguramos que solo se pueda actualizar un empaque del tenant correcto.
                cursor.execute(
                    "UPDATE empaques SET nombre=%s, descripcion=%s, precio=%s WHERE id_empaque=%s AND tenant_id = %s",
                    (nombre, descripcion, precio, id, tenant_id)
                )
                conn.commit()
                return jsonify({"mensaje": "Empaque actualizado correctamente"})
        except Exception as e:
            get_db().rollback()
            logger.error(f"Error en update_empaque: {str(e)}")
            return jsonify({"error": "Error al actualizar el empaque"}), 500
    except Exception as e:
        logger.error(f"Error en update_empaque: {str(e)}")
        return jsonify({"error": "Error al procesar los datos del empaque"}), 500

@empaques_bp.route("/<int:id>", methods=["DELETE"])
@admin_required # FIX: Solo admins pueden borrar del catálogo.
def delete_empaque(id):
    tenant_id = current_user.tenant_id
    try:
        conn = get_db()
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            # VERIFICACIÓN: ¿Está este empaque en uso por algún producto?
            # 💡 SAAS-IFICATION: La verificación de uso también debe ser por tenant.
            cursor.execute("SELECT COUNT(*) as total FROM recetas_empaques WHERE id_empaque = %s AND tenant_id = %s", (id, tenant_id))
            uso = cursor.fetchone()
            
            if uso and uso['total'] > 0:
                return jsonify({"error": "No se puede eliminar: el empaque está asignado a productos en la sección de Recetas"}), 400
            
            # 💡 SAAS-IFICATION: Aseguramos que solo se pueda borrar un empaque del tenant correcto.
            cursor.execute("DELETE FROM empaques WHERE id_empaque=%s AND tenant_id = %s", (id, tenant_id))
            conn.commit()
            return jsonify({"mensaje": "Empaque eliminado del catálogo"})
    except Exception as e:
        get_db().rollback()
        logger.error(f"Error en delete_empaque: {str(e)}")
        return jsonify({"error": "Error al eliminar el empaque"}), 500

# ==================== EMPAQUES ASIGNADOS A PRODUCTOS ====================
# Estos se usan específicamente dentro de la sección de recetas de cada producto

@empaques_bp.route("/producto/<int:producto_id>", methods=["GET"])
@login_required
def get_empaques_producto(producto_id):
    tenant_id = current_user.tenant_id
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("""
                SELECT re.id, re.id_empaque, re.cantidad, re.subtotal,
                       e.nombre, e.precio
                FROM recetas_empaques re
                LEFT JOIN empaques e ON re.id_empaque = e.id_empaque
                WHERE re.id_producto = %s AND re.tenant_id = %s
            """, (producto_id, tenant_id))
            filas = cursor.fetchall()

            items = []
            costo_total = 0
            for f in filas:
                precio_unitario = float(f["precio"] or 0)
                cantidad = int(f["cantidad"] or 1)
                subtotal = float(f["subtotal"] or (precio_unitario * cantidad))
                
                costo_total += subtotal
                items.append({
                    "id":         f["id"],
                    "id_empaque": f["id_empaque"],
                    "cantidad":   cantidad,
                    "subtotal":   subtotal,
                    "nombre":     f["nombre"],
                    "precio":     precio_unitario
                })

            return jsonify({"empaques": items, "costo_total_empaque": costo_total})
    except Exception as e:
        logger.error(f"Error en get_empaques_producto: {str(e)}")
        return jsonify({"error": "Error al obtener empaques del producto"}), 500

@empaques_bp.route("/producto/<int:producto_id>", methods=["POST"])
@login_required
def add_empaque_producto(producto_id):
    tenant_id = current_user.tenant_id
    data = request.get_json()
    conn = get_db()

    id_empaque = data.get("id_empaque")
    # 💡 FIX DEFINITIVO: El log de diagnóstico reveló que el frontend envía la cantidad
    # en el campo 'cantidad_empaque'. Se añade a la lógica para capturar el valor correctamente.
    cantidad = data.get("cantidad_empaque") or data.get("cantidad") or data.get("cantidad_necesaria") or 1

    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            if not id_empaque:
                return jsonify({"error": "id_empaque es obligatorio"}), 400

            # 💡 SAAS-IFICATION: Obtenemos el precio del empaque del tenant correcto.
            cursor.execute("SELECT precio FROM empaques WHERE id_empaque=%s AND tenant_id = %s", (id_empaque, current_user.tenant_id))
            row = cursor.fetchone()
            
            if not row:
                return jsonify({"error": "Empaque no encontrado"}), 404

            precio_empaque = float(row["precio"] or 0)
            subtotal = precio_empaque * int(cantidad)
            
            # 💡 SAAS-IFICATION: Insertamos el tenant_id.
            cursor.execute("""
                INSERT INTO recetas_empaques (id_producto, id_empaque, cantidad, subtotal, tenant_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (producto_id, id_empaque, cantidad, subtotal, tenant_id))
            conn.commit()

        # 💡 FIX: Recalculamos el costo del producto para que se actualice en la tabla 'productos'.
        calcular_costo_completo(producto_id, tenant_id)

        return jsonify({"mensaje": "Empaque asignado al producto"}), 201
    except Exception as e:
        conn.rollback()
        logger.error(f"Error en add_empaque_producto: {str(e)}")
        return jsonify({"error": "Error al asignar el empaque"}), 500

@empaques_bp.route("/producto/item/<int:id>", methods=["DELETE"])
@login_required
def delete_empaque_producto(id):
    tenant_id = current_user.tenant_id
    conn = get_db()
    id_producto = None
    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            # 💡 FIX: Obtenemos el id_producto ANTES de borrar para poder recalcular.
            # 💡 SAAS-IFICATION: Aseguramos que solo se pueda borrar un item del tenant correcto.
            cursor.execute("SELECT id_producto FROM recetas_empaques WHERE id = %s AND tenant_id = %s", (id, tenant_id))
            resultado = cursor.fetchone()
            
            if resultado:
                id_producto = resultado['id_producto']
                cursor.execute("DELETE FROM recetas_empaques WHERE id=%s AND tenant_id = %s", (id, tenant_id))
                conn.commit()
            else:
                return jsonify({"mensaje": "Item de empaque no encontrado"}), 404

        # 💡 FIX: Si se borró, recalculamos el costo del producto.
        if id_producto:
            calcular_costo_completo(id_producto, tenant_id)

        return jsonify({"mensaje": "Empaque eliminado del producto"})
    except Exception as e:
        conn.rollback()
        logger.error(f"Error en delete_empaque_producto: {str(e)}")
        return jsonify({"error": "Error al eliminar el empaque del producto"}), 500