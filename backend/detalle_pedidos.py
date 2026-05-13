from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from extensions import mysql
from flask_cors import cross_origin
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

detalle_pedidos_bp = Blueprint("detalle_pedidos", __name__, url_prefix="/detalle_pedidos")

# ========================================
# Obtener TODOS los detalles (admin)
# ========================================
@detalle_pedidos_bp.route("/", methods=["GET"])
@login_required
@cross_origin()
def get_detalles():
    tenant_id = current_user.tenant_id
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("""
            SELECT 
                dp.id_detalle, 
                dp.pedido_id, 
                p.nombre AS producto, 
                dp.cantidad, 
                dp.precio_unitario,
                dp.subtotal
            FROM detalle_pedidos dp
            LEFT JOIN productos p ON dp.producto_id = p.id_producto AND p.tenant_id = %s
            WHERE dp.tenant_id = %s
            ORDER BY dp.id_detalle DESC
        """, (tenant_id, tenant_id))
        filas = cursor.fetchall()
        detalles = [dict(fila) for fila in filas] if filas else []

        # Asegurar que precio_unitario y subtotal sean float
        for d in detalles:
            d["precio_unitario"] = float(d.get("precio_unitario", 0) or 0)
            d["subtotal"] = float(d.get("subtotal", 0) or 0)

        return jsonify(detalles)
    except Exception as e:
        logger.error(f"Error en get_detalles: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


# ========================================
# Obtener detalle por ID
# ========================================
@detalle_pedidos_bp.route("/<int:id>", methods=["GET"])
@login_required
@cross_origin()
def get_detalle(id):
    tenant_id = current_user.tenant_id
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("""
            SELECT 
                dp.id_detalle, 
                dp.pedido_id, 
                p.nombre AS producto, 
                dp.cantidad, 
                dp.precio_unitario,
                dp.subtotal
            FROM detalle_pedidos dp
            LEFT JOIN productos p ON dp.producto_id = p.id_producto AND p.tenant_id = %s
            WHERE dp.id_detalle = %s AND dp.tenant_id = %s
        """, (tenant_id, id, tenant_id))
        fila = cursor.fetchone()

        if not fila:
            return jsonify({"error": "Detalle no encontrado"}), 404

        detalle = dict(fila)
        detalle["precio_unitario"] = float(detalle.get("precio_unitario", 0) or 0)
        detalle["subtotal"] = float(detalle.get("subtotal", 0) or 0)

        return jsonify(detalle)
    except Exception as e:
        logger.error(f"Error en get_detalle: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


# ========================================
# NUEVO: Obtener detalles por PEDIDO_ID
# ========================================
@detalle_pedidos_bp.route("/pedido/<int:pedido_id>", methods=["GET"])
@login_required
@cross_origin()
def get_detalles_por_pedido(pedido_id):
    """
    Obtiene todos los detalles de un pedido específico.
    Incluye info del producto para mostrar en el frontend.
    """
    tenant_id = current_user.tenant_id
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("""
            SELECT 
                dp.id_detalle AS id,
                dp.pedido_id,
                dp.producto_id,
                p.nombre AS producto_nombre,
                p.categoria,
                dp.cantidad,
                dp.precio_unitario,
                dp.subtotal
            FROM detalle_pedidos dp
            LEFT JOIN productos p ON dp.producto_id = p.id_producto AND p.tenant_id = %s
            WHERE dp.pedido_id = %s AND dp.tenant_id = %s
            ORDER BY dp.id_detalle ASC
        """, (tenant_id, pedido_id, tenant_id))
        filas = cursor.fetchall()
        detalles = [dict(fila) for fila in filas] if filas else []

        # Asegurar tipos numéricos
        for d in detalles:
            d["cantidad"] = int(d.get("cantidad", 0) or 0)
            d["precio_unitario"] = float(d.get("precio_unitario", 0) or 0)
            d["subtotal"] = float(d.get("subtotal", 0) or 0)

        return jsonify(detalles)
    except Exception as e:
        logger.error(f"Error en get_detalles_por_pedido: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


# ========================================
# Crear nuevo detalle de pedido
# ========================================
@detalle_pedidos_bp.route("/", methods=["POST"])
@login_required
@cross_origin()
def create_detalle():
    tenant_id = current_user.tenant_id
    try:
        data = request.get_json()

        pedido_id = data.get("pedido_id")
        producto_id = data.get("producto_id")
        cantidad = data.get("cantidad")
        precio_unitario = data.get("precio_unitario")
        subtotal = data.get("subtotal")

        # Validar campos requeridos
        if not all([pedido_id, producto_id, cantidad, precio_unitario, subtotal]):
            return jsonify({"error": "Todos los campos son requeridos"}), 400

        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO detalle_pedidos (pedido_id, producto_id, cantidad, precio_unitario, subtotal, tenant_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (pedido_id, producto_id, cantidad, precio_unitario, subtotal, tenant_id))

        detalle_id = cursor.lastrowid
        mysql.connection.commit()
        cursor.close()

        return jsonify({
            "mensaje": "Detalle de pedido creado correctamente",
            "id_detalle": detalle_id
        }), 201

    except Exception as e:
        logger.error(f"Error en create_detalle: {str(e)}")
        return jsonify({"error": f"Error del servidor: {str(e)}"}), 500


# ========================================
# Actualizar un detalle
# ========================================
@detalle_pedidos_bp.route("/<int:id>", methods=["PUT"])
@login_required
@cross_origin()
def update_detalle(id):
    tenant_id = current_user.tenant_id
    data = request.get_json()
    cantidad = data.get("cantidad")
    precio_unitario = data.get("precio_unitario")
    subtotal = data.get("subtotal")

    cursor = mysql.connection.cursor()
    try:
        cursor.execute("""
            UPDATE detalle_pedidos 
            SET cantidad=%s, precio_unitario=%s, subtotal=%s 
            WHERE id_detalle=%s AND tenant_id = %s
        """, (cantidad, precio_unitario, subtotal, id, tenant_id))
        mysql.connection.commit()
        return jsonify({"mensaje": "Detalle actualizado correctamente"})
    except Exception as e:
        logger.error(f"Error en update_detalle: {str(e)}")
        mysql.connection.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


# ========================================
# Eliminar detalle de pedido
# ========================================
@detalle_pedidos_bp.route("/<int:id>", methods=["DELETE"])
@login_required
@cross_origin()
def delete_detalle(id):
    tenant_id = current_user.tenant_id
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("DELETE FROM detalle_pedidos WHERE id_detalle = %s AND tenant_id = %s", (id, tenant_id))
        mysql.connection.commit()
        return jsonify({"mensaje": "Detalle eliminado correctamente"})
    except Exception as e:
        logger.error(f"Error en delete_detalle: {str(e)}")
        mysql.connection.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()