from flask import Blueprint, request, jsonify, current_app, url_for, redirect
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from models import User
from extensions import mail, limiter, mysql 
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from utils import registrar_log
from authlib.integrations.flask_client import OAuth
import os
import threading

auth_bp = Blueprint("auth_bp", __name__, url_prefix="/auth")

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

        cursor = mysql.connection.cursor()
        try:
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
                mysql.connection.commit()
                new_id = cursor.lastrowid
                usuario = User(id=new_id, nombre=nombre, email=email, password=None, rol='cliente')
                login_user(usuario)
                registrar_log(f"Nuevo registro vía Google: {email}")
            return redirect("https://sweetlandbyanny.vercel.app/mi-cuenta.html")
        finally:
            if cursor: cursor.close()
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
    try:
        data = request.get_json()
        email = data.get("email")
        
        from models import User
        user = User.get_by_email(email)

        # English comment: Security hardening. Only allow password recovery for users with the 'cliente' role.
        # This prevents admins or other privileged roles from using the self-service recovery flow.
        if user and user.rol == 'cliente':
            from itsdangerous import URLSafeTimedSerializer
            
            s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
            token = s.dumps(email, salt='password-reset-salt')
            reset_url = f"https://sweetlandbyanny.vercel.app/reset-password.html?token={token}"

            msg = Message("Recuperación de Contraseña - Precivox",
                          recipients=[email])
            msg.body = f"Hola {user.nombre},\n\nPara restablecer tu clave haz clic aquí:\n{reset_url}\n\nEl enlace expira en 1 hora."
            
            # 🚀 SOLUCIÓN TÉCNICA: Enviar en un hilo separado
            # Esto hace que la función responda al navegador ANTES de intentar conectar con Google
            def send_async_email(app, msg):
                with app.app_context():
                    try:
                        mail.send(msg)
                        app.logger.info(f"✅ HILO: Correo de recuperación enviado a {email}")
                    except Exception as e:
                        app.logger.error(f"❌ HILO: Error enviando correo de recuperación a {email}: {e}", exc_info=True)

            thread = threading.Thread(target=send_async_email, args=(current_app._get_current_object(), msg))
            thread.start()
            
            registrar_log(f"Solicitó recuperación de contraseña (proceso iniciado): {email}")

        # English comment: Always return a generic success message.
        # This prevents user enumeration attacks, as the response is the same whether the user
        # exists, is an admin, or doesn't exist at all.
        return jsonify({"mensaje": "Si el correo está registrado, recibirás un enlace pronto."}), 200

    except Exception as e:
        current_app.logger.error(f"❌ ERROR GENERAL en forgot-password: {e}", exc_info=True)
        return jsonify({"error": "Error interno del servidor"}), 500

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
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("UPDATE usuarios SET password = %s WHERE email = %s", (hashed_pw, email))
        mysql.connection.commit()
        registrar_log(f"Restableció su contraseña con éxito: {email}")
        return jsonify({"mensaje": "Contraseña actualizada"})
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"error": "Error al actualizar la contraseña"}), 500
    finally:
        if cursor: cursor.close()

# =========================
# LOGIN/REGISTRO PÚBLICO (CLIENTES) 🙋‍♀️
# =========================

@auth_bp.route("/public/login", methods=["POST"])
def login_cliente():
    data = request.get_json()
    user = User.get_by_email(data.get("email"))
    
    # English comment: Verify user exists, password is correct, and role is 'cliente'.
    if user and user.check_password(data.get("password")) and user.rol == 'cliente':
        login_user(user)
        registrar_log(f"Cliente inició sesión: {user.email}")
        return jsonify({"usuario": {"id": user.id, "nombre": user.nombre, "email": user.email, "telefono": user.telefono, "direccion": user.direccion}})
    
    registrar_log(f"Intento de login de cliente fallido: {data.get('email')}")
    return jsonify({"error": "Credenciales inválidas"}), 401

@auth_bp.route("/public/registro", methods=["POST"])
def registro_cliente():
    data = request.get_json()
    nombre = data.get("nombre")
    email = data.get("email")
    password = data.get("password")

    if not nombre or not email or not password:
        return jsonify({"error": "Nombre, email y contraseña son obligatorios"}), 400

    cursor = mysql.connection.cursor()
    try:
        cursor.execute("SELECT id_usuario FROM usuarios WHERE email = %s", (email,))
        if cursor.fetchone():
            return jsonify({"error": "Email ya registrado"}), 400
        
        hashed = generate_password_hash(password)
        cursor.execute("""
            INSERT INTO usuarios (nombre, email, password, telefono, direccion, rol, fecha_registro)
            VALUES (%s, %s, %s, %s, %s, 'cliente', NOW())
        """, (nombre, email, hashed, data.get("telefono"), data.get("direccion")))
        mysql.connection.commit()
        registrar_log(f"Nuevo cliente registrado: {email}")
        return jsonify({"mensaje": "Registro exitoso"}), 201
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor: cursor.close()

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