from flask import Blueprint, jsonify, request
from flask_login import login_required
from extensions import mysql
import logging
from recetas import calcular_costo_completo # Importamos la función de costeo

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

empaques_bp = Blueprint("empaques", __name__, url_prefix="/empaques")

# ==================== CATÁLOGO GENERAL DE EMPAQUES ====================
# Estos son los que aparecerán en la nueva sección de "Insumos"

@empaques_bp.route("/", methods=["GET"])
@login_required
def get_empaques():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id_empaque, nombre, descripcion, precio FROM empaques ORDER BY nombre")
        filas = cursor.fetchall()
        cursor.close()
        return jsonify([dict(f) for f in filas])
    except Exception as e:
        logger.error(f"Error en get_empaques: {str(e)}")
        return jsonify({"error": str(e)}), 500

@empaques_bp.route("/", methods=["POST"])
@login_required
def add_empaque():
    try:
        data = request.get_json()
        nombre = data.get("nombre")
        descripcion = data.get("descripcion", "")
        # Forzamos conversión a float
        precio = float(data.get("precio") or 0)

        if not nombre:
            return jsonify({"error": "El nombre es obligatorio"}), 400

        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO empaques (nombre, descripcion, precio) VALUES (%s, %s, %s)",
            (nombre, descripcion, precio)
        )
        mysql.connection.commit()
        cursor.close()
        return jsonify({"mensaje": "Empaque creado en el catálogo"}), 201
    except Exception as e:
        logger.error(f"Error en add_empaque: {str(e)}")
        return jsonify({"error": str(e)}), 500

@empaques_bp.route("/<int:id>", methods=["PUT"])
@login_required
def update_empaque(id):
    try:
        data = request.get_json()
        nombre = data.get("nombre")
        descripcion = data.get("descripcion", "")
        precio = float(data.get("precio") or 0)

        if not nombre:
            return jsonify({"error": "El nombre es obligatorio"}), 400

        cursor = mysql.connection.cursor()
        cursor.execute(
            "UPDATE empaques SET nombre=%s, descripcion=%s, precio=%s WHERE id_empaque=%s",
            (nombre, descripcion, precio, id)
        )
        mysql.connection.commit()
        cursor.close()
        return jsonify({"mensaje": "Empaque actualizado correctamente"})
    except Exception as e:
        logger.error(f"Error en update_empaque: {str(e)}")
        return jsonify({"error": str(e)}), 500

@empaques_bp.route("/<int:id>", methods=["DELETE"])
@login_required
def delete_empaque(id):
    try:
        cursor = mysql.connection.cursor()
        
        # VERIFICACIÓN: ¿Está este empaque en uso por algún producto?
        cursor.execute("SELECT COUNT(*) as total FROM recetas_empaques WHERE id_empaque = %s", (id,))
        uso = cursor.fetchone()
        
        if uso and uso.get('total', 0) > 0:
            cursor.close()
            return jsonify({"error": "No se puede eliminar: el empaque está asignado a productos en la sección de Recetas"}), 400

        cursor.execute("DELETE FROM empaques WHERE id_empaque=%s", (id,))
        mysql.connection.commit()
        cursor.close()
        return jsonify({"mensaje": "Empaque eliminado del catálogo"})
    except Exception as e:
        logger.error(f"Error en delete_empaque: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ==================== EMPAQUES ASIGNADOS A PRODUCTOS ====================
# Estos se usan específicamente dentro de la sección de recetas de cada producto

@empaques_bp.route("/producto/<int:producto_id>", methods=["GET"])
@login_required
def get_empaques_producto(producto_id):
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT re.id, re.id_empaque, re.cantidad, re.subtotal,
               e.nombre, e.precio
        FROM recetas_empaques re
        LEFT JOIN empaques e ON re.id_empaque = e.id_empaque
        WHERE re.id_producto = %s
    """, (producto_id,))
    filas = cursor.fetchall()
    cursor.close()

    items = []
    costo_total = 0
    for f in filas:
        precio_unitario = float(f.get("precio") or 0)
        cantidad = int(f.get("cantidad") or 1)
        subtotal = float(f.get("subtotal") or (precio_unitario * cantidad))
        
        costo_total += subtotal
        items.append({
            "id":         f.get("id"),
            "id_empaque": f.get("id_empaque"),
            "cantidad":   cantidad,
            "subtotal":   subtotal,
            "nombre":     f.get("nombre"),
            "precio":     precio_unitario
        })

    return jsonify({"empaques": items, "costo_total_empaque": costo_total})

@empaques_bp.route("/producto/<int:producto_id>", methods=["POST"])
@login_required
def add_empaque_producto(producto_id):
    data = request.get_json()
    id_empaque = data.get("id_empaque")
    # 💡 FIX 2: Hacemos el backend más robusto para aceptar varios nombres comunes para la cantidad
    # ('cantidad', 'cantidad_necesaria') y así resolver la inconsistencia con el formulario,
    # que parece no enviar los campos esperados.
    cantidad = data.get("cantidad") or data.get("cantidad_necesaria") or 1

    if not id_empaque:
        return jsonify({"error": "id_empaque es obligatorio"}), 400

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT precio FROM empaques WHERE id_empaque=%s", (id_empaque,))
    row = cursor.fetchone()
    
    if not row:
        cursor.close()
        return jsonify({"error": "Empaque no encontrado"}), 404

    precio_empaque = float(row.get("precio") or 0)
    subtotal = precio_empaque * int(cantidad)
    
    cursor.execute("""
        INSERT INTO recetas_empaques (id_producto, id_empaque, cantidad, subtotal)
        VALUES (%s, %s, %s, %s)
    """, (producto_id, id_empaque, cantidad, subtotal))
    mysql.connection.commit()

    # 💡 FIX: Recalculamos el costo del producto para que se actualice en la tabla 'productos'.
    calcular_costo_completo(producto_id)

    cursor.close()
    return jsonify({"mensaje": "Empaque asignado al producto"}), 201

@empaques_bp.route("/producto/item/<int:id>", methods=["DELETE"])
@login_required
def delete_empaque_producto(id):
    cursor = mysql.connection.cursor()
    try:
        # 💡 FIX: Obtenemos el id_producto ANTES de borrar para poder recalcular.
        cursor.execute("SELECT id_producto FROM recetas_empaques WHERE id = %s", (id,))
        resultado = cursor.fetchone()
        id_producto = resultado.get('id_producto') if resultado else None

        cursor.execute("DELETE FROM recetas_empaques WHERE id=%s", (id,))
        mysql.connection.commit()

        # 💡 FIX: Si se borró, recalculamos el costo del producto.
        if id_producto:
            calcular_costo_completo(id_producto)

        return jsonify({"mensaje": "Empaque eliminado del producto"})
    finally:
        cursor.close()