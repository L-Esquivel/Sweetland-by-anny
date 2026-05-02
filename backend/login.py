from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from db import get_db_connection
from models import User

auth_bp = Blueprint("auth_bp", __name__, url_prefix="/auth")

# =========================
# Rutas OPTIONS para CORS
# =========================
@auth_bp.route("/registrarse", methods=["OPTIONS"])
@auth_bp.route("/login", methods=["OPTIONS"])
@auth_bp.route("/logout", methods=["OPTIONS"])
@auth_bp.route("/me", methods=["OPTIONS"])
def handle_auth_options():
    return jsonify({"status": "ok"}), 200

# =========================
# Registro de usuario
# =========================
@auth_bp.route("/registrarse", methods=["POST"])
def registrarse():
    data = request.json
    nombre = data.get("nombre")
    email = data.get("email")
    password = data.get("password")
    telefono = data.get("telefono")
    direccion = data.get("direccion")
    rol = data.get("rol", "cliente")

    if not nombre or not email or not password:
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    if User.get_by_email(email):
        return jsonify({"error": "El email ya está registrado"}), 400

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

    return jsonify({"mensaje": "Usuario registrado con éxito"}), 201

# =========================
# Login
# =========================
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Faltan datos"}), 400

    user = User.get_by_email(email)
    if user and user.check_password(password):
        login_user(user)
        return jsonify({
            "mensaje": "Login exitoso",
            "usuario": {
                "id": user.id,
                "nombre": user.nombre,
                "email": user.email,
                "telefono": user.telefono,
                "direccion": user.direccion,
                "rol": user.rol
            }
        })
    return jsonify({"error": "Credenciales inválidas"}), 401

# =========================
# Logout
# =========================
@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"mensaje": "Sesión cerrada"})

# =========================
# Obtener usuario actual
# =========================
@auth_bp.route("/me", methods=["GET"])
@login_required
def get_current_user():
    return jsonify({
        "usuario": {
            "id": current_user.id,
            "nombre": current_user.nombre,
            "email": current_user.email, 
            "telefono": current_user.telefono,
            "direccion": current_user.direccion,
            "rol": current_user.rol
        }
    })