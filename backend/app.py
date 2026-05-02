from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_login import LoginManager
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'super_clave_secreta_sweetland_2026')

# ───────────────────────────────────────────────
# CORS: en producción restringe a tu dominio real
# ───────────────────────────────────────────────
allowed_origins = os.getenv('ALLOWED_ORIGINS', '*')
if allowed_origins != '*':
    allowed_origins = [o.strip() for o in allowed_origins.split(',')]

CORS(app, origins=allowed_origins, supports_credentials=True)

# ───────────────────────────────────────────────
# Flask-Login
# ───────────────────────────────────────────────
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth_bp.login"

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.get_by_id(user_id)

# ───────────────────────────────────────────────
# Inicializar extensiones (cierra conexiones automáticamente)
# ───────────────────────────────────────────────
from extensions import mysql
mysql.init_app(app)

# ───────────────────────────────────────────────
# Blueprints
# ───────────────────────────────────────────────
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

# ───────────────────────────────────────────────
# Rutas base
# ───────────────────────────────────────────────
@app.route("/")
def index():
    return jsonify({"mensaje": "Backend Sweetland funcionando correctamente ✅"})

@app.route('/static/images/<filename>')
def serve_image(filename):
    """Sirve imágenes de productos desde shared-assets."""
    image_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'shared-assets', 'images')
    return send_from_directory(image_dir, filename)

# ───────────────────────────────────────────────
# Health check para Railway
# ───────────────────────────────────────────────
@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

# ───────────────────────────────────────────────
# Entry point (solo para desarrollo local)
# ───────────────────────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=False)