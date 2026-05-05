from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user, login_user, logout_user
from db import get_db_connection
from utils import admin_required
from werkzeug.security import generate_password_hash
import secrets, string, logging

logger = logging.getLogger(__name__)

pedidos_bp = Blueprint("pedidos", __name__, url_prefix="/pedidos")

# ==================== LÓGICA DE STOCK ====================

def procesar_descuento_stock(pedido_id):
    """Resta unidades del inventario basándose en el detalle del pedido."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT producto_id, cantidad FROM detalle_pedidos WHERE pedido_id = %s", (pedido_id,))
        items = cursor.fetchall()
        for item in items:
            cursor.execute("""
                UPDATE productos SET stock = stock - %s 
                WHERE id_producto = %s AND controla_stock = TRUE
            """, (item['cantidad'], item['producto_id']))
        conn.commit()
    except Exception as e:
        logger.error(f"Error descontando stock: {e}")
    finally:
        cursor.close()
        conn.close()

# ==================== STATS (Dashboard Avanzado) ====================

@pedidos_bp.route("/stats", methods=["GET"])
@login_required
@admin_required
def get_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 1. Resumen financiero (Gasto vs Ingreso)
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN DATE(fecha_pedido) = CURDATE() THEN total ELSE 0 END) as hoy,
                SUM(CASE WHEN MONTH(fecha_pedido) = MONTH(CURDATE()) AND YEAR(fecha_pedido) = YEAR(CURDATE()) THEN total ELSE 0 END) as mes,
                SUM(total) as total_historico,
                COUNT(id_pedido) as num_pedidos
            FROM pedidos WHERE estado != 'cancelado'
        """)
        resumen_raw = cursor.fetchone()
        resumen = {k: float(v or 0) for k, v in dict(resumen_raw).items()}

        # 2. Datos para la gráfica (Últimos 7 días con ventas)
        cursor.execute("""
            SELECT DATE(fecha_pedido) as fecha, SUM(total) as venta 
            FROM pedidos WHERE estado != 'cancelado' 
            GROUP BY DATE(fecha_pedido) ORDER BY fecha DESC LIMIT 7
        """)
        grafica_raw = cursor.fetchall()
        # Invertimos para que el frontend reciba del pasado al presente
        grafica = [{"fecha": str(row['fecha']), "venta": float(row['venta'])} for row in grafica_raw]

        # 3. Pedidos por estado (Dashboard progress bars)
        cursor.execute("""
            SELECT estado, COUNT(id_pedido) as cantidad 
            FROM pedidos 
            GROUP BY estado
        """)
        estados_raw = cursor.fetchall()
        pedidos_por_estado = {row['estado']: row['cantidad'] for row in estados_raw}

        # 4. Producto Top (El más vendido en cantidad)
        cursor.execute("""
            SELECT p.nombre, p.precio, SUM(dp.cantidad) as total_vendido
            FROM detalle_pedidos dp
            JOIN productos p ON dp.producto_id = p.id_producto
            JOIN pedidos ped ON dp.pedido_id = ped.id_pedido
            WHERE ped.estado = 'completado'
            GROUP BY p.id_producto
            ORDER BY total_vendido DESC
            LIMIT 1
        """)
        producto_top_raw = cursor.fetchone()
        producto_top = None
        if producto_top_raw:
            producto_top = {
                "nombre": producto_top_raw['nombre'],
                "precio": float(producto_top_raw['precio']),
                "total_vendido": int(producto_top_raw['total_vendido'])
            }

        return jsonify({
            "resumen": resumen, 
            "grafica": grafica,
            "pedidos_por_estado": pedidos_por_estado,
            "producto_top": producto_top
        })
        
    except Exception as e:
        logger.error(f"Error en get_stats: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# ==================== GESTIÓN DE PEDIDOS (Admin) ====================

@pedidos_bp.route("/", methods=["GET"])
@login_required
def get_pedidos():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT p.*, u.nombre as cliente_nombre, u.telefono as cliente_telefono 
            FROM pedidos p 
            LEFT JOIN usuarios u ON p.usuario_id = u.id_usuario 
            ORDER BY p.fecha_pedido DESC
        """)
        rows = cursor.fetchall()
        pedidos = []
        for row in rows:
            p = dict(row)
            p['total'] = float(p.get('total') or 0)
            if p.get('fecha_pedido'):
                p['fecha_pedido'] = p['fecha_pedido'].strftime('%Y-%m-%d %H:%M')
            pedidos.append(p)
        return jsonify(pedidos)
    finally:
        cursor.close()
        conn.close()

@pedidos_bp.route("/<int:id>/estado", methods=["PUT"])
@login_required
def update_estado_pedido(id):
    data = request.get_json()
    nuevo_estado = data.get("estado")
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT estado FROM pedidos WHERE id_pedido = %s", (id,))
        actual = cursor.fetchone()
        if not actual: return jsonify({"error": "No existe"}), 404

        # DISPARADOR DE STOCK
        if nuevo_estado == 'completado' and actual.get('estado') != 'completado':
            procesar_descuento_stock(id)

        cursor.execute("UPDATE pedidos SET estado=%s WHERE id_pedido=%s", (nuevo_estado, id))
        conn.commit()
        return jsonify({"mensaje": "Estado actualizado", "estado": nuevo_estado})
    finally:
        cursor.close()
        conn.close()

# ==================== ENDPOINTS PÚBLICOS (Landing Page) ====================

@pedidos_bp.route("/public", methods=["POST"])
def create_pedido_public():
    """Crea un pedido atómico (cabecera + detalles) desde el carrito del cliente."""
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO pedidos (usuario_id, telefono, direccion, total, estado, fecha_pedido)
            VALUES (%s, %s, %s, %s, 'pendiente', NOW())
        """, (data.get("usuario_id"), data.get("telefono"), data.get("direccion"), data.get("total", 0)))
        pedido_id = cursor.lastrowid
        
        for item in data.get("items", []):
            cursor.execute("""
                INSERT INTO detalle_pedidos (pedido_id, producto_id, cantidad, precio_unitario, subtotal)
                VALUES (%s, %s, %s, %s, %s)
            """, (pedido_id, item.get("id_producto"), item.get("cantidad"), item.get("precio"), item.get("subtotal")))
        
        conn.commit()
        return jsonify({"mensaje": "Pedido recibido", "id_pedido": pedido_id}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@pedidos_bp.route("/public/mis-pedidos", methods=["GET"])
@login_required
def mis_pedidos():
    """Devuelve el historial de pedidos para el cliente logueado."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM pedidos WHERE usuario_id = %s ORDER BY fecha_pedido DESC", (current_user.id,))
        pedidos = [dict(p) for p in cursor.fetchall()]
        
        for p in pedidos:
            p['total'] = float(p['total'] or 0)
            p['fecha_pedido'] = p['fecha_pedido'].strftime('%Y-%m-%d %H:%M') if p['fecha_pedido'] else ""
            cursor.execute("""
                SELECT dp.*, pr.nombre FROM detalle_pedidos dp 
                JOIN productos pr ON dp.producto_id = pr.id_producto 
                WHERE dp.pedido_id = %s
            """, (p['id_pedido'],))
            detalles = cursor.fetchall()
            p['detalles'] = [{"nombre": d['nombre'], "cantidad": d['cantidad'], "subtotal": float(d['subtotal'])} for d in detalles]
            
        return jsonify({"pedidos": pedidos})
    finally:
        cursor.close()
        conn.close()

@pedidos_bp.route("/<int:id>/detalles", methods=["GET"])
@login_required
def get_detalles_admin(id):
    """Obtiene los detalles de un pedido para el modal del Panel Admin."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT dp.*, p.nombre as producto_nombre 
            FROM detalle_pedidos dp
            JOIN productos p ON dp.producto_id = p.id_producto
            WHERE dp.pedido_id = %s
        """, (id,))
        detalles = [dict(d) for d in cursor.fetchall()]
        for d in detalles:
            d['subtotal'] = float(d['subtotal'] or 0)
            d['precio_unitario'] = float(d.get('precio_unitario') or 0)
        return jsonify(detalles)
    finally:
        cursor.close()
        conn.close()

# (Registro, Login y Logout de clientes se mantienen iguales según tu archivo previo)