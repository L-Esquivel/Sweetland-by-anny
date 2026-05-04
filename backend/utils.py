from functools import wraps
from flask import jsonify
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Si no está logueado o el rol no es admin, bloqueamos
        if not current_user.is_authenticated or current_user.rol != 'admin':
            return jsonify({"error": "Acceso denegado. Se requieren permisos de administrador."}), 403
        return f(*args, **kwargs)
    return decorated_function