from flask import Flask, jsonify, request, send_from_directory, redirect
from flask_cors import CORS
from flask_login import LoginManager
from dotenv import load_dotenv
import os
import re
from werkzeug.middleware.proxy_fix import ProxyFix

# 1. 🟢 Importamos el nuevo gestor de DB y las otras extensiones
import db
from extensions import limiter
# Importamos el Blueprint de auth y la función de inicialización de OAuth
from login import auth_bp, init_oauth

load_dotenv()

app = Flask(__name__)

app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# ==========================================
# 🛠️ WORKAROUNDS DE ENRUTAMIENTO
# ==========================================
@app.before_request
def fix_path():
    """
    Soluciona URLs malformadas enviadas por el cliente.
    1. Reemplaza múltiples barras (//) por una sola (/).
    """
    if '//' in request.path:
        new_path = re.sub('/+', '/', request.path)
        request.environ['PATH_INFO'] = new_path

# ==========================================
# �️ CONFIGURACIÓN DE SEGURIDAD Y SESIONES
# ==========================================
app.secret_key = os.getenv('SECRET_KEY', 'super_clave_secreta_sweetland_2026')

app.config.update(
    SESSION_COOKIE_SAMESITE='None',
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    REMEMBER_COOKIE_SAMESITE='None',
    REMEMBER_COOKIE_SECURE=True,
    REMEMBER_COOKIE_HTTPONLY=True
)

# ==========================================
# 🗄️ CONFIGURACIÓN DE BASE DE DATOS
# ==========================================
# 🔴 La configuración de la base de datos ahora se gestiona con la variable DATABASE_URL en el archivo .env

# ==========================================
# 🚀 INICIALIZACIÓN DE EXTENSIONES
# ==========================================
db.init_app(app) # 2. 🟢 Inicializamos el nuevo gestor de base de datos PostgreSQL
# 2. Desactivamos la regla estricta de barras al final de la URL (ej: /gastos y /gastos/ son iguales)
# Esto hace la API más tolerante a errores del frontend.
app.url_map.strict_slashes = False

limiter.init_app(app)
# Inicializamos OAuth para Google Login
init_oauth(app)

# --- CORS DINÁMICO ---
allowed_origins = os.getenv('ALLOWED_ORIGINS', '').split(',')
if not allowed_origins or allowed_origins == ['']:
    # 💡 MEJORA: Lista de fallback robusta para producción y desarrollo local.
    allowed_origins = [
        "https://precivox.vercel.app",          # Dominio principal del panel de admin
        "https://sweetlandbyanny.vercel.app", # Dominio de la landing page
        "http://localhost:5173",                # Para desarrollo local del panel de admin
        "http://127.0.0.1:5173"                 # Alternativa para desarrollo local
    ]

CORS(app, origins=allowed_origins, supports_credentials=True)

# ==========================================
# 🛡️ MANEJADORES DE ERRORES (SANITIZACIÓN)
# ==========================================
@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({"error": "Demasiados intentos", "mensaje": "Por seguridad, espera un momento antes de reintentar."}), 429

@app.errorhandler(500)
def internal_error(e):
    app.logger.error(f"Error 500: {str(e)}")
    return jsonify({"error": "Error interno", "mensaje": "Estamos trabajando para solucionarlo rápidamente."}), 500

# ==========================================
# 👤 CONFIGURACIÓN DE FLASK-LOGIN
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
        return jsonify(success=True), 200
    return jsonify({"error": "No autorizado", "mensaje": "Debes iniciar sesión para realizar esta acción."}), 401

# ==========================================
# 📦 REGISTRO DE BLUEPRINTS
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

# ==========================================
# 🌍 RUTAS DE ARCHIVOS Y ESTADO
# ==========================================
@app.route("/")
def index():
    return jsonify({
        "mensaje": "Precivox Backend funcionando ✅",
        "security": "Rate Limiting & OAuth Active",
        "env": os.getenv('FLASK_ENV', 'development')
    })

@app.route('/static/images/<path:filename>')
def serve_image(filename):
    image_dir = os.path.join(app.root_path, 'static', 'images')
    return send_from_directory(image_dir, filename)

@app.after_request
def add_header(response):
    # Desactivar caché para evitar datos desactualizados en el Dashboard y Mi Cuenta
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

if __name__ == "__main__":
    # Asegurar que la carpeta de imágenes exista
    os.makedirs(os.path.join(app.root_path, 'static', 'images'), exist_ok=True)
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)