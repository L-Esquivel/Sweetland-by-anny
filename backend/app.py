from flask import Flask, jsonify, request, send_from_directory, redirect
from flask_cors import CORS
from flask_login import LoginManager
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'super_clave_secreta_sweetland_2026')

# --- 1. CONFIGURACIÓN DE CORS DINÁMICO ---
# Leemos los orígenes permitidos de la variable de entorno que configuraste en Railway
allowed_origins = os.getenv('ALLOWED_ORIGINS', '').split(',')
if not allowed_origins or allowed_origins == ['']:
    allowed_origins = ["https://sweetland-by-anny.vercel.app", "https://sweetlandbyanny.vercel.app"]

CORS(app, origins=allowed_origins, supports_credentials=True)

# --- 2. CONFIGURACIÓN DE COOKIES Y SEGURIDAD ---
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True

@app.before_request
def force_https():
    if os.getenv('FLASK_ENV') == 'production' and not request.is_secure:
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, code=301)

# --- 3. CONFIGURACIÓN DE BASE DE DATOS ---
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', 'Root1234')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'sweetland_by_anny')
app.config['MYSQL_PORT'] = int(os.getenv('MYSQL_PORT', 3306))

from extensions import mysql
mysql.init_app(app)

# --- 4. MANEJO DE SESIONES (Flask-Login) ---
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

# --- 5. REGISTRO DE BLUEPRINTS ---
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

# --- 6. RUTAS DE ARCHIVOS ESTÁTICOS E ÍNDICE ---

@app.route("/")
def index():
    return jsonify({
        "mensaje": "Backend Sweetland funcionando correctamente ✅",
        "servidor": "Railway Production"
    })

# RUTA CORREGIDA PARA IMÁGENES
# Busca la carpeta 'static/images' dentro de la carpeta del backend
@app.route('/static/images/<path:filename>')
def serve_image(filename):
    # Usamos app.root_path para asegurar que busque dentro de la carpeta del proyecto
    image_dir = os.path.join(app.root_path, 'static', 'images')
    return send_from_directory(image_dir, filename)

# === RUTA TEMPORAL DE MANTENIMIENTO (BORRAR DESPUÉS DE USAR) ===
@app.route("/ejecutar-gran-reset-2026")
def trigger_reset():
    from reset_db import reset_database
    try:
        reset_database()
        return "✅ Base de datos reseteada con éxito. ELIMINA ESTE CÓDIGO AHORA."
    except Exception as e:
        return f"❌ Error: {str(e)}"

if __name__ == "__main__":
    # Asegurar que la carpeta static/images exista al arrancar
    os.makedirs(os.path.join(app.root_path, 'static', 'images'), exist_ok=True)
    
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)