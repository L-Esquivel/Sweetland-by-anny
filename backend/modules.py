from flask import Blueprint, jsonify, current_app
from flask_login import login_required
from db import get_db
from psycopg2.extras import DictCursor
from utils import superadmin_required

modules_bp = Blueprint("modules_bp", __name__, url_prefix="/modules")

@modules_bp.route("/", methods=["GET"])
@login_required
@superadmin_required
def get_all_modules():
    """
    Devuelve una lista de todos los módulos configurables en la plataforma.
    """
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("SELECT module_key, label, icon, description FROM modules ORDER BY label")
            modules = cursor.fetchall()
            return jsonify(modules)
    except Exception as e:
        current_app.logger.error(f"Error en get_all_modules: {e}")
        return jsonify({"error": "Error al obtener la lista de módulos"}), 500