from flask import Blueprint, request, jsonify, current_app, url_for, redirect
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from models import User
from extensions import limiter
from db import get_db # 🟢 Import the new DB manager
from psycopg2.extras import DictCursor # 🟢 To get results as dictionaries
from utils import register_log
from authlib.integrations.flask_client import OAuth
from itsdangerous import URLSafeTimedSerializer
import os
import threading
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail as SendGridMail

auth_bp = Blueprint("auth_bp", __name__, url_prefix="/auth")

# --- OAUTH CONFIGURATION ---
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
# GOOGLE LOGIN 🌍
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
            return jsonify({"error": "Could not retrieve user information from Google"}), 400

        email = user_info['email']
        nombre = user_info['name']
        google_id = user_info['sub']

        conn = get_db()
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
            user_row = cursor.fetchone()

            if user_row:
                # If the user already exists, load them with all their data
                usuario = User.get_by_id(user_row["id_usuario"])
                login_user(usuario)
                register_log(f"Logged in via Google: {email}")
            else:
                # 💡 SAAS-IFICATION: New Google sign-ups are associated with the public tenant (1).
                tenant_id_publico = os.getenv('PUBLIC_TENANT_ID', 1)
                cursor.execute("""
                    INSERT INTO usuarios (nombre, email, rol, google_id, tenant_id)
                    VALUES (%s, %s, 'cliente', %s, %s)
                    RETURNING id_usuario
                """, (nombre, email, google_id, tenant_id_publico))
                new_id = cursor.fetchone()[0]
                conn.commit()
                
                # Load the new user from the DB to ensure consistency
                usuario = User.get_by_id(new_id)
                if usuario:
                    login_user(usuario)
                    register_log(f"New user registered via Google: {email}")

            # 💡 IMPROVEMENT: Use an environment variable for the frontend URL.
            frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
            return redirect(f"{frontend_url}/mi-cuenta.html")
    except Exception as e:
        current_app.logger.error(f"Error en Google Auth: {e}", exc_info=True)
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
        return redirect(f"{frontend_url}/mi-cuenta.html?error=auth_failed") # Redirect with an error query param

# =========================
# TRADITIONAL LOGIN 🔑
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
        register_log(f"Logged in: {email}")
        return jsonify({
            "message": "Login successful",
            "usuario": {
                "id": user.id, "nombre": user.nombre, 
                "email": user.email, "rol": user.rol,
                # 💡 IMPROVEMENT: Return the complete module configuration.
                "module_settings": user.module_settings 
            }
        })
    
    register_log(f"Failed login attempt for: {email}")
    return jsonify({"error": "Invalid credentials"}), 401

# =========================
# PASSWORD RECOVERY 📧
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
            s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
            token = s.dumps(email, salt='password-reset-salt')
            # 💡 IMPROVEMENT: Use an environment variable for the frontend URL.
            frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
            reset_url = f"{frontend_url}/reset-password.html?token={token}"

            # 🚀 TECHNICAL SOLUTION: Use a transactional email service (SendGrid) in a separate thread.
            # This avoids network blocking on platforms like Railway and is the recommended practice.
            def send_async_email_sendgrid(app, recipient, user_nombre, url_reseteo):
                with app.app_context():
                    body = f"Hi {user_nombre},\n\nTo reset your password, click here:\n{url_reseteo}\n\nThe link will expire in 1 hour."
                    # 💡 IMPROVEMENT: Use an HTML template for a more professional and deliverable email.
                    html_content = f"""
                    <div style="font-family: sans-serif; padding: 20px; background-color: #f4f4f4;">
                        <div style="max-width: 600px; margin: auto; background-color: white; padding: 30px; border-radius: 10px;">
                            <h2 style="color: #333;">Password Recovery</h2>
                            <p>Hi {user_nombre},</p>
                            <p>We received a request to reset your account password. Click the button below to continue:</p>
                            <a href="{url_reseteo}" style="display: inline-block; padding: 12px 25px; margin: 20px 0; background-color: #aa1d80; color: white; text-decoration: none; border-radius: 5px;">
                                Reset Password
                            </a>
                            <p>If you did not request this, you can safely ignore this email.</p>
                            <hr style="border: none; border-top: 1px solid #eee; margin-top: 20px;">
                            <p style="font-size: 0.8em; color: #999;">The link will expire in 1 hour.</p>
                        </div>
                    </div>
                    """
                    message = SendGridMail(
                        from_email=os.getenv('SENDER_EMAIL'),
                        to_emails=recipient,
                        subject="Password Recovery - Precivox",
                        plain_text_content=body,
                        html_content=html_content)
                    try:
                        sendgrid_client = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
                        response = sendgrid_client.send(message)
                        app.logger.info(f"✅ THREAD: Recovery email sent to {recipient} via SendGrid. Status: {response.status_code}")
                    except Exception as e:
                        app.logger.error(f"❌ THREAD: Error sending email via SendGrid to {recipient}: {e}", exc_info=True)

            thread = threading.Thread(target=send_async_email_sendgrid, args=(current_app._get_current_object(), email, user.nombre, reset_url))
            thread.start()
            
            register_log(f"Password recovery requested (process initiated) for: {email}")

        # English comment: Always return a generic success message.
        # This prevents user enumeration attacks, as the response is the same whether the user
        # exists, is an admin, or doesn't exist at all.
        return jsonify({"message": "If the email is registered, you will receive a link shortly."}), 200

    except Exception as e:
        current_app.logger.error(f"❌ GENERAL ERROR in forgot-password: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route("/reset-password-confirm", methods=["POST"])
def reset_password_confirm():
    data = request.get_json()
    token = data.get("token")
    password = data.get("password")

    try:
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        email = s.loads(token, salt='password-reset-salt', max_age=3600)
    except:
        return jsonify({"error": "The link has expired or is invalid"}), 400

    hashed_pw = generate_password_hash(password)
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE usuarios SET password = %s WHERE email = %s", (hashed_pw, email))
            conn.commit()
            register_log(f"Successfully reset password for: {email}")
            return jsonify({"message": "Password updated successfully"})
    except Exception as e:
        conn.rollback()
        return jsonify({"error": "Error updating password"}), 500

# =========================
# PUBLIC LOGIN/REGISTRATION (CUSTOMERS) 🙋‍♀️
# =========================

@auth_bp.route("/public/login", methods=["POST"])
def login_cliente():
    data = request.get_json()
    user = User.get_by_email(data.get("email"))
    
    # English comment: Verify user exists, password is correct, and role is 'cliente'.
    if user and user.check_password(data.get("password")) and user.rol == 'cliente':
        login_user(user)
        register_log(f"Customer logged in: {user.email}")
        return jsonify({"usuario": {"id": user.id, "nombre": user.nombre, "email": user.email, "telefono": user.telefono, "direccion": user.direccion}})
    
    register_log(f"Failed customer login attempt for: {data.get('email')}")
    return jsonify({"error": "Invalid credentials"}), 401

@auth_bp.route("/public/registro", methods=["POST"])
def registro_cliente():
    data = request.get_json()
    nombre = data.get("nombre")
    email = data.get("email")
    password = data.get("password")

    if not nombre or not email or not password:
        return jsonify({"error": "Name, email, and password are required"}), 400

    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id_usuario FROM usuarios WHERE email = %s", (email,))
            if cursor.fetchone():
                return jsonify({"error": "Email already registered"}), 400
            
            # 💡 SAAS-IFICATION: New customer sign-ups are associated with the public tenant (1).
            tenant_id_publico = os.getenv('PUBLIC_TENANT_ID', 1)
            hashed = generate_password_hash(password)
            cursor.execute("""
                INSERT INTO usuarios (nombre, email, password, telefono, direccion, rol, tenant_id)
                VALUES (%s, %s, %s, %s, %s, 'cliente', %s)
            """, (nombre, email, hashed, data.get("telefono"), data.get("direccion"), tenant_id_publico))
            conn.commit()
            register_log(f"New customer registered: {email}")
            return jsonify({"message": "Registration successful"}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": "An error occurred. The email might already be in use."}), 500

# =========================
# SESIÓN Y ESTADO
# =========================

@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    register_log(f"Logged out")
    logout_user()
    return jsonify({"message": "Session closed"})

@auth_bp.route("/me", methods=["GET"])
@login_required
def get_current_user():
    return jsonify({
        "usuario": {
            "id": current_user.id, "nombre": current_user.nombre, 
            "email": current_user.email, "rol": current_user.rol,
            "telefono": current_user.telefono,
            "direccion": current_user.direccion,
            "module_settings": current_user.module_settings
        }
    })