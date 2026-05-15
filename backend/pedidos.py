from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from utils import admin_required, registrar_log # 🛡️ Import the audit log utility
from db import get_db # 🟢 Import the new DB manager
from psycopg2.extras import DictCursor # 🟢 To get results as dictionaries
import logging, datetime

logger = logging.getLogger(__name__)

pedidos_bp = Blueprint("pedidos", __name__, url_prefix="/pedidos")

# ==================== LÓGICA DE STOCK ====================
# ==================== STOCK LOGIC ====================

def process_stock_deduction(cursor, order_id, tenant_id):
    """Deducts units from inventory based on the order details."""
    try:
        # This function is called from another that already handles commit/rollback,
        # so we don't commit here to maintain atomicity.
        cursor.execute("SELECT producto_id, cantidad FROM detalle_pedidos WHERE pedido_id = %s AND tenant_id = %s", (pedido_id, tenant_id))
        items = cursor.fetchall()
        for item in items:
            cursor.execute("""
                UPDATE productos SET stock = stock - %s 
                WHERE id_producto = %s AND controla_stock = TRUE AND tenant_id = %s
            """, (item['cantidad'], item['producto_id'], tenant_id))
    except Exception as e:
        logger.error(f"Error deducting stock: {e}")
        # Propagate the exception so the calling function can perform a rollback.
        raise

# ==================== STATS (Dashboard) ====================

@pedidos_bp.route("/stats", methods=["GET"])
@admin_required
def get_dashboard_stats():
    tenant_id = current_user.tenant_id
    conn = get_db()
    cursor = conn.cursor(cursor_factory=DictCursor)
    try:
        # 1. Obtener y validar rango de fechas (default: últimos 30 días)
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=29)

        start_date_str = request.args.get('fecha_inicio', start_date.strftime('%Y-%m-%d'))
        end_date_str = request.args.get('fecha_fin', end_date.strftime('%Y-%m-%d'))
        params_with_tenant = (tenant_id, start_date_str, end_date_str)

        # 2. Financial summary for the date range
        # 💡 SAAS-IFICATION: All queries now filter by tenant_id.
        where_pedidos = " WHERE tenant_id = %s AND estado != 'cancelado' AND DATE(fecha_pedido) BETWEEN %s AND %s "
        cursor.execute(f"""
            SELECT 
                SUM(total) as total_sales_range,
                COUNT(id_pedido) as num_orders_range
            FROM pedidos {where_pedidos}
        """, params_with_tenant)
        summary_range_raw = cursor.fetchone()
        summary = {
            'total_sales_range': float(summary_range_raw.get('total_sales_range') or 0),
            'num_orders_range': int(summary_range_raw.get('num_orders_range') or 0)
        }
        
        # 3. Sum expenses in the same date range
        cursor.execute("""
            SELECT SUM(monto) as total_expenses_range
            FROM gastos WHERE tenant_id = %s AND fecha BETWEEN %s AND %s
        """, params_with_tenant)
        expenses_range_raw = cursor.fetchone()
        summary['total_expenses_range'] = float(expenses_range_raw.get('total_expenses_range') or 0)

        # 4. Sum waste in the same date range
        cursor.execute("""
            SELECT SUM(costo_perdida) as total_waste_range
            FROM merma WHERE tenant_id = %s AND fecha BETWEEN %s AND %s
        """, params_with_tenant)
        waste_range_raw = cursor.fetchone()
        summary['total_waste_range'] = float(waste_range_raw.get('total_waste_range') or 0)

        # 5. Data for the chart for the date range (IMPROVED VERSION)
        # 💡 FIX: A complete date series is generated for the range and sales are joined.
        # This ensures there is a data point (even if it's 0) for each day,
        # making the chart continuous and easier to render on the frontend.
        cursor.execute("""
            WITH date_series AS (
                SELECT generate_series(%s::date, %s::date, '1 day'::interval)::date as fecha
            )
            SELECT 
                d.fecha,
                COALESCE(SUM(p.total), 0) as venta
            FROM date_series d
            LEFT JOIN pedidos p ON DATE(p.fecha_pedido) = d.fecha AND p.tenant_id = %s AND p.estado != 'cancelado'
            GROUP BY d.fecha
            ORDER BY d.fecha ASC
        """, (start_date_str, end_date_str, tenant_id))
        chart_data_raw = cursor.fetchall()
        sales_chart_data = [{"fecha": str(row['fecha']), "venta": float(row['venta'])} for row in chart_data_raw]

        # 6. Orders by status for the date range
        cursor.execute(f"SELECT estado, COUNT(id_pedido) as cantidad FROM pedidos {where_pedidos} GROUP BY estado", params_with_tenant)
        status_raw = cursor.fetchall()
        orders_by_status = {row['estado']: row['cantidad'] for row in status_raw}

        # 7. Top product for the date range
        where_pedidos_aliased = " WHERE ped.tenant_id = %s AND ped.estado = 'completado' AND DATE(ped.fecha_pedido) BETWEEN %s AND %s "
        cursor.execute(f"""
            SELECT p.nombre, p.precio, SUM(dp.cantidad) as total_vendido
            FROM detalle_pedidos dp
            JOIN productos p ON dp.producto_id = p.id_producto
            JOIN pedidos ped ON dp.pedido_id = ped.id_pedido
            {where_pedidos_aliased}
            GROUP BY p.id_producto
            ORDER BY total_vendido DESC LIMIT 1
        """, params_with_tenant)
        top_product_raw = cursor.fetchone()
        top_product = None
        if top_product_raw:
            top_product = {
                "nombre": top_product_raw['nombre'],
                "precio": float(top_product_raw['precio']),
                "total_vendido": int(top_product_raw['total_vendido'])
            }

        return jsonify({
            "summary": summary, 
            "sales_chart_data": sales_chart_data, 
            "orders_by_status": orders_by_status, 
            "top_product": top_product,
            "applied_filters": {"start_date": start_date_str, "end_date": end_date_str}
        })
    except Exception as e:
        current_app.logger.error(f"Error in get_dashboard_stats: {e}")
        return jsonify({"error": "Error fetching statistics"}), 500

# ==================== ADMIN MANAGEMENT ====================

@pedidos_bp.route("/", methods=["GET"])
@login_required
def get_orders():
    tenant_id = current_user.tenant_id
    conn = get_db()
    cursor = conn.cursor(cursor_factory=DictCursor)
    try:
        cursor.execute("""
            SELECT p.*, u.nombre as customer_name, u.telefono as customer_phone 
            FROM pedidos p LEFT JOIN usuarios u ON p.usuario_id = u.id_usuario 
            WHERE p.tenant_id = %s
            ORDER BY p.fecha_pedido DESC
        """, (tenant_id,))
        orders = [dict(row) for row in cursor.fetchall()]
        # Format data for the frontend
        for p in orders:
            p['id_pedido'] = p.get('id_pedido') 
            p['total'] = float(p.get('total') or 0)
            if p.get('fecha_pedido'): 
                p['fecha_pedido'] = p['fecha_pedido'].strftime('%Y-%m-%d %H:%M')
        return jsonify(orders)
    except Exception as e:
        current_app.logger.error(f"Error in get_orders: {e}")
        return jsonify({"error": "Error fetching orders"}), 500

@pedidos_bp.route("/", methods=["POST"])
@admin_required
def create_order_admin():
    """
    Allows an administrator to create a new order manually.
    Calculates the total on the backend for security.
    """
    data = request.get_json()
    tenant_id = current_user.tenant_id
    conn = get_db()

    items = data.get("items", [])
    if not items:
        return jsonify({"error": "The order must contain at least one product"}), 400

    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            # 1. Calculate the order total from the backend to prevent price manipulation.
            order_total = 0
            products_to_insert = []
            for item in items:
                producto_id = item.get("producto_id")
                cantidad = item.get("cantidad")
                if not producto_id or not cantidad or int(cantidad) <= 0:
                    continue # Ignore invalid items

                cursor.execute("SELECT precio FROM productos WHERE id_producto = %s AND tenant_id = %s", (producto_id, tenant_id))
                producto_data = cursor.fetchone()
                if not producto_data:
                    raise ValueError(f"One of the selected products (ID: {producto_id}) was not found.")
                
                precio_unitario = float(producto_data['precio'] or 0)
                subtotal = precio_unitario * int(cantidad)
                order_total += subtotal
                products_to_insert.append({
                    "producto_id": producto_id,
                    "cantidad": cantidad,
                    "precio_unitario": precio_unitario,
                    "subtotal": subtotal
                })
            
            if not products_to_insert:
                return jsonify({"error": "No valid products were provided in the order"}), 400

            # 2. Insert the main order.
            # FIX: 'customer_name' is removed from the INSERT. The customer's name is obtained via a JOIN with the 'usuarios' table using 'usuario_id'.
            cursor.execute("""
                INSERT INTO pedidos (usuario_id, telefono, direccion, total, estado, tenant_id)
                VALUES (%s, %s, %s, %s, 'pendiente', %s)
                RETURNING id_pedido
            """, (
                data.get("usuario_id"), 
                data.get("telefono"), 
                data.get("direccion"), 
                order_total, 
                tenant_id
            ))
            pedido_id = cursor.fetchone()[0]

            # 3. Insert the order details.
            for prod in products_to_insert:
                cursor.execute("INSERT INTO detalle_pedidos (pedido_id, producto_id, cantidad, precio_unitario, subtotal, tenant_id) VALUES (%s, %s, %s, %s, %s, %s)",
                               (pedido_id, prod['producto_id'], prod['cantidad'], prod['precio_unitario'], prod['subtotal'], tenant_id))
            
            conn.commit()
            registrar_log(f"Admin created new order ID {pedido_id}")
            return jsonify({"message": "Order created successfully", "id_pedido": pedido_id}), 201

    except ValueError as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error in create_order_admin: {e}", exc_info=True)
        return jsonify({"error": "Internal error creating order"}), 500

@pedidos_bp.route("/<int:id>/estado", methods=["PUT"])
@admin_required # FIX: Security decorator added. Only admins can change the status.
def update_order_status(id):
    data = request.get_json()
    new_status = data.get("estado")
    tenant_id = current_user.tenant_id
    conn = get_db()
    cursor = conn.cursor(cursor_factory=DictCursor)
    try:
        cursor.execute("SELECT estado FROM pedidos WHERE id_pedido = %s AND tenant_id = %s", (id, tenant_id))
        current_status_row = cursor.fetchone()
        if not current_status_row: return jsonify({"error": "Order not found"}), 404

        if new_status == 'completado' and current_status_row.get('estado') != 'completado':
            process_stock_deduction(cursor, id, tenant_id)

        cursor.execute("UPDATE pedidos SET estado=%s WHERE id_pedido=%s AND tenant_id = %s", (new_status, id, tenant_id))
        conn.commit()

        # 🛡️ LOG: Order status tracking
        registrar_log(f"Updated order #{id} status from '{current_status_row.get('estado')}' to '{new_status}'")

        return jsonify({"message": "Updated", "status": new_status})
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error in update_order_status: {e}", exc_info=True)
        return jsonify({"error": "Error updating order status"}), 500

@pedidos_bp.route("/<int:id>", methods=["DELETE"])
@admin_required
def delete_order(id):
    tenant_id = current_user.tenant_id
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM detalle_pedidos WHERE pedido_id = %s AND tenant_id = %s", (id, tenant_id))
        cursor.execute("DELETE FROM pedidos WHERE id_pedido = %s AND tenant_id = %s", (id, tenant_id))
        conn.commit()

        # 🛡️ LOG: Order deletion
        registrar_log(f"Permanently deleted order ID {id}")

        return jsonify({"message": "Order deleted successfully"})
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error in delete_order: {e}", exc_info=True)
        return jsonify({"error": "Error deleting order"}), 500

@pedidos_bp.route("/<int:id>/detalles", methods=["GET"])
@login_required
def get_order_details_admin(id):
    tenant_id = current_user.tenant_id
    conn = get_db()
    cursor = conn.cursor(cursor_factory=DictCursor)
    try:
        # This route is now redundant with /detalle_pedidos/pedido/<id>, but we keep it for backward compatibility.
        cursor.execute("""
            SELECT dp.*, p.nombre as producto_nombre 
            FROM detalle_pedidos dp JOIN productos p ON dp.producto_id = p.id_producto
            WHERE dp.pedido_id = %s AND dp.tenant_id = %s
        """, (id, tenant_id))
        details = [dict(d) for d in cursor.fetchall()]
        for d in details:
            d['subtotal'] = float(d['subtotal'] or 0)
            d['precio_unitario'] = float(d.get('precio_unitario') or 0)
        return jsonify(details)
    except Exception as e:
        current_app.logger.error(f"Error in get_order_details_admin: {e}")
        return jsonify({"error": "Error fetching details"}), 500

# ==================== PUBLIC ENDPOINTS 🌍 ====================

@pedidos_bp.route("/public", methods=["POST"])
def create_public_order():
    data = request.get_json()
    # 💡 SAAS-IFICATION: Public orders are associated with the public tenant.
    tenant_id_publico = os.getenv('PUBLIC_TENANT_ID', 1)
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO pedidos (usuario_id, telefono, direccion, total, estado, tenant_id)
            VALUES (%s, %s, %s, %s, 'pendiente', %s)
            RETURNING id_pedido
        """, (data.get("usuario_id"), data.get("telefono"), data.get("direccion"), data.get("total", 0), tenant_id_publico))
        pedido_id = cursor.fetchone()[0]

        for item in data.get("items", []):
            cursor.execute("""
                INSERT INTO detalle_pedidos (pedido_id, producto_id, cantidad, precio_unitario, subtotal, tenant_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (pedido_id, item.get("id_producto"), item.get("cantidad"), item.get("precio"), item.get("subtotal"), tenant_id_publico))
        conn.commit()

        # 🛡️ LOG: New incoming order
        registrar_log(f"Received new web order: ID #{pedido_id}")

        return jsonify({"message": "Order received", "id_pedido": pedido_id}), 201
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error in create_public_order: {e}", exc_info=True)
        return jsonify({"error": "Error processing order"}), 500

@pedidos_bp.route("/public/mis-pedidos", methods=["GET"])
@login_required
def get_my_orders():
    tenant_id = current_user.tenant_id
    conn = get_db()
    cursor = conn.cursor(cursor_factory=DictCursor)
    try:
        # This route was already optimized to avoid N+1, only the connection is changed.
        # 1. Get all user orders (1st query)
        cursor.execute("SELECT * FROM pedidos WHERE usuario_id = %s AND tenant_id = %s ORDER BY fecha_pedido DESC", (current_user.id, tenant_id))
        orders = [dict(p) for p in cursor.fetchall()]

        if not orders:
            return jsonify({"pedidos": []})

        # 2. Get ALL details for THOSE orders in a single query (2nd query)
        pedido_ids = [p['id_pedido'] for p in orders]
        placeholders = ','.join(['%s'] * len(pedido_ids))
        cursor.execute(f"""
            SELECT dp.pedido_id, dp.cantidad, dp.subtotal, pr.nombre 
            FROM detalle_pedidos dp JOIN productos pr ON dp.producto_id = pr.id_producto
            WHERE dp.pedido_id IN ({placeholders}) AND dp.tenant_id = %s
        """, tuple(pedido_ids) + (tenant_id,))
        all_details = cursor.fetchall()

        # 3. Map details to their corresponding orders in Python (very fast)
        details_by_order = {}
        for detalle in all_details:
            pedido_id = detalle['pedido_id']
            if pedido_id not in details_by_order:
                details_by_order[pedido_id] = []
            details_by_order[pedido_id].append({
                "nombre": detalle['nombre'], "cantidad": detalle['cantidad'], "subtotal": float(detalle['subtotal'])
            })

        # 4. Combine the data
        for p in orders:
            p['total'] = float(p['total'] or 0)
            p['fecha_pedido'] = p['fecha_pedido'].strftime('%Y-%m-%d %H:%M') if p['fecha_pedido'] else ""
            p['detalles'] = details_by_order.get(p['id_pedido'], [])
        return jsonify({"pedidos": orders})
    except Exception as e:
        current_app.logger.error(f"Error in get_my_orders: {e}")
        return jsonify({"error": "Error fetching your orders"}), 500