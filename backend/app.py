from flask import Flask, jsonify, request, send_from_directory, redirect
from flask_cors import CORS
from flask_login import LoginManager
from dotenv import load_dotenv
import os

# Importamos las extensiones centralizadas
from extensions import mysql, mail, limiter

load_dotenv()

app = Flask(__name__)

# --- CONFIGURACIÓN DE SEGURIDAD ---
app.secret_key = os.getenv('SECRET_KEY', 'super_clave_secreta_sweetland_2026')

app.config.update(
    SESSION_COOKIE_SAMESITE='None',
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    # Configuración de Email (SMTP Google)
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
    MAIL_DEFAULT_SENDER=os.getenv('MAIL_DEFAULT_SENDER')
)

# --- INICIALIZAR EXTENSIONES ---
mysql.init_app(app)
mail.init_app(app)
limiter.init_app(app)

# --- CORS DINÁMICO ---
allowed_origins = os.getenv('ALLOWED_ORIGINS', '').split(',')
if not allowed_origins or allowed_origins == ['']:
    allowed_origins = ["https://sweetland-by-anny.vercel.app", "https://sweetlandbyanny.vercel.app"]

CORS(app, origins=allowed_origins, supports_credentials=True)

@app.before_request
def force_https():
    if os.getenv('FLASK_ENV') == 'production' and not request.is_secure:
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, code=301)

# --- MANEJADORES DE ERRORES (Ciberseguridad) ---
@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({"error": "Demasiados intentos", "mensaje": "Por seguridad, espera un momento antes de reintentar."}), 429

@app.errorhandler(500)
def internal_error(e):
    # Logueamos el error real internamente, pero al usuario le damos un mensaje genérico
    app.logger.error(f"Error 500: {str(e)}")
    return jsonify({"error": "Error interno", "mensaje": "Estamos trabajando en ello."}), 500

# --- FLASK LOGIN ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth_bp.login"

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.get_by_id(user_id)

@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({"error": "No autorizado"}), 401

# --- REGISTRO DE BLUEPRINTS ---
from login import auth_bp
from usuarios import usuarios_bp
from productos import productos_bp
from pedidos import pedidos_bp
from detalle_pedidos import detalle_pedidos_bp
from ingredientes import ingredientes_bp
from recetas import recetas_bp
from empaques import empaques_bp

app.register_blueprint(auth_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(productos_bp)
app.register_blueprint(pedidos_bp)
app.register_blueprint(detalle_pedidos_bp)
app.register_blueprint(ingredientes_bp)
app.register_blueprint(recetas_bp)
app.register_blueprint(empaques_bp)

@app.route("/")
def index():
    return jsonify({"mensaje": "Backend Sweetland funcionando ✅", "security": "Rate Limiting Active"})

@app.route('/static/images/<path:filename>')
def serve_image(filename):
    image_dir = os.path.join(app.root_path, 'static', 'images')
    return send_from_directory(image_dir, filename)

@app.after_request
def add_header(response):
    # Esto le dice al navegador: "No guardes caché de mis respuestas de la API"
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

if __name__ == "__main__":
    os.makedirs(os.path.join(app.root_path, 'static', 'images'), exist_ok=True)
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)