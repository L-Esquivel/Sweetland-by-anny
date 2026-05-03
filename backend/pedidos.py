from flask import Blueprint, jsonify, request
from flask_login import login_required
from extensions import mysql
import logging
from werkzeug.security import generate_password_hash
import secrets
import string

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

pedidos_bp = Blueprint("pedidos", __name__, url_prefix="/pedidos")

# ==================== GET PEDIDOS ====================

@pedidos_bp.route("/", methods=["GET"])
@login_required
def get_pedidos():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT 
                p.id_pedido, 
                u.nombre AS cliente_nombre,
                u.telefono AS cliente_telefono,
                p.fecha_pedido, 
                p.estado,
                p.total,
                p.direccion,
                COUNT(dp.id_detalle) as total_productos
            FROM pedidos p
            LEFT JOIN usuarios u ON p.usuario_id = u.id_usuario
            LEFT JOIN detalle_pedidos dp ON p.id_pedido = dp.pedido_id
            GROUP BY p.id_pedido, u.nombre, u.telefono, p.fecha_pedido, p.estado, p.total, p.direccion
            ORDER BY p.fecha_pedido DESC
        """)
        filas = cursor.fetchall()
        cursor.close()

        return jsonify([{
            "id":               f["id_pedido"],
            "cliente_nombre":   f["cliente_nombre"] or "Cliente no registrado",
            "cliente_telefono": f["cliente_telefono"] or "Sin teléfono",
            "fecha_pedido":     f["fecha_pedido"].strftime('%Y-%m-%d %H:%M:%S') if f["fecha_pedido"] else None,
            "estado":           f["estado"] or "pendiente",
            "total":            float(f["total"]) if f["total"] else 0,
            "direccion":        f["direccion"] or "Sin dirección",
            "total_productos":  f["total_productos"]
        } for f in filas])

    except Exception as e:
        logger.error(f"Error en get_pedidos: {str(e)}")
        return jsonify({"error": f"Error del servidor: {str(e)}"}), 500

# ==================== GET DETALLES PEDIDO ====================

@pedidos_bp.route("/<int:id>/detalles", methods=["GET"])
@login_required
def get_detalles_pedido(id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id_pedido FROM pedidos WHERE id_pedido = %s", (id,))
        if not cursor.fetchone():
            cursor.close()
            return jsonify({"error": f"Pedido {id} no encontrado"}), 404

        cursor.execute("""
            SELECT dp.id_detalle, dp.producto_id, p.nombre AS producto_nombre,
                   p.categoria, dp.cantidad, dp.precio_unitario, dp.subtotal
            FROM detalle_pedidos dp
            INNER JOIN productos p ON dp.producto_id = p.id_producto
            WHERE dp.pedido_id = %s
        """, (id,))
        detalles = cursor.fetchall()
        cursor.close()

        return jsonify([{
            "id":              d["id_detalle"],
            "producto_id":     d["producto_id"],
            "producto_nombre": d["producto_nombre"],
            "categoria":       d["categoria"],
            "cantidad":        d["cantidad"],
            "precio_unitario": float(d["precio_unitario"]) if d["precio_unitario"] else 0,
            "subtotal":        float(d["subtotal"]) if d["subtotal"] else 0
        } for d in detalles])

    except Exception as e:
        logger.error(f"Error en get_detalles_pedido: {str(e)}")
        return jsonify({"error": f"Error del servidor: {str(e)}"}), 500

# ==================== GET PEDIDO ====================

@pedidos_bp.route("/<int:id>", methods=["GET"])
@login_required
def get_pedido(id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT p.id_pedido, u.nombre, u.telefono, p.fecha_pedido,
                   p.estado, p.total, p.direccion
            FROM pedidos p
            LEFT JOIN usuarios u ON p.usuario_id = u.id_usuario
            WHERE p.id_pedido = %s
        """, (id,))
        f = cursor.fetchone()
        cursor.close()

        if not f:
            return jsonify({"error": "Pedido no encontrado"}), 404

        return jsonify({
            "id_pedido":        f["id_pedido"],
            "cliente_nombre":   f["nombre"] or "Cliente no registrado",
            "cliente_telefono": f["telefono"] or "Sin teléfono",
            "fecha_pedido":     f["fecha_pedido"].strftime('%Y-%m-%d %H:%M:%S') if f["fecha_pedido"] else None,
            "estado":           f["estado"] or "pendiente",
            "total":            float(f["total"]) if f["total"] else 0,
            "direccion":        f["direccion"] or "Sin dirección"
        })

    except Exception as e:
        logger.error(f"Error en get_pedido: {str(e)}")
        return jsonify({"error": f"Error del servidor: {str(e)}"}), 500

# ==================== CREATE PEDIDO ====================

@pedidos_bp.route("/", methods=["POST"])
@login_required
def create_pedido():
    try:
        data      = request.get_json()
        cursor    = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO pedidos (usuario_id, telefono, direccion, total, estado, fecha_pedido)
            VALUES (%s, %s, %s, %s, 'pendiente', NOW())
        """, (data.get("usuario_id"), data.get("telefono"), data.get("direccion"), data.get("total", 0)))
        pedido_id = cursor.lastrowid
        mysql.connection.commit()
        cursor.close()
        return jsonify({"mensaje": "Pedido creado correctamente", "id_pedido": pedido_id}), 201

    except Exception as e:
        logger.error(f"Error en create_pedido: {str(e)}")
        return jsonify({"error": f"Error del servidor: {str(e)}"}), 500

# ==================== UPDATE PEDIDO ====================

@pedidos_bp.route("/<int:id>", methods=["PUT"])
@login_required
def update_pedido(id):
    try:
        data   = request.get_json()
        cursor = mysql.connection.cursor()
        cursor.execute("""
            UPDATE pedidos SET total=%s, direccion=%s, telefono=%s, estado=%s WHERE id_pedido=%s
        """, (data.get("total"), data.get("direccion"), data.get("telefono"), data.get("estado"), id))
        mysql.connection.commit()
        cursor.close()
        return jsonify({"mensaje": "Pedido actualizado correctamente"})

    except Exception as e:
        logger.error(f"Error en update_pedido: {str(e)}")
        return jsonify({"error": f"Error del servidor: {str(e)}"}), 500

# ==================== DELETE PEDIDO ====================

@pedidos_bp.route("/<int:id>", methods=["DELETE"])
@login_required
def delete_pedido(id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM detalle_pedidos WHERE pedido_id = %s", (id,))
        cursor.execute("DELETE FROM pedidos WHERE id_pedido = %s", (id,))
        mysql.connection.commit()
        cursor.close()
        return jsonify({"mensaje": "Pedido eliminado correctamente"})

    except Exception as e:
        logger.error(f"Error en delete_pedido: {str(e)}")
        return jsonify({"error": f"Error del servidor: {str(e)}"}), 500

# ==================== UPDATE ESTADO ====================

@pedidos_bp.route("/<int:id>/estado", methods=["PUT"])
@login_required
def update_estado_pedido(id):
    try:
        data         = request.get_json()
        nuevo_estado = data.get("estado")
        estados_ok   = ['pendiente', 'confirmado', 'en_preparacion', 'completado', 'cancelado']

        if nuevo_estado not in estados_ok:
            return jsonify({"error": "Estado no válido"}), 400

        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE pedidos SET estado=%s WHERE id_pedido=%s", (nuevo_estado, id))
        mysql.connection.commit()
        cursor.close()
        return jsonify({"mensaje": f"Estado actualizado a '{nuevo_estado}'", "estado": nuevo_estado})

    except Exception as e:
        logger.error(f"Error en update_estado_pedido: {str(e)}")
        return jsonify({"error": f"Error del servidor: {str(e)}"}), 500

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

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id_pedido FROM pedidos WHERE id_pedido = %s", (pedido_id,))
        if not cursor.fetchone():
            cursor.close()
            return jsonify({"error": "Pedido no encontrado"}), 404

        cursor.execute("""
            INSERT INTO detalle_pedidos (pedido_id, producto_id, cantidad, subtotal)
            VALUES (%s, %s, %s, %s)
        """, (pedido_id, producto_id, cantidad, subtotal))
        detalle_id = cursor.lastrowid
        mysql.connection.commit()
        cursor.close()
        return jsonify({"mensaje": "Detalle creado correctamente", "id_detalle": detalle_id}), 201

    except Exception as e:
        logger.error(f"Error en agregar_detalle_pedido: {str(e)}")
        return jsonify({"error": f"Error del servidor: {str(e)}"}), 500

# ==================== USUARIOS (desde panel de pedidos) ====================

@pedidos_bp.route("/usuarios", methods=["GET"])
@login_required
def get_usuarios():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT id_usuario, nombre, telefono, email, direccion
            FROM usuarios WHERE rol = 'cliente' ORDER BY nombre
        """)
        filas = cursor.fetchall()
        cursor.close()
        return jsonify([{
            "id_usuario": f["id_usuario"],
            "nombre":     f["nombre"],
            "telefono":   f["telefono"] or "",
            "email":      f["email"] or "",
            "direccion":  f["direccion"] or ""
        } for f in filas])

    except Exception as e:
        logger.error(f"Error en get_usuarios: {str(e)}")
        return jsonify({"error": f"Error del servidor: {str(e)}"}), 500


@pedidos_bp.route("/usuarios", methods=["POST"])
@login_required
def create_usuario():
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

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id_usuario FROM usuarios WHERE email = %s", (email,))
        if cursor.fetchone():
            cursor.close()
            return jsonify({"error": "El email ya está registrado"}), 400

        cursor.execute("""
            INSERT INTO usuarios (nombre, email, password, telefono, direccion, rol, fecha_registro)
            VALUES (%s, %s, %s, %s, %s, 'cliente', NOW())
        """, (nombre, email, password_hash, telefono, direccion))
        usuario_id = cursor.lastrowid
        mysql.connection.commit()
        cursor.close()

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
        logger.error(f"Error en create_usuario: {str(e)}")
        return jsonify({"error": f"Error del servidor: {str(e)}"}), 500

# ==================== ENDPOINTS PÚBLICOS (Landing Page) ====================

@pedidos_bp.route("/public", methods=["POST"])
def create_pedido_public():
    try:
        data       = request.get_json()
        usuario_id = data.get("usuario_id")
        telefono   = data.get("telefono", "")
        direccion  = data.get("direccion", "")
        total      = data.get("total", 0)
        items      = data.get("items", [])

        if not items:
            return jsonify({"error": "El carrito está vacío"}), 400

        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO pedidos (usuario_id, telefono, direccion, total, estado, fecha_pedido)
            VALUES (%s, %s, %s, %s, 'pendiente', NOW())
        """, (usuario_id, telefono, direccion, total))
        pedido_id = cursor.lastrowid

        for item in items:
            producto_id = item.get("id_producto")
            cantidad    = item.get("cantidad", 1)
            precio      = item.get("precio", 0)
            subtotal    = item.get("subtotal", precio * cantidad)
            if not producto_id:
                continue
            cursor.execute("""
                INSERT INTO detalle_pedidos (pedido_id, producto_id, cantidad, precio_unitario, subtotal)
                VALUES (%s, %s, %s, %s, %s)
            """, (pedido_id, producto_id, cantidad, precio, subtotal))

        mysql.connection.commit()
        cursor.close()
        return jsonify({"mensaje": "Pedido registrado correctamente", "id_pedido": pedido_id}), 201

    except Exception as e:
        logger.error(f"Error en create_pedido_public: {str(e)}")
        return jsonify({"error": f"Error del servidor: {str(e)}"}), 500


@pedidos_bp.route("/public/login", methods=["POST"])
def login_cliente():
    from models import User
    from flask_login import login_user
    data     = request.get_json()
    email    = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email y contraseña son requeridos"}), 400

    user = User.get_by_email(email)
    if user and user.check_password(password):
        if user.rol != 'cliente':
            return jsonify({"error": "Acceso no permitido"}), 403
        login_user(user)
        return jsonify({
            "mensaje": "Login exitoso",
            "usuario": {"id": user.id, "nombre": user.nombre, "email": user.email,
                        "telefono": user.telefono, "direccion": user.direccion}
        })
    return jsonify({"error": "Credenciales inválidas"}), 401


@pedidos_bp.route("/public/registro", methods=["POST"])
def registro_cliente():
    data      = request.get_json()
    nombre    = data.get("nombre")
    email     = data.get("email")
    password  = data.get("password")
    telefono  = data.get("telefono", "")
    direccion = data.get("direccion", "")

    if not nombre or not email or not password:
        return jsonify({"error": "Nombre, email y contraseña son requeridos"}), 400

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id_usuario FROM usuarios WHERE email = %s", (email,))
    if cursor.fetchone():
        cursor.close()
        return jsonify({"error": "El email ya está registrado"}), 400

    hashed = generate_password_hash(password)
    cursor.execute("""
        INSERT INTO usuarios (nombre, email, password, telefono, direccion, rol, fecha_registro)
        VALUES (%s, %s, %s, %s, %s, 'cliente', NOW())
    """, (nombre, email, hashed, telefono, direccion))
    mysql.connection.commit()
    cursor.close()
    return jsonify({"mensaje": "Registro exitoso. Ya puedes iniciar sesión."}), 201


@pedidos_bp.route("/public/logout", methods=["POST"])
def logout_cliente():
    from flask_login import logout_user
    logout_user()
    return jsonify({"mensaje": "Sesión cerrada"})


@pedidos_bp.route("/public/mis-pedidos", methods=["GET"])
def mis_pedidos():
    from flask_login import current_user
    if not current_user.is_authenticated:
        return jsonify({"error": "No autenticado"}), 401

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT p.id_pedido, p.fecha_pedido, p.total, p.estado,
                   COUNT(dp.id_detalle) as total_productos
            FROM pedidos p
            LEFT JOIN detalle_pedidos dp ON p.id_pedido = dp.pedido_id
            WHERE p.usuario_id = %s
            GROUP BY p.id_pedido
            ORDER BY p.fecha_pedido DESC
        """, (current_user.id,))
        filas = cursor.fetchall()

        pedidos = []
        for f in filas:
            cursor.execute("""
                SELECT dp.cantidad, dp.precio_unitario, dp.subtotal, pr.nombre, pr.imagen
                FROM detalle_pedidos dp
                LEFT JOIN productos pr ON dp.producto_id = pr.id_producto
                WHERE dp.pedido_id = %s
            """, (f["id_pedido"],))
            detalles_raw = cursor.fetchall()
            pedidos.append({
                "id_pedido":       f["id_pedido"],
                "fecha_pedido":    f["fecha_pedido"].strftime('%Y-%m-%d %H:%M') if f["fecha_pedido"] else None,
                "total":           float(f["total"]) if f["total"] else 0,
                "estado":          f["estado"] or "pendiente",
                "total_productos": f["total_productos"],
                "detalles": [{
                    "cantidad":        d["cantidad"],
                    "precio_unitario": float(d["precio_unitario"]) if d["precio_unitario"] else 0,
                    "subtotal":        float(d["subtotal"]) if d["subtotal"] else 0,
                    "nombre":          d["nombre"],
                    "imagen":          d["imagen"]
                } for d in detalles_raw]
            })

        cursor.close()
        return jsonify({"pedidos": pedidos})

    except Exception as e:
        logger.error(f"Error en mis_pedidos: {str(e)}")
        return jsonify({"error": str(e)}), 500