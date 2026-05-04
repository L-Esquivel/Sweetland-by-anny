from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user, login_user
from db import get_db_connection
from utils import admin_required
from werkzeug.security import generate_password_hash
import secrets, string, logging

logger = logging.getLogger(__name__)

pedidos_bp = Blueprint("pedidos", __name__, url_prefix="/pedidos")

# ==================== LÓGICA DE STOCK ====================

def procesar_descuento_stock(pedido_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT producto_id, cantidad FROM detalle_pedidos WHERE pedido_id = %s", (pedido_id,))
    for item in cursor.fetchall():
        cursor.execute("""
            UPDATE productos SET stock = stock - %s 
            WHERE id_producto = %s AND controla_stock = TRUE
        """, (item['cantidad'], item['producto_id']))
    conn.commit()
    cursor.close()
    conn.close()

# ==================== STATS (Dashboard) ====================

@pedidos_bp.route("/stats", methods=["GET"])
@login_required
@admin_required
def get_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN DATE(fecha_pedido) = CURDATE() THEN total ELSE 0 END) as hoy,
                SUM(CASE WHEN MONTH(fecha_pedido) = MONTH(CURDATE()) AND YEAR(fecha_pedido) = YEAR(CURDATE()) THEN total ELSE 0 END) as mes,
                SUM(total) as total_historico,
                COUNT(id_pedido) as num_pedidos
            FROM pedidos WHERE estado != 'cancelado'
        """)
        resumen = cursor.fetchone()
        # Convertir Decimal a float
        resumen = {k: float(v) if v is not None else 0 for k, v in dict(resumen).items()}

        cursor.execute("""
            SELECT DATE(fecha_pedido) as fecha, SUM(total) as venta 
            FROM pedidos WHERE estado != 'cancelado' 
            GROUP BY DATE(fecha_pedido) ORDER BY fecha DESC LIMIT 7
        """)
        grafica = cursor.fetchall()
        grafica = [{k: float(v) if isinstance(v, (int, float)) else str(v) for k, v in dict(row).items()} for row in grafica]

        return jsonify({"resumen": resumen, "grafica": grafica})
    except Exception as e:
        logger.error(f"Error en get_stats: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# ==================== GET PEDIDOS ====================

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
        # Convertir Decimal a float para JSON
        pedidos = []
        for row in rows:
            pedido = dict(row)
            for key in ['total', 'costo_produccion', 'precio_sugerido']:
                if key in pedido and pedido[key] is not None:
                    pedido[key] = float(pedido[key])
            pedidos.append(pedido)
        return jsonify(pedidos)
    except Exception as e:
        logger.error(f"Error en get_pedidos: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# ==================== GET DETALLES PEDIDO ====================

@pedidos_bp.route("/<int:id>/detalles", methods=["GET"])
@login_required
def get_detalles_pedido(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id_pedido FROM pedidos WHERE id_pedido = %s", (id,))
        if not cursor.fetchone():
            return jsonify({"error": f"Pedido {id} no encontrado"}), 404

        cursor.execute("""
            SELECT dp.id_detalle, dp.producto_id, p.nombre AS producto_nombre,
                   p.categoria, dp.cantidad, dp.precio_unitario, dp.subtotal
            FROM detalle_pedidos dp
            INNER JOIN productos p ON dp.producto_id = p.id_producto
            WHERE dp.pedido_id = %s
        """, (id,))
        detalles_raw = cursor.fetchall()

        # CORREGIDO: Convertir Decimal a float para evitar NaN en frontend
        detalles = []
        for row in detalles_raw:
            detalle = dict(row)
            detalle['cantidad'] = int(detalle.get('cantidad', 0) or 0)
            detalle['precio_unitario'] = float(detalle.get('precio_unitario', 0) or 0)
            detalle['subtotal'] = float(detalle.get('subtotal', 0) or 0)
            detalles.append(detalle)

        return jsonify(detalles)
    except Exception as e:
        logger.error(f"Error en get_detalles_pedido: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# ==================== CREATE PEDIDO ====================

@pedidos_bp.route("/", methods=["POST"])
@login_required
def create_pedido():
    try:
        data = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO pedidos (usuario_id, telefono, direccion, total, estado, fecha_pedido)
            VALUES (%s, %s, %s, %s, 'pendiente', NOW())
        """, (data.get("usuario_id"), data.get("telefono"), data.get("direccion"), data.get("total", 0)))
        pedido_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"mensaje": "Pedido creado correctamente", "id_pedido": pedido_id}), 201
    except Exception as e:
        logger.error(f"Error en create_pedido: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ==================== UPDATE PEDIDO ====================

@pedidos_bp.route("/<int:id>", methods=["PUT"])
@login_required
def update_pedido(id):
    try:
        data = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE pedidos SET total=%s, direccion=%s, telefono=%s, estado=%s
            WHERE id_pedido=%s
        """, (data.get("total"), data.get("direccion"), data.get("telefono"), data.get("estado"), id))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"mensaje": "Pedido actualizado correctamente"})
    except Exception as e:
        logger.error(f"Error en update_pedido: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ==================== UPDATE ESTADO ====================

@pedidos_bp.route("/<int:id>/estado", methods=["PUT"])
@login_required
def update_estado_pedido(id):
    try:
        data = request.get_json()
        nuevo_estado = data.get("estado")
        estados_ok = ['pendiente', 'confirmado', 'en_preparacion', 'completado', 'cancelado']
        if nuevo_estado not in estados_ok:
            return jsonify({"error": "Estado no válido"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT estado FROM pedidos WHERE id_pedido = %s", (id,))
        actual = cursor.fetchone()

        if nuevo_estado == 'completado' and actual and actual.get('estado') != 'completado':
            procesar_descuento_stock(id)

        cursor.execute("UPDATE pedidos SET estado=%s WHERE id_pedido=%s", (nuevo_estado, id))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"mensaje": f"Estado actualizado a '{nuevo_estado}'", "estado": nuevo_estado})
    except Exception as e:
        logger.error(f"Error en update_estado_pedido: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ==================== DELETE PEDIDO ====================

@pedidos_bp.route("/<int:id>", methods=["DELETE"])
@login_required
@admin_required
def delete_pedido(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM detalle_pedidos WHERE pedido_id = %s", (id,))
        cursor.execute("DELETE FROM pedidos WHERE id_pedido = %s", (id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"mensaje": "Pedido eliminado correctamente"})
    except Exception as e:
        logger.error(f"Error en delete_pedido: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ==================== AGREGAR DETALLE ====================

@pedidos_bp.route("/<int:pedido_id>/agregar_detalle", methods=["POST"])
@login_required
def agregar_detalle_pedido(pedido_id):
    try:
        data        = request.get_json()
        producto_id = data.get("producto_id")
        cantidad    = data.get("cantidad")
        subtotal    = data.get("subtotal")

        if not all([producto_id, cantidad, subtotal]):
            return jsonify({"error": "Todos los campos son requeridos"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id_pedido FROM pedidos WHERE id_pedido = %s", (pedido_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": "Pedido no encontrado"}), 404

        cursor.execute("""
            INSERT INTO detalle_pedidos (pedido_id, producto_id, cantidad, subtotal)
            VALUES (%s, %s, %s, %s)
        """, (pedido_id, producto_id, cantidad, subtotal))
        detalle_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"mensaje": "Detalle creado correctamente", "id_detalle": detalle_id}), 201
    except Exception as e:
        logger.error(f"Error en agregar_detalle_pedido: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ==================== USUARIOS (desde panel de pedidos) ====================

@pedidos_bp.route("/usuarios", methods=["GET"])
@login_required
def get_usuarios_pedidos():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id_usuario, nombre, telefono, email, direccion FROM usuarios WHERE rol='cliente' ORDER BY nombre")
        rows = cursor.fetchall()
        return jsonify(list(rows))
    except Exception as e:
        logger.error(f"Error en get_usuarios_pedidos: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@pedidos_bp.route("/usuarios", methods=["POST"])
@login_required
def create_usuario_pedido():
    try:
        data      = request.get_json()
        nombre    = data.get("nombre")
        email     = data.get("email")
        telefono  = data.get("telefono", "")
        direccion = data.get("direccion", "")

        if not nombre or not email:
            return jsonify({"error": "Nombre y email son requeridos"}), 400

        password_temp = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
        password_hash = generate_password_hash(password_temp)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id_usuario FROM usuarios WHERE email = %s", (email,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": "El email ya está registrado"}), 400

        cursor.execute("""
            INSERT INTO usuarios (nombre, email, password, telefono, direccion, rol, fecha_registro)
            VALUES (%s, %s, %s, %s, %s, 'cliente', NOW())
        """, (nombre, email, password_hash, telefono, direccion))
        usuario_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "mensaje":           "Usuario creado correctamente",
            "id_usuario":        usuario_id,
            "nombre":            nombre,
            "email":             email,
            "telefono":          telefono,
            "direccion":         direccion,
            "password_temporal": password_temp
        }), 201
    except Exception as e:
        logger.error(f"Error en create_usuario_pedido: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ==================== ENDPOINTS PÚBLICOS (Landing Page) ====================

@pedidos_bp.route("/public", methods=["POST"])
def create_pedido_public():
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
        return jsonify({"id_pedido": pedido_id}), 201
    except Exception as e:
        conn.rollback()
        logger.error(f"Error en create_pedido_public: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@pedidos_bp.route("/public/login", methods=["POST"])
def login_cliente():
    from models import User
    data = request.get_json()
    user = User.get_by_email(data.get("email"))
    if user and user.check_password(data.get("password")) and user.rol == 'cliente':
        login_user(user)
        return jsonify({"usuario": {
            "id":        user.id,
            "nombre":    user.nombre,
            "email":     user.email,
            "telefono":  user.telefono,
            "direccion": user.direccion
        }})
    return jsonify({"error": "Credenciales inválidas"}), 401

@pedidos_bp.route("/public/registro", methods=["POST"])
def registro_cliente():
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id_usuario FROM usuarios WHERE email = %s", (data.get("email"),))
        if cursor.fetchone():
            return jsonify({"error": "El email ya está registrado"}), 400
        hashed = generate_password_hash(data.get("password"))
        cursor.execute("""
            INSERT INTO usuarios (nombre, email, password, telefono, direccion, rol, fecha_registro)
            VALUES (%s, %s, %s, %s, %s, 'cliente', NOW())
        """, (data.get("nombre"), data.get("email"), hashed, data.get("telefono"), data.get("direccion")))
        conn.commit()
        return jsonify({"mensaje": "Registro exitoso"}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@pedidos_bp.route("/public/logout", methods=["POST"])
def logout_cliente():
    from flask_login import logout_user
    logout_user()
    return jsonify({"mensaje": "Sesión cerrada"})

@pedidos_bp.route("/public/mis-pedidos", methods=["GET"])
@login_required
def mis_pedidos():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT * FROM pedidos WHERE usuario_id = %s ORDER BY fecha_pedido DESC
        """, (current_user.id,))
        pedidos = cursor.fetchall()
        for p in pedidos:
            cursor.execute("""
                SELECT dp.*, pr.nombre FROM detalle_pedidos dp 
                JOIN productos pr ON dp.producto_id = pr.id_producto 
                WHERE dp.pedido_id = %s
            """, (p['id_pedido'],))
            p['detalles'] = list(cursor.fetchall())
        return jsonify({"pedidos": list(pedidos)})
    except Exception as e:
        logger.error(f"Error en mis_pedidos: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()