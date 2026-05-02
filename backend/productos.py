from flask import Blueprint, request, jsonify
from flask_login import login_required
from db import get_db_connection

productos_bp = Blueprint("productos_bp", __name__, url_prefix="/productos")

# ==================== PREFLIGHT CORS ====================

@productos_bp.route("/", methods=["OPTIONS"])
@productos_bp.route("/<int:id>", methods=["OPTIONS"])
@productos_bp.route("/public", methods=["OPTIONS"])
def handle_options(id=None):
    return jsonify({"status": "ok"}), 200

# ==================== RUTAS PRIVADAS (Panel Admin) ====================

@productos_bp.route("/", methods=["GET"])
@login_required
def get_productos():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id_producto, nombre, categoria, descripcion, precio, imagen FROM productos")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(rows)

@productos_bp.route("/<int:id>", methods=["GET"])
@login_required
def get_producto(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id_producto, nombre, categoria, descripcion, precio, imagen FROM productos WHERE id_producto=%s", (id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row:
        return jsonify(row)
    return jsonify({"error": "Producto no encontrado"}), 404

@productos_bp.route("/", methods=["POST"])
@login_required
def add_producto():
    data = request.json
    nombre = data.get("nombre")
    categoria = data.get("categoria")
    descripcion = data.get("descripcion")
    precio = data.get("precio")
    imagen = data.get("imagen")

    if not nombre or not categoria or not precio:
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO productos (nombre, categoria, descripcion, precio, imagen)
        VALUES (%s, %s, %s, %s, %s)
    """, (nombre, categoria, descripcion, precio, imagen))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"mensaje": "Producto agregado"}), 201

@productos_bp.route("/<int:id>", methods=["PUT"])
@login_required
def update_producto(id):
    data = request.json
    nombre = data.get("nombre")
    categoria = data.get("categoria")
    descripcion = data.get("descripcion")
    precio = data.get("precio")
    imagen = data.get("imagen")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE productos
        SET nombre=%s, categoria=%s, descripcion=%s, precio=%s, imagen=%s
        WHERE id_producto=%s
    """, (nombre, categoria, descripcion, precio, imagen, id))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"mensaje": "Producto actualizado"})

@productos_bp.route("/<int:id>", methods=["DELETE"])
@login_required
def delete_producto(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE id_producto=%s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"mensaje": "Producto eliminado"})

# ==================== ENDPOINTS PÚBLICOS (Landing Page) ====================

@productos_bp.route("/public", methods=["GET"])
def get_productos_public():
    """Endpoint público para la página web de clientes"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id_producto, nombre, categoria, descripcion, precio, imagen
            FROM productos
            ORDER BY categoria, nombre
        """)
        productos = cursor.fetchall()
        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "productos": productos
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500