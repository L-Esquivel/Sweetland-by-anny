from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user, login_user, logout_user
from db import get_db_connection
from utils import admin_required
from werkzeug.security import generate_password_hash
import secrets, string, logging

pedidos_bp = Blueprint("pedidos", __name__, url_prefix="/pedidos")

# --- LÓGICA DE STOCK ---
def procesar_descuento_stock(pedido_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT producto_id, cantidad FROM detalle_pedidos WHERE pedido_id = %s", (pedido_id,))
    for item in cursor.fetchall():
        cursor.execute("UPDATE productos SET stock = stock - %s WHERE id_producto = %s AND controla_stock = TRUE", 
                       (item['cantidad'], item['producto_id']))
    conn.commit()
    cursor.close()
    conn.close()

# --- ADMIN ENDPOINTS ---

@pedidos_bp.route("/stats", methods=["GET"])
@login_required
@admin_required
def get_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN DATE(fecha_pedido) = CURDATE() THEN total ELSE 0 END) as hoy,
            SUM(CASE WHEN MONTH(fecha_pedido) = MONTH(CURDATE()) AND YEAR(fecha_pedido) = YEAR(CURDATE()) THEN total ELSE 0 END) as mes,
            SUM(total) as total_historico,
            COUNT(id_pedido) as num_pedidos
        FROM pedidos WHERE estado != 'cancelado'
    """)
    resumen = cursor.fetchone()
    cursor.execute("""
        SELECT DATE(fecha_pedido) as fecha, SUM(total) as venta FROM pedidos 
        WHERE estado != 'cancelado' GROUP BY DATE(fecha_pedido) ORDER BY fecha DESC LIMIT 7
    """)
    grafica = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({"resumen": resumen, "grafica": list(grafica)})

@pedidos_bp.route("/", methods=["GET"])
@login_required
def get_pedidos():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.*, u.nombre as cliente_nombre, u.telefono as cliente_telefono 
        FROM pedidos p LEFT JOIN usuarios u ON p.usuario_id = u.id_usuario ORDER BY p.fecha_pedido DESC
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(list(rows))

@pedidos_bp.route("/<int:id>/estado", methods=["PUT"])
@login_required
def update_estado_pedido(id):
    data = request.get_json()
    nuevo_estado = data.get("estado")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT estado FROM pedidos WHERE id_pedido = %s", (id,))
    actual = cursor.fetchone()
    if nuevo_estado == 'completado' and actual.get('estado') != 'completado':
        procesar_descuento_stock(id)
    cursor.execute("UPDATE pedidos SET estado=%s WHERE id_pedido=%s", (nuevo_estado, id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"mensaje": "Estado actualizado"})

@pedidos_bp.route("/usuarios", methods=["GET"])
@login_required
def get_usuarios_pedidos():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_usuario, nombre, telefono, email FROM usuarios WHERE rol='cliente'")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(list(rows))

# --- PUBLIC ENDPOINTS (LANDING) ---

@pedidos_bp.route("/public", methods=["POST"])
def create_pedido_public():
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Nota: Usamos usuario_id (con guión bajo) porque así está en la DB
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
        return jsonify({"usuario": {"id": user.id, "nombre": user.nombre, "email": user.email}})
    return jsonify({"error": "Credenciales inválidas"}), 401

@pedidos_bp.route("/public/mis-pedidos", methods=["GET"])
@login_required
def mis_pedidos():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pedidos WHERE usuario_id = %s ORDER BY fecha_pedido DESC", (current_user.id,))
    pedidos = cursor.fetchall()
    # Para cada pedido, traer sus detalles
    for p in pedidos:
        cursor.execute("""
            SELECT dp.*, pr.nombre FROM detalle_pedidos dp 
            JOIN productos pr ON dp.producto_id = pr.id_producto WHERE dp.pedido_id = %s
        """, (p['id_pedido'],))
        p['detalles'] = list(cursor.fetchall())
    cursor.close()
    conn.close()
    return jsonify({"pedidos": list(pedidos)})

@pedidos_bp.route("/public/registro", methods=["POST"])
def registro_cliente():
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed = generate_password_hash(data.get("password"))
    cursor.execute("""
        INSERT INTO usuarios (nombre, email, password, telefono, direccion, rol)
        VALUES (%s, %s, %s, %s, %s, 'cliente')
    """, (data.get("nombre"), data.get("email"), hashed, data.get("telefono"), data.get("direccion")))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"mensaje": "Registrado"}), 201