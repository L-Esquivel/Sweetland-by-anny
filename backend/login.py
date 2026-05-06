from flask import Blueprint, request, jsonify, current_app, url_for, redirect
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from db import get_db_connection
from models import User
from extensions import mail, limiter
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
# Nuevas librerías para OAuth
from authlib.integrations.flask_client import OAuth
import os

auth_bp = Blueprint("auth_bp", __name__, url_prefix="/auth")

# --- CONFIGURACIÓN DE OAUTH ---
oauth = OAuth()
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

# Inicializar oauth con la app (esto se activará mediante app.py que ya lo registra)
def init_oauth(app):
    oauth.init_app(app)

# =========================
# RUTAS DE LOGIN CON GOOGLE 🌍
# =========================

@auth_bp.route("/login/google")
def login_google():
    """Redirige al usuario a Google para autenticarse."""
    # El redirect_uri debe coincidir EXACTAMENTE con lo que pusiste en Google Cloud Console
    redirect_uri = url_for('auth_bp.google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@auth_bp.route("/login/google/callback")
def google_callback():
    """Recibe la respuesta de Google y gestiona el usuario."""
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
        
        # 🔍 Verificar si el usuario ya existe por email
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        user_row = cursor.fetchone()

        if user_row:
            # Si ya existe, lo logueamos directamente
            usuario_logueado = User(
                id=user_row["id_usuario"],
                nombre=user_row["nombre"],
                email=user_row["email"],
                password=user_row["password"],
                rol=user_row["rol"]
            )
            login_user(usuario_logueado)
        else:
            # ✨ SI ES NUEVO: Lo creamos como 'cliente' automáticamente
            # Importante: google_id nos sirve para identificar que no tiene password manual
            cursor.execute("""
                INSERT INTO usuarios (nombre, email, rol, google_id, fecha_registro)
                VALUES (%s, %s, 'cliente', %s, NOW())
            """, (nombre, email, google_id))
            conn.commit()
            
            new_id = cursor.lastrowid
            usuario_nuevo = User(id=new_id, nombre=nombre, email=email, password=None, rol='cliente')
            login_user(usuario_nuevo)

        cursor.close()
        conn.close()

        # Redirigir al cliente a su cuenta en el Landing Page
        return redirect("https://sweetlandbyanny.vercel.app/mi-cuenta.html")

    except Exception as e:
        current_app.logger.error(f"Error en Google Auth: {str(e)}")
        return jsonify({"error": "Fallo en la autenticación con Google"}), 500

# =========================
# RUTAS DE LOGIN TRADICIONAL
# =========================

@auth_bp.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
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

# ... [Mantenemos igual tus rutas de forgot-password, logout y me] ...

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