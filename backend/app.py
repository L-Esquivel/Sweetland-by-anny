from flask import Flask, jsonify, request, send_from_directory, redirect
from flask_cors import CORS
from flask_login import LoginManager
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'super_clave_secreta_sweetland_2026')

# Force HTTPS fuerte (al principio)
@app.before_request
def force_https():
    if os.getenv('FLASK_ENV') == 'production' and not request.is_secure:
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, code=301)

# Configuración de cookies
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['REMEMBER_COOKIE_SAMESITE'] = 'None'
app.config['REMEMBER_COOKIE_SECURE'] = True

# MySQL config
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', 'Root1234')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'sweetland_by_anny')
app.config['MYSQL_PORT'] = int(os.getenv('MYSQL_PORT', 3306))

from extensions import mysql
mysql.init_app(app)

# CORS
CORS(app, origins=["https://sweetland-by-anny.vercel.app", "*"], supports_credentials=True)

# Preflight
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

# Flask-Login
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

# Blueprints
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
    return jsonify({"mensaje": "Backend Sweetland funcionando correctamente ✅"})

@app.route('/static/images/<filename>')
def serve_image(filename):
    image_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'shared-assets', 'images')
    return send_from_directory(image_dir, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=False)