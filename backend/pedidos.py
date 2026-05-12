from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user, login_user, logout_user
from utils import admin_required, registrar_log # 🛡️ Importamos la auditoría
from extensions import mysql
from werkzeug.security import generate_password_hash
import secrets, string, logging

logger = logging.getLogger(__name__)

pedidos_bp = Blueprint("pedidos", __name__, url_prefix="/pedidos")

# ==================== LÓGICA DE STOCK ====================

def procesar_descuento_stock(pedido_id):
    """Resta unidades del inventario basándose en el detalle del pedido."""
    cursor = mysql.connection.cursor()
    try:
        # Esta función es llamada desde otra que ya maneja el commit/rollback,
        # por lo que no hacemos commit aquí para mantener la atomicidad.
        cursor.execute("SELECT producto_id, cantidad FROM detalle_pedidos WHERE pedido_id = %s", (pedido_id,))
        items = cursor.fetchall()
        for item in items:
            cursor.execute("""
                UPDATE productos SET stock = stock - %s 
                WHERE id_producto = %s AND controla_stock = TRUE
            """, (item['cantidad'], item['producto_id']))
    except Exception as e:
        logger.error(f"Error descontando stock: {e}")
        # Propagamos la excepción para que la función llamadora haga rollback.
        raise
    finally:
        if cursor: cursor.close()

# ==================== STATS (Dashboard) ====================

@pedidos_bp.route("/stats", methods=["GET"])
@login_required
@admin_required
def get_stats():
    cursor = mysql.connection.cursor()
    try:
        # 1. Resumen financiero
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

        # 2. Datos para la gráfica
        cursor.execute("""
            SELECT DATE(fecha_pedido) as fecha, SUM(total) as venta 
            FROM pedidos WHERE estado != 'cancelado' 
            GROUP BY DATE(fecha_pedido) ORDER BY fecha DESC LIMIT 7
        """)
        grafica_raw = cursor.fetchall()
        grafica = [{"fecha": str(row['fecha']), "venta": float(row['venta'])} for row in grafica_raw]

        # 3. Pedidos por estado
        cursor.execute("SELECT estado, COUNT(id_pedido) as cantidad FROM pedidos GROUP BY estado")
        estados_raw = cursor.fetchall()
        pedidos_por_estado = {row['estado']: row['cantidad'] for row in estados_raw}

        # 4. Producto Top
        cursor.execute("""
            SELECT p.nombre, p.precio, SUM(dp.cantidad) as total_vendido
            FROM detalle_pedidos dp
            JOIN productos p ON dp.producto_id = p.id_producto
            JOIN pedidos ped ON dp.pedido_id = ped.id_pedido
            WHERE ped.estado = 'completado'
            GROUP BY p.id_producto
            ORDER BY total_vendido DESC LIMIT 1
        """)
        producto_top_raw = cursor.fetchone()
        producto_top = None
        if producto_top_raw:
            producto_top = {
                "nombre": producto_top_raw['nombre'],
                "precio": float(producto_top_raw['precio']),
                "total_vendido": int(producto_top_raw['total_vendido'])
            }

        return jsonify({"resumen": resumen, "grafica": grafica, "pedidos_por_estado": pedidos_por_estado, "producto_top": producto_top})
    finally:
        if cursor: cursor.close()

# ==================== GESTIÓN ADMIN ====================

@pedidos_bp.route("/", methods=["GET"])
@login_required
def get_pedidos():
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("""
            SELECT p.*, u.nombre as cliente_nombre, u.telefono as cliente_telefono 
            FROM pedidos p LEFT JOIN usuarios u ON p.usuario_id = u.id_usuario 
            ORDER BY p.fecha_pedido DESC
        """)
        pedidos = [dict(row) for row in cursor.fetchall()]
        for p in pedidos:
            p['id_pedido'] = p.get('id_pedido') 
            p['total'] = float(p.get('total') or 0)
            if p.get('fecha_pedido'): 
                p['fecha_pedido'] = p['fecha_pedido'].strftime('%Y-%m-%d %H:%M')
        return jsonify(pedidos)
    finally:
        if cursor: cursor.close()

@pedidos_bp.route("/<int:id>/estado", methods=["PUT"])
@login_required
def update_estado_pedido(id):
    data = request.get_json()
    nuevo_estado = data.get("estado")
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("SELECT estado FROM pedidos WHERE id_pedido = %s", (id,))
        actual = cursor.fetchone()
        if not actual: return jsonify({"error": "No existe"}), 404

        if nuevo_estado == 'completado' and actual.get('estado') != 'completado':
            procesar_descuento_stock(id)

        cursor.execute("UPDATE pedidos SET estado=%s WHERE id_pedido=%s", (nuevo_estado, id))
        mysql.connection.commit()

        # 🛡️ LOG: Seguimiento de estado de pedido
        registrar_log(f"Actualizó estado pedido #{id} de '{actual.get('estado')}' a '{nuevo_estado}'")

        return jsonify({"mensaje": "Actualizado", "estado": nuevo_estado})
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor: cursor.close()

@pedidos_bp.route("/<int:id>", methods=["DELETE"])
@login_required
@admin_required
def delete_pedido(id):
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("DELETE FROM detalle_pedidos WHERE pedido_id = %s", (id,))
        cursor.execute("DELETE FROM pedidos WHERE id_pedido = %s", (id,))
        mysql.connection.commit()

        # 🛡️ LOG: Eliminación de pedido
        registrar_log(f"Eliminó permanentemente el pedido ID {id}")

        return jsonify({"mensaje": "Pedido eliminado correctamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor: cursor.close()

@pedidos_bp.route("/<int:id>/detalles", methods=["GET"])
@login_required
def get_detalles_admin(id):
    cursor = mysql.connection.cursor()
    try:
        # Esta ruta es ahora redundante con /detalle_pedidos/pedido/<id>, pero la mantenemos por retrocompatibilidad
        cursor.execute("""
            SELECT dp.*, p.nombre as producto_nombre 
            FROM detalle_pedidos dp JOIN productos p ON dp.producto_id = p.id_producto
            WHERE dp.pedido_id = %s
        """, (id,))
        detalles = [dict(d) for d in cursor.fetchall()]
        for d in detalles:
            d['subtotal'] = float(d['subtotal'] or 0)
            d['precio_unitario'] = float(d.get('precio_unitario') or 0)
        return jsonify(detalles)
    finally:
        if cursor: cursor.close()

# ==================== ENDPOINTS PÚBLICOS 🌍 ====================

@pedidos_bp.route("/public", methods=["POST"])
def create_pedido_public():
    data = request.get_json()
    cursor = mysql.connection.cursor()
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
        mysql.connection.commit()

        # 🛡️ LOG: Nuevo pedido entrante
        registrar_log(f"Recibió nuevo pedido web: ID #{pedido_id}")

        return jsonify({"mensaje": "Pedido recibido", "id_pedido": pedido_id}), 201
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor: cursor.close()

@pedidos_bp.route("/public/login", methods=["POST"])
def login_cliente():
    from models import User
    data = request.get_json()
    user = User.get_by_email(data.get("email"))
    if user and user.check_password(data.get("password")) and user.rol == 'cliente':
        login_user(user)

        # 🛡️ LOG: Inicio de sesión de cliente
        registrar_log(f"Cliente inició sesión: {user.email}")

        return jsonify({"usuario": {"id": user.id, "nombre": user.nombre, "email": user.email, "telefono": user.telefono, "direccion": user.direccion}})
    return jsonify({"error": "Credenciales inválidas"}), 401

@pedidos_bp.route("/public/registro", methods=["POST"])
def registro_cliente():
    data = request.get_json()
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("SELECT id_usuario FROM usuarios WHERE email = %s", (data.get("email"),))
        if cursor.fetchone(): return jsonify({"error": "Email ya registrado"}), 400
        hashed = generate_password_hash(data.get("password"))
        cursor.execute("""
            INSERT INTO usuarios (nombre, email, password, telefono, direccion, rol, fecha_registro)
            VALUES (%s, %s, %s, %s, %s, 'cliente', NOW())
        """, (data.get("nombre"), data.get("email"), hashed, data.get("telefono"), data.get("direccion")))
        mysql.connection.commit()

        # 🛡️ LOG: Registro de cliente
        registrar_log(f"Nuevo cliente registrado: {data.get('email')}")

        return jsonify({"mensaje": "Registro exitoso"}), 201
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor: cursor.close()

@pedidos_bp.route("/public/logout", methods=["POST"])
def logout_cliente():
    from flask_login import logout_user
    logout_user()
    return jsonify({"mensaje": "Sesión cerrada"})

@pedidos_bp.route("/public/mis-pedidos", methods=["GET"])
@login_required
def mis_pedidos():
    cursor = mysql.connection.cursor()
    try:
        # Esta ruta ya fue optimizada para evitar N+1, solo se cambia la conexión
        # 1. Obtener todos los pedidos del usuario (1ª consulta)
        cursor.execute("SELECT * FROM pedidos WHERE usuario_id = %s ORDER BY fecha_pedido DESC", (current_user.id,))
        pedidos = [dict(p) for p in cursor.fetchall()]

        if not pedidos:
            return jsonify({"pedidos": []})

        # 2. Obtener TODOS los detalles para ESOS pedidos en una sola consulta (2ª consulta)
        pedido_ids = [p['id_pedido'] for p in pedidos]
        placeholders = ','.join(['%s'] * len(pedido_ids))
        cursor.execute(f"""
            SELECT dp.pedido_id, dp.cantidad, dp.subtotal, pr.nombre 
            FROM detalle_pedidos dp JOIN productos pr ON dp.producto_id = pr.id_producto 
            WHERE dp.pedido_id IN ({placeholders})
        """, tuple(pedido_ids))
        detalles_todos = cursor.fetchall()

        # 3. Mapear los detalles a sus pedidos correspondientes en Python (muy rápido)
        detalles_por_pedido = {}
        for detalle in detalles_todos:
            pedido_id = detalle['pedido_id']
            if pedido_id not in detalles_por_pedido:
                detalles_por_pedido[pedido_id] = []
            detalles_por_pedido[pedido_id].append({
                "nombre": detalle['nombre'], "cantidad": detalle['cantidad'], "subtotal": float(detalle['subtotal'])
            })

        # 4. Combinar los datos
        for p in pedidos:
            p['total'] = float(p['total'] or 0)
            p['fecha_pedido'] = p['fecha_pedido'].strftime('%Y-%m-%d %H:%M') if p['fecha_pedido'] else ""
            p['detalles'] = detalles_por_pedido.get(p['id_pedido'], [])
        return jsonify({"pedidos": pedidos})
    finally:
        if cursor: cursor.close()