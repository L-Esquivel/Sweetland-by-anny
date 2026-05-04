from flask import Blueprint, request, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from db import get_db_connection
from models import User
from extensions import mail, limiter # Importamos las instancias globales
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer

auth_bp = Blueprint("auth_bp", __name__, url_prefix="/auth")

@auth_bp.route("/login", methods=["POST"])
@limiter.limit("5 per minute") # BLINDAJE ANTI-BRUTEFORCE 🛡️
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
                "id": user.id, "nombre": user.nombre, "email": user.email,
                "telefono": user.telefono, "direccion": user.direccion, "rol": user.rol
            }
        })
    return jsonify({"error": "Credenciales inválidas"}), 401

# --- RECUPERACIÓN DE CONTRASEÑA ---

@auth_bp.route("/forgot-password", methods=["POST"])
@limiter.limit("3 per hour") # Previene SPAM de correos
def forgot_password():
    data = request.get_json()
    email = data.get("email")
    user = User.get_by_email(email)

    # SEGURIDAD: Siempre responder lo mismo para evitar recolectar emails (User Enumeration)
    if user:
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        token = s.dumps(email, salt='password-reset-salt')
        reset_url = f"https://sweetlandbyanny.vercel.app/reset-password.html?token={token}"

        msg = Message("Recuperación de Contraseña - Sweetland", recipients=[email])
        msg.body = f"Hola {user.nombre},\n\nPara restablecer tu clave haz clic aquí: {reset_url}\n\nEl enlace expira en 1 hora."
        try:
            mail.send(msg)
        except Exception as e:
            current_app.logger.error(f"Error SMTP: {e}")

    return jsonify({"mensaje": "Si el correo está registrado, recibirás un enlace pronto."}), 200

@auth_bp.route("/reset-password-confirm", methods=["POST"])
def reset_password_confirm():
    data = request.get_json()
    token = data.get("token")
    new_password = data.get("password")

    try:
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        email = s.loads(token, salt='password-reset-salt', max_age=3600)
    except:
        return jsonify({"error": "El enlace es inválido o ha expirado"}), 400

    hashed_pw = generate_password_hash(new_password)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE usuarios SET password = %s WHERE email = %s", (hashed_pw, email))
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({"mensaje": "Contraseña actualizada correctamente"}), 200

# --- RESTO DE RUTAS ---
@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"mensaje": "Sesión cerrada"})

@auth_bp.route("/me", methods=["GET"])
@login_required
def get_current_user():
    return jsonify({
        "usuario": {
            "id": current_user.id, "nombre": current_user.nombre, "email": current_user.email, 
            "telefono": current_user.telefono, "direccion": current_user.direccion, "rol": current_user.rol
        }
    })