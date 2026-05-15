from flask import Flask, jsonify, request, send_from_directory, redirect
from flask_cors import CORS
from flask_login import LoginManager
from dotenv import load_dotenv
import os
import re
from werkzeug.middleware.proxy_fix import ProxyFix

# 1. 🟢 Import the new DB manager and other extensions
import db
from extensions import limiter
# Import auth blueprint and OAuth initialization function
from login import auth_bp, init_oauth

load_dotenv()

app = Flask(__name__)

# ==========================================
# 🛠️ ROUTING WORKAROUNDS
# ==========================================
class FixPathMiddleware:
    """
    Middleware that intercepts requests at the WSGI level to fix
    malformed URLs (e.g., with double slashes) BEFORE the Flask router
    processes them and potentially issues an unwanted redirect.
    """
    def __init__(self, app):
        self.app = app
    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO', '')
        if '//' in path:
            environ['PATH_INFO'] = re.sub('/+', '/', path)
        return self.app(environ, start_response)

# ==========================================
# ️ SECURITY AND SESSION CONFIGURATION
# ==========================================
app.secret_key = os.getenv('SECRET_KEY', 'a-super-secret-key-for-development')

app.config.update(
    SESSION_COOKIE_SAMESITE='None',
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    REMEMBER_COOKIE_SAMESITE='None',
    REMEMBER_COOKIE_SECURE=True,
    REMEMBER_COOKIE_HTTPONLY=True
)

# ==========================================
# 🗄️ DATABASE CONFIGURATION
# ==========================================
# 🔴 Database configuration is now managed by the DATABASE_URL variable in the .env file

# ==========================================
# 🚀 MIDDLEWARE AND EXTENSIONS INITIALIZATION
# ==========================================

# ==========================================
# 🚀 EXTENSIONS INITIALIZATION
# ==========================================
db.init_app(app) # 2. 🟢 Initialize the new PostgreSQL database manager
# Disable strict slashes rule at the end of the URL (e.g., /gastos and /gastos/ are the same).
# This makes the API more tolerant to frontend errors.
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
# Apply our middleware to clean up URLs
app.wsgi_app = FixPathMiddleware(app.wsgi_app)

app.url_map.strict_slashes = False

limiter.init_app(app)
# Initialize OAuth for Google Login
init_oauth(app)

# --- DYNAMIC CORS ---
allowed_origins = os.getenv('ALLOWED_ORIGINS', '').split(',')
if not allowed_origins or allowed_origins == ['']:
    # 💡 IMPROVEMENT: Robust fallback list for production and local development.
    allowed_origins = [
        "https://precivox.vercel.app",          # Main domain for the admin panel
        "https://sweetlandbyanny.vercel.app", # Landing page domain
        "http://localhost:5173",                # For local development of the admin panel
        "http://127.0.0.1:5173"                 # Alternative for local development
    ]

CORS(app, origins=allowed_origins, supports_credentials=True)

# ==========================================
# 🛡️ ERROR HANDLERS (SANITIZATION)
# ==========================================
@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({"error": "Too many requests", "message": "For security reasons, please wait a moment before trying again."}), 429

@app.errorhandler(500)
def internal_error(e):
    app.logger.error(f"500 Error: {str(e)}")
    return jsonify({"error": "Internal Server Error", "message": "We are working to fix it quickly."}), 500

# ==========================================
# 👤 FLASK-LOGIN CONFIGURATION
# ==========================================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth_bp.login"

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.get_by_id(user_id)

@login_manager.unauthorized_handler
def unauthorized():
    # FIX: Handle OPTIONS requests for unauthorized access to prevent CORS preflight errors.
    # This ensures that preflight requests always receive a 200 OK, even if the user is not authenticated.
    # Flask-CORS will then add the necessary headers.
    if request.method == 'OPTIONS':
        return jsonify(success=True), 200 # Allow preflight requests
    return jsonify({"error": "Unauthorized", "message": "You must be logged in to perform this action."}), 401

# ==========================================
# 📦 BLUEPRINT REGISTRATION
# ==========================================
from usuarios import usuarios_bp
from productos import productos_bp
from pedidos import pedidos_bp
from detalle_pedidos import detalle_pedidos_bp
from ingredientes import ingredientes_bp
from recetas import recetas_bp
from empaques import empaques_bp
from gastos import gastos_bp
from merma import merma_bp
from tenants import tenants_bp
from platform_api import platform_bp # Corrected import
from modules import modules_bp      # Added missing import
from payments import payments_bp

app.register_blueprint(auth_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(productos_bp)
app.register_blueprint(pedidos_bp)
app.register_blueprint(detalle_pedidos_bp)
app.register_blueprint(ingredientes_bp)
app.register_blueprint(recetas_bp)
app.register_blueprint(empaques_bp)
app.register_blueprint(gastos_bp)
app.register_blueprint(merma_bp)
app.register_blueprint(tenants_bp)
app.register_blueprint(platform_bp)
app.register_blueprint(modules_bp)
app.register_blueprint(payments_bp)

# ==========================================
# 🌍 FILE AND STATUS ROUTES
# ==========================================
@app.route("/")
def index():
    return jsonify({
        "message": "Precivox Backend is running ✅",
        "security": "Rate Limiting & OAuth Active",
        "env": os.getenv('FLASK_ENV', 'development')
    })

@app.route('/static/images/<path:filename>')
def serve_image(filename):
    image_dir = os.path.join(app.root_path, 'static', 'images')
    return send_from_directory(image_dir, filename)

@app.after_request
def add_header(response):
    # Disable cache to prevent stale data in the Dashboard and My Account
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

if __name__ == "__main__":
    # Ensure the images folder exists
    os.makedirs(os.path.join(app.root_path, 'static', 'images'), exist_ok=True)
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)