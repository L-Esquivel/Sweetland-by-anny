from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from db import get_db # 🟢 Import the new DB manager
from psycopg2.extras import DictCursor # 🟢 To get results as dictionaries
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

detalle_pedidos_bp = Blueprint("detalle_pedidos", __name__, url_prefix="/detalle_pedidos")

# ========================================
# Get ALL order details (admin)
# ========================================
@detalle_pedidos_bp.route("/", methods=["GET"])
@login_required
def get_detalles():
    tenant_id = current_user.tenant_id
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
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
            detalles = cursor.fetchall()

            # Ensure precio_unitario and subtotal are floats
            for d in detalles:
                d["precio_unitario"] = float(d.get("precio_unitario", 0) or 0)
                d["subtotal"] = float(d.get("subtotal", 0) or 0)

            return jsonify(detalles)
    except Exception as e:
        logger.error(f"Error en get_detalles: {e}", exc_info=True)
        return jsonify({"error": "Error fetching order details"}), 500


# ========================================
# Get detail by ID
# ========================================
@detalle_pedidos_bp.route("/<int:id>", methods=["GET"])
@login_required
def get_detalle(id):
    tenant_id = current_user.tenant_id
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
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
            detalle = cursor.fetchone()

            if not detalle:
                return jsonify({"error": "Detail not found"}), 404

            detalle["precio_unitario"] = float(detalle.get("precio_unitario", 0) or 0)
            detalle["subtotal"] = float(detalle.get("subtotal", 0) or 0)

            return jsonify(detalle)
    except Exception as e:
        logger.error(f"Error en get_detalle: {e}", exc_info=True)
        return jsonify({"error": "Error fetching order detail"}), 500


# ========================================
# NEW: Get details by ORDER_ID
# ========================================
@detalle_pedidos_bp.route("/pedido/<int:pedido_id>", methods=["GET"])
@login_required
def get_detalles_por_pedido(pedido_id):
    """
    Gets all details for a specific order.
    Includes product info for frontend display.
    """
    tenant_id = current_user.tenant_id
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
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
            detalles = cursor.fetchall()

            # Ensure numeric types
            for d in detalles:
                d["cantidad"] = int(d.get("cantidad", 0) or 0)
                d["precio_unitario"] = float(d.get("precio_unitario", 0) or 0)
                d["subtotal"] = float(d.get("subtotal", 0) or 0)

            return jsonify(detalles)
    except Exception as e:
        logger.error(f"Error en get_detalles_por_pedido: {e}", exc_info=True)
        return jsonify({"error": "Error fetching order details"}), 500


# ========================================
# Create new order detail
# ========================================
@detalle_pedidos_bp.route("/", methods=["POST"])
@login_required
def create_detalle():
    tenant_id = current_user.tenant_id
    conn = get_db()
    try:
        data = request.get_json()

        pedido_id = data.get("pedido_id")
        producto_id = data.get("producto_id")
        cantidad = data.get("cantidad")
        precio_unitario = data.get("precio_unitario")
        subtotal = data.get("subtotal")

        # Validate required fields
        if not all([pedido_id, producto_id, cantidad, precio_unitario, subtotal]):
            return jsonify({"error": "All fields are required"}), 400

        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO detalle_pedidos (pedido_id, producto_id, cantidad, precio_unitario, subtotal, tenant_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id_detalle
            """, (pedido_id, producto_id, cantidad, precio_unitario, subtotal, tenant_id))
            detalle_id = cursor.fetchone()[0]
            conn.commit()

            return jsonify({
                "message": "Order detail created successfully",
                "id_detalle": detalle_id
            }), 201
    except Exception as e:
        conn.rollback()
        logger.error(f"Error en create_detalle: {e}", exc_info=True)
        return jsonify({"error": "Error creating order detail"}), 500


# ========================================
# Update a detail
# ========================================
@detalle_pedidos_bp.route("/<int:id>", methods=["PUT"])
@login_required
def update_detalle(id):
    tenant_id = current_user.tenant_id
    data = request.get_json()
    cantidad = data.get("cantidad")
    precio_unitario = data.get("precio_unitario")
    subtotal = data.get("subtotal")

    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE detalle_pedidos 
                SET cantidad=%s, precio_unitario=%s, subtotal=%s 
                WHERE id_detalle=%s AND tenant_id = %s
            """, (cantidad, precio_unitario, subtotal, id, tenant_id))
            conn.commit()
            return jsonify({"message": "Detail updated successfully"})
    except Exception as e:
        conn.rollback()
        logger.error(f"Error en update_detalle: {e}", exc_info=True)
        return jsonify({"error": "Error updating detail"}), 500


# ========================================
# Delete order detail
# ========================================
@detalle_pedidos_bp.route("/<int:id>", methods=["DELETE"])
@login_required
def delete_detalle(id):
    tenant_id = current_user.tenant_id
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM detalle_pedidos WHERE id_detalle = %s AND tenant_id = %s", (id, tenant_id))
            conn.commit()
            if cursor.rowcount == 0:
                return jsonify({"error": "Order detail not found or does not belong to your organization"}), 404
            return jsonify({"message": "Order detail deleted successfully"})
    except Exception as e:
        conn.rollback()
        logger.error(f"Error in delete_detalle: {e}", exc_info=True)
        return jsonify({"error": "Error deleting order detail"}), 500