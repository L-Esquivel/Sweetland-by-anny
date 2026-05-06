from functools import wraps
from flask import jsonify, request
from flask_login import current_user
from db import get_db_connection

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
    Guarda un registro de la actividad en la tabla audit_logs.
    """
    try:
        print(f"🕵️ Intentando registrar log: {accion}")
        # Capturamos la IP manejando el proxy de Railway/Vercel
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        
        usuario_id = None
        usuario_nombre = "Sistema / Invitado"
        
        # Si el usuario está logueado, tomamos sus datos
        if current_user.is_authenticated:
            usuario_id = current_user.id
            usuario_nombre = current_user.nombre
        else:
            usuario_id = None
            usuario_nombre = "Usuario Anónimo"

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO audit_logs (usuario_id, usuario_nombre, accion, endpoint, metodo, ip_address)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (usuario_id, usuario_nombre, accion, request.path, request.method, ip))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"⚠️ Alerta de Seguridad: No se pudo escribir en Audit Log: {e}")