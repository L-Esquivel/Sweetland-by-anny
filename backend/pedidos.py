from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user, login_user, logout_user
from utils import admin_required, registrar_log # 🛡️ Importamos la auditoría
from extensions import mysql
from werkzeug.security import generate_password_hash
import secrets, string, logging, datetime

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
        # 1. Obtener y validar rango de fechas (default: últimos 30 días)
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=29)
        
        fecha_inicio_str = request.args.get('fecha_inicio', start_date.strftime('%Y-%m-%d'))
        fecha_fin_str = request.args.get('fecha_fin', end_date.strftime('%Y-%m-%d'))
        params = (fecha_inicio_str, fecha_fin_str)

        # 2. Resumen financiero para el rango
        where_pedidos = " WHERE estado != 'cancelado' AND DATE(fecha_pedido) BETWEEN %s AND %s "
        cursor.execute(f"""
            SELECT 
                SUM(total) as total_ventas_rango,
                COUNT(id_pedido) as num_pedidos_rango
            FROM pedidos {where_pedidos}
        """, params)
        resumen_rango_raw = cursor.fetchone()
        resumen = {
            'total_ventas_rango': float(resumen_rango_raw.get('total_ventas_rango') or 0),
            'num_pedidos_rango': int(resumen_rango_raw.get('num_pedidos_rango') or 0)
        }
        
        # 3. Sumar gastos en el mismo rango de fechas
        cursor.execute("""
            SELECT SUM(monto) as total_gastos_rango
            FROM gastos WHERE fecha BETWEEN %s AND %s
        """, params)
        gastos_rango_raw = cursor.fetchone()
        resumen['total_gastos_rango'] = float(gastos_rango_raw.get('total_gastos_rango') or 0)

        # 4. Sumar merma en el mismo rango de fechas
        cursor.execute("""
            SELECT SUM(costo_perdida) as total_merma_rango
            FROM merma WHERE fecha BETWEEN %s AND %s
        """, params)
        merma_rango_raw = cursor.fetchone()
        resumen['total_merma_rango'] = float(merma_rango_raw.get('total_merma_rango') or 0)

        # 5. Datos para la gráfica para el rango
        cursor.execute(f"""
            SELECT DATE(fecha_pedido) as fecha, SUM(total) as venta 
            FROM pedidos {where_pedidos}
            GROUP BY DATE(fecha_pedido) ORDER BY fecha ASC
        """, params)
        grafica_raw = cursor.fetchall()
        grafica = [{"fecha": str(row['fecha']), "venta": float(row['venta'])} for row in grafica_raw]

        # 6. Pedidos por estado para el rango
        cursor.execute(f"SELECT estado, COUNT(id_pedido) as cantidad FROM pedidos {where_pedidos} GROUP BY estado", params)
        estados_raw = cursor.fetchall()
        pedidos_por_estado = {row['estado']: row['cantidad'] for row in estados_raw}

        # 7. Producto Top para el rango
        where_pedidos_aliased = " WHERE ped.estado = 'completado' AND DATE(ped.fecha_pedido) BETWEEN %s AND %s "
        cursor.execute(f"""
            SELECT p.nombre, p.precio, SUM(dp.cantidad) as total_vendido
            FROM detalle_pedidos dp
            JOIN productos p ON dp.producto_id = p.id_producto
            JOIN pedidos ped ON dp.pedido_id = ped.id_pedido
            {where_pedidos_aliased}
            GROUP BY p.id_producto
            ORDER BY total_vendido DESC LIMIT 1
        """, params)
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
            "producto_top": producto_top,
            "filtros_aplicados": {"fecha_inicio": fecha_inicio_str, "fecha_fin": fecha_fin_str}
        })
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
    nombre = data.get("nombre")
    email = data.get("email")
    password = data.get("password")

    # 💡 MEJORA: Validar que los campos esenciales no estén vacíos.
    # Esto previene errores 500 si falta la contraseña y devuelve un 400 claro.
    if not nombre or not email or not password:
        return jsonify({"error": "Nombre, email y contraseña son obligatorios"}), 400

    cursor = mysql.connection.cursor()
    try:
        cursor.execute("SELECT id_usuario FROM usuarios WHERE email = %s", (email,))
        if cursor.fetchone(): return jsonify({"error": "Email ya registrado"}), 400
        hashed = generate_password_hash(password)
        cursor.execute("""
            INSERT INTO usuarios (nombre, email, password, telefono, direccion, rol, fecha_registro)
            VALUES (%s, %s, %s, %s, %s, 'cliente', NOW())
        """, (nombre, email, hashed, data.get("telefono"), data.get("direccion")))
        mysql.connection.commit()

        # 🛡️ LOG: Registro de cliente
        registrar_log(f"Nuevo cliente registrado: {email}")

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