from flask import Blueprint, request, jsonify
from flask_login import login_required
from db import get_db_connection
from werkzeug.security import generate_password_hash

usuarios_bp = Blueprint("usuarios_bp", __name__, url_prefix="/usuarios")

# Rutas OPTIONS SIN autenticación
@usuarios_bp.route("/", methods=["OPTIONS"])
@usuarios_bp.route("/<int:id>", methods=["OPTIONS"])
def handle_options(id=None):
    return jsonify({"status": "ok"}), 200

# =========================
# Obtener todos los usuarios
# =========================
@usuarios_bp.route("/", methods=["GET"])
@login_required
def get_usuarios():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id_usuario, nombre, email, telefono, direccion, rol FROM usuarios")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(rows)

# =========================
# Obtener un usuario por id
# =========================
@usuarios_bp.route("/<int:id>", methods=["GET"])
@login_required
def get_usuario(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id_usuario, nombre, email, telefono, direccion, rol FROM usuarios WHERE id_usuario = %s", (id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row:
        return jsonify(row)
    return jsonify({"error": "Usuario no encontrado"}), 404

# =========================
# Agregar un nuevo usuario
# =========================
@usuarios_bp.route("/", methods=["POST"])
@login_required
def add_usuario():
    data = request.json
    nombre = data.get("nombre")
    email = data.get("email")
    password = data.get("password")
    telefono = data.get("telefono")
    direccion = data.get("direccion")
    rol = data.get("rol", "cliente")

    if not nombre or not email or not password:
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    hashed_pw = generate_password_hash(password)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO usuarios (nombre, email, password, telefono, direccion, rol)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (nombre, email, hashed_pw, telefono, direccion, rol))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"mensaje": "Usuario agregado"}), 201

# =========================
# Actualizar un usuario
# =========================
@usuarios_bp.route("/<int:id>", methods=["PUT"])
@login_required
def update_usuario(id):
    data = request.json
    nombre = data.get("nombre")
    email = data.get("email")
    telefono = data.get("telefono")
    direccion = data.get("direccion")
    rol = data.get("rol")
    password = data.get("password")

    conn = get_db_connection()
    cursor = conn.cursor()

    if password:
        hashed_pw = generate_password_hash(password)
        cursor.execute("""
            UPDATE usuarios
            SET nombre=%s, email=%s, telefono=%s, direccion=%s, rol=%s, password=%s
            WHERE id_usuario=%s
        """, (nombre, email, telefono, direccion, rol, hashed_pw, id))
    else:
        cursor.execute("""
            UPDATE usuarios
            SET nombre=%s, email=%s, telefono=%s, direccion=%s, rol=%s
            WHERE id_usuario=%s
        """, (nombre, email, telefono, direccion, rol, id))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"mensaje": "Usuario actualizado"})

# =========================
# Eliminar un usuario
# =========================
@usuarios_bp.route("/<int:id>", methods=["DELETE"])
@login_required
def delete_usuario(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id_usuario=%s", (id,))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"mensaje": "Usuario eliminado"})