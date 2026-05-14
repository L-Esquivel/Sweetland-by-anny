from functools import wraps
from flask import jsonify, request, current_app
from flask_login import current_user
from db import get_db # 🟢 Importamos el nuevo gestor de DB

# --- 1. DECORADOR ADMIN (Mantenemos la protección de roles) ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'OPTIONS':
            return f(*args, **kwargs)
        if not current_user.is_authenticated:
            return jsonify({"error": "No autenticado"}), 401
        user_role = str(current_user.rol).lower().strip() if current_user.rol else ""
        if user_role != 'admin':
            return jsonify({"error": "Acceso denegado"}), 403
        return f(*args, **kwargs)
    return decorated_function

# --- 2. FUNCIÓN DE REGISTRO DE LOGS 🛡️ ---
def registrar_log(accion):
    """
    Guarda un registro de la actividad en la tabla 'logs'.
    """
    try:
        usuario_id = None
        tenant_id = None
        
        # Si el usuario está logueado, tomamos sus datos
        if current_user.is_authenticated:
            usuario_id = current_user.id
            tenant_id = current_user.tenant_id

        conn = get_db()
        with conn.cursor() as cursor:
            # La nueva tabla 'logs' tiene una estructura más simple.
            cursor.execute("""
                INSERT INTO logs (usuario_id, accion, tenant_id)
                VALUES (%s, %s, %s)
            """, (usuario_id, accion, tenant_id))
            conn.commit()

    except Exception as e:
        # Usamos el logger de la aplicación para un registro de errores consistente.
        current_app.logger.error(f"⚠️ Alerta de Seguridad: No se pudo escribir en el Log: {e}")