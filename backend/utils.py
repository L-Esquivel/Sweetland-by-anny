from functools import wraps
from flask import jsonify, request
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 🛡️ CIBERSEGURIDAD: Permitir siempre las peticiones OPTIONS (Preflight)
        if request.method == 'OPTIONS':
            return f(*args, **kwargs)
            
        # Verificar autenticación y rol (Case-insensitive y limpio)
        if not current_user.is_authenticated:
            return jsonify({"error": "No autenticado"}), 401
            
        user_role = str(current_user.rol).lower().strip() if current_user.rol else ""
        if user_role != 'admin':
            return jsonify({"error": "Acceso denegado. Se requiere rol de administrador."}), 403
            
        return f(*args, **kwargs)
    return decorated_function