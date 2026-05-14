from flask import Blueprint, request, jsonify, current_app, url_for, redirect
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from models import User
from extensions import limiter
from backend.db import get_db # 🟢 Importamos el nuevo gestor de DB
from psycopg2.extras import DictCursor # 🟢 Para obtener resultados como diccionarios
from utils import registrar_log
from authlib.integrations.flask_client import OAuth
import os
import threading
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail as SendGridMail

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

        conn = get_db()
        try:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
                user_row = cursor.fetchone()

                if user_row:
                    # Si el usuario ya existe, lo cargamos con todos sus datos
                    usuario = User.get_by_id(user_row["id_usuario"])
                    login_user(usuario)
                    registrar_log(f"Inició sesión vía Google: {email}")
                else:
                    # 💡 SAAS-IFICATION: Los nuevos registros de Google se asocian al tenant público (1).
                    tenant_id_publico = 1
                    cursor.execute("""
                        INSERT INTO usuarios (nombre, email, rol, google_id, tenant_id)
                        VALUES (%s, %s, 'cliente', %s, %s)
                        RETURNING id_usuario
                    """, (nombre, email, google_id, tenant_id_publico))
                    new_id = cursor.fetchone()[0]
                    conn.commit()
                    
                    # Cargamos el nuevo usuario desde la DB para asegurar consistencia
                    usuario = User.get_by_id(new_id)
                    if usuario:
                        login_user(usuario)
                        registrar_log(f"Nuevo registro vía Google: {email}")

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

            # 🚀 SOLUCIÓN TÉCNICA: Usar un servicio de email transaccional (SendGrid) en un hilo separado.
            # Esto evita bloqueos de red en plataformas como Railway y es la práctica recomendada.
            def send_async_email_sendgrid(app, recipient, user_nombre, url_reseteo):
                with app.app_context():
                    # Aquí podrías usar una plantilla HTML para un correo más profesional
                    body = f"Hola {user_nombre},\n\nPara restablecer tu clave haz clic aquí:\n{url_reseteo}\n\nEl enlace expira en 1 hora."
                    # 💡 MEJORA: Usar una plantilla HTML para un correo más profesional y con mejor entregabilidad.
                    html_content = f"""
                    <div style="font-family: sans-serif; padding: 20px; background-color: #f4f4f4;">
                        <div style="max-width: 600px; margin: auto; background-color: white; padding: 30px; border-radius: 10px;">
                            <h2 style="color: #333;">Recuperación de Contraseña</h2>
                            <p>Hola {user_nombre},</p>
                            <p>Hemos recibido una solicitud para restablecer la contraseña de tu cuenta. Haz clic en el siguiente botón para continuar:</p>
                            <a href="{url_reseteo}" style="display: inline-block; padding: 12px 25px; margin: 20px 0; background-color: #aa1d80; color: white; text-decoration: none; border-radius: 5px;">
                                Restablecer Contraseña
                            </a>
                            <p>Si no solicitaste esto, puedes ignorar este correo de forma segura.</p>
                            <hr style="border: none; border-top: 1px solid #eee; margin-top: 20px;">
                            <p style="font-size: 0.8em; color: #999;">El enlace expirará en 1 hora.</p>
                        </div>
                    </div>
                    """
                    message = SendGridMail(
                        from_email=os.getenv('SENDER_EMAIL'),
                        to_emails=recipient,
                        subject="Recuperación de Contraseña - Precivox",
                        plain_text_content=body,
                        html_content=html_content)
                    try:
                        sendgrid_client = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
                        response = sendgrid_client.send(message)
                        app.logger.info(f"✅ HILO: Correo de recuperación enviado a {recipient} vía SendGrid. Status: {response.status_code}")
                    except Exception as e:
                        app.logger.error(f"❌ HILO: Error enviando correo vía SendGrid a {recipient}: {e}", exc_info=True)

            thread = threading.Thread(target=send_async_email_sendgrid, args=(current_app._get_current_object(), email, user.nombre, reset_url))
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
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE usuarios SET password = %s WHERE email = %s", (hashed_pw, email))
            conn.commit()
            registrar_log(f"Restableció su contraseña con éxito: {email}")
            return jsonify({"mensaje": "Contraseña actualizada"})
    except Exception as e:
        conn.rollback()
        return jsonify({"error": "Error al actualizar la contraseña"}), 500

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

    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id_usuario FROM usuarios WHERE email = %s", (email,))
            if cursor.fetchone():
                return jsonify({"error": "Email ya registrado"}), 400
            
            # 💡 SAAS-IFICATION: Los nuevos registros de clientes se asocian al tenant público (1).
            tenant_id_publico = 1
            hashed = generate_password_hash(password)
            cursor.execute("""
                INSERT INTO usuarios (nombre, email, password, telefono, direccion, rol, tenant_id)
                VALUES (%s, %s, %s, %s, %s, 'cliente', %s)
            """, (nombre, email, hashed, data.get("telefono"), data.get("direccion"), tenant_id_publico))
            conn.commit()
            registrar_log(f"Nuevo cliente registrado: {email}")
            return jsonify({"mensaje": "Registro exitoso"}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

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
            "email": current_user.email, "rol": current_user.rol,
            "telefono": current_user.telefono,
            "direccion": current_user.direccion
        }
    })