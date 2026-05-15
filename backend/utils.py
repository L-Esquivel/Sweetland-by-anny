from functools import wraps
from flask import jsonify, request, current_app
from flask_login import current_user
from db import get_db # 🟢 Importamos el nuevo gestor de DB

# --- 1. ROLE DECORATORS ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # FIX: For a preflight OPTIONS request, we must return an OK response
        # immediately without executing the function body. Flask-CORS will
        # handle adding the necessary headers. Executing the body would cause
        # errors, as OPTIONS requests do not have a JSON payload.
        if request.method == 'OPTIONS':
            return jsonify(success=True), 200
        if not current_user.is_authenticated:
            return jsonify({"error": "Not authenticated"}), 401
        user_role = str(current_user.rol).lower().strip() if current_user.rol else ""
        # 💡 IMPROVEMENT: A superadmin also has admin permissions.
        if user_role not in ('admin', 'superadmin'):
            return jsonify({"error": "Access denied"}), 403
        return f(*args, **kwargs)
    return decorated_function

def superadmin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # FIX: Same correction as in admin_required for CORS preflight requests.
        if request.method == 'OPTIONS':
            return jsonify(success=True), 200
        if not current_user.is_authenticated:
            return jsonify({"error": "Not authenticated"}), 401
        user_role = str(current_user.rol).lower().strip() if current_user.rol else ""
        if user_role != 'superadmin':
            return jsonify({"error": "Superadmin access required"}), 403
        return f(*args, **kwargs)
    return decorated_function

# --- 2. AUDIT LOG FUNCTION 🛡️ ---
def register_log(action):
    """
    Saves an activity record to the 'logs' table.
    """
    try:
        user_id = None
        tenant_id = None
        
        # If the user is logged in, get their data
        if current_user.is_authenticated:
            user_id = current_user.id
            tenant_id = current_user.tenant_id

        conn = get_db()
        with conn.cursor() as cursor:
            # The new 'logs' table has a simpler structure.
            cursor.execute("""
                INSERT INTO logs (usuario_id, accion, tenant_id)
                VALUES (%s, %s, %s)
            """, (user_id, action, tenant_id))
            conn.commit()

    except Exception as e:
        # Use the application logger for consistent error logging.
        current_app.logger.error(f"⚠️ Security Alert: Could not write to Log: {e}")