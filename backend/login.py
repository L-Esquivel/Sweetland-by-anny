from flask import Blueprint, request, jsonify, current_app, url_for, redirect
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from db import get_db_connection
from models import User
from extensions import mail, limiter, mysql 
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from utils import registrar_log
from authlib.integrations.flask_client import OAuth
import os

auth_bp = Blueprint("auth_bp", __name__, url_prefix="/auth")

# =========================
# MANEJO DE CORS (OPTIONS) 🛡️
# =========================
@auth_bp.route("/login", methods=["OPTIONS"])
@auth_bp.route("/registrarse", methods=["OPTIONS"])
@auth_bp.route("/forgot-password", methods=["OPTIONS"])
@auth_bp.route("/reset-password-confirm", methods=["OPTIONS"])
def handle_auth_options():
    return jsonify({"status": "ok"}), 200

# --- CONFIGURACIÓN DE OAUTH ---
oauth = OAuth()
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

def init_oauth(app):
    oauth.init_app(app)

# =========================
# LOGIN CON GOOGLE 🌍
# =========================

@auth_bp.route("/login/google")
def login_google():
    redirect_uri = url_for('auth_bp.google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@auth_bp.route("/login/google/callback")
def google_callback():
    try:
        token = google.authorize_access_token()
        user_info = token.get('userinfo')
        if not user_info:
            return jsonify({"error": "No se pudo obtener información de Google"}), 400

        email = user_info['email']
        nombre = user_info['name']
        google_id = user_info['sub']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        user_row = cursor.fetchone()

        if user_row:
            usuario = User(id=user_row["id_usuario"], nombre=user_row["nombre"], 
                           email=user_row["email"], password=user_row["password"], rol=user_row["rol"])
            login_user(usuario)
            registrar_log(f"Inició sesión vía Google: {email}")
        else:
            cursor.execute("""
                INSERT INTO usuarios (nombre, email, rol, google_id, fecha_registro)
                VALUES (%s, %s, 'cliente', %s, NOW())
            """, (nombre, email, google_id))
            conn.commit()
            new_id = cursor.lastrowid
            usuario = User(id=new_id, nombre=nombre, email=email, password=None, rol='cliente')
            login_user(usuario)
            registrar_log(f"Nuevo registro vía Google: {email}")

        cursor.close()
        conn.close()
        return redirect("https://sweetlandbyanny.vercel.app/mi-cuenta.html")
    except Exception as e:
        current_app.logger.error(f"Error en Google Auth: {str(e)}")
        return redirect("https://sweetlandbyanny.vercel.app/mi-cuenta.html?error=auth_failed")

# =========================
# LOGIN TRADICIONAL 🔑
# =========================

@auth_bp.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    user = User.get_by_email(email)
    if user and user.check_password(password):
        login_user(user)
        registrar_log(f"Inició sesión: {email}")
        return jsonify({
            "mensaje": "Login exitoso",
            "usuario": {"id": user.id, "nombre": user.nombre, "email": user.email, "rol": user.rol}
        })
    
    registrar_log(f"Intento de login fallido: {email}")
    return jsonify({"error": "Credenciales inválidas"}), 401

# =========================
# RECUPERACIÓN DE CLAVE 📧
# =========================

@auth_bp.route("/forgot-password", methods=["POST"])
@limiter.limit("3 per hour")
def forgot_password():
    data = request.get_json()
    email = data.get("email")
    user = User.get_by_email(email)

    if user:
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        token = s.dumps(email, salt='password-reset-salt')
        # URL de tu landing page
        reset_url = f"https://sweetlandbyanny.vercel.app/reset-password.html?token={token}"

        msg = Message("Recuperación de Contraseña - Precivox", recipients=[email])
        msg.body = f"Hola {user.nombre},\n\nPara restablecer tu clave haz clic aquí:\n{reset_url}\n\nEl enlace expira en 1 hora."
        try:
            mail.send(msg)
            registrar_log(f"Solicitó recuperación de contraseña: {email}")
        except Exception as e:
            current_app.logger.error(f"Error SMTP: {e}")

    # Seguridad: siempre responder éxito
    return jsonify({"mensaje": "Si el correo está registrado, recibirás un enlace pronto."}), 200

@auth_bp.route("/reset-password-confirm", methods=["POST"])
def reset_password_confirm():
    data = request.get_json()
    token = data.get("token")
    password = data.get("password")

    try:
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        email = s.loads(token, salt='password-reset-salt', max_age=3600)
    except:
        return jsonify({"error": "El enlace ha expirado o es inválido"}), 400

    hashed_pw = generate_password_hash(password)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE usuarios SET password = %s WHERE email = %s", (hashed_pw, email))
    conn.commit()
    cursor.close()
    conn.close()
    
    registrar_log(f"Restableció su contraseña con éxito: {email}")
    return jsonify({"mensaje": "Contraseña actualizada"})

# =========================
# SESIÓN Y ESTADO
# =========================

@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    registrar_log(f"Cerró sesión")
    logout_user()
    return jsonify({"mensaje": "Sesión cerrada"})

@auth_bp.route("/me", methods=["GET"])
@login_required
def get_current_user():
    return jsonify({
        "usuario": {
            "id": current_user.id, "nombre": current_user.nombre, 
            "email": current_user.email, "rol": current_user.rol
        }
    })