from flask import Flask, jsonify, request, send_from_directory, redirect
from flask_cors import CORS
from flask_login import LoginManager
from dotenv import load_dotenv
import os
from werkzeug.middleware.proxy_fix import ProxyFix

# Importamos las extensiones centralizadas
from extensions import mysql, mail, limiter
# Importamos el Blueprint de auth y la función de inicialización de OAuth
from login import auth_bp, init_oauth

load_dotenv()

app = Flask(__name__)

app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# ==========================================
# 🛡️ CONFIGURACIÓN DE SEGURIDAD Y SESIONES
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

# # ==========================================
# 📧 CONFIGURACIÓN DE CORREO (SMTP GOOGLE SSL)
# ==========================================
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=int(os.getenv('MAIL_PORT', 587)),
    MAIL_USE_TLS=os.getenv('MAIL_USE_TLS', 'True').lower() == 'true',
    MAIL_USE_SSL=os.getenv('MAIL_USE_SSL', 'False').lower() == 'true',
    MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
    MAIL_DEFAULT_SENDER=os.getenv('MAIL_DEFAULT_SENDER')
)

# ==========================================
# 🗄️ CONFIGURACIÓN DE BASE DE DATOS
# ==========================================
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
app.config['MYSQL_PORT'] = int(os.getenv('MYSQL_PORT') or 3306)

# ==========================================
# 🚀 INICIALIZACIÓN DE EXTENSIONES
# ==========================================
mysql.init_app(app)
mail.init_app(app)
limiter.init_app(app)
# Inicializamos OAuth para Google Login
init_oauth(app)

# --- CORS DINÁMICO ---
allowed_origins = os.getenv('ALLOWED_ORIGINS', '').split(',')
if not allowed_origins or allowed_origins == ['']:
    allowed_origins = ["https://sweetland-by-anny.vercel.app", "https://sweetlandbyanny.vercel.app"]

CORS(app, origins=allowed_origins, supports_credentials=True)

# Forzar HTTPS en producción
@app.before_request
def force_https():
    if os.getenv('FLASK_ENV') == 'production' and not request.is_secure:
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, code=301)

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
    return jsonify({"error": "No autorizado", "mensaje": "Debes iniciar sesión para realizar esta acción."}), 401
    # 🕵️‍♂️ INICIO: LOGGING DE DIAGNÓSTICO TEMPORAL
    # Este bloque nos ayudará a cazar el bug del 401 intermitente.
    # Registraremos las cabeceras para ver si el proxy está funcionando bien.
    app.logger.warning(f"===== UNAUTHORIZED_HANDLER_DEBUG =====")
    app.logger.warning(f"Request URL: {request.url}")
    app.logger.warning(f"Request is_secure: {request.is_secure}")
    app.logger.warning(f"Request Headers: {request.headers}")
    app.logger.warning(f"======================================")
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