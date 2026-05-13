import pymysql
import threading
from flask import current_app
import os
import urllib.parse as urlparse
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Hace que PyMySQL se comporte como MySQLdb
pymysql.install_as_MySQLdb()

class MySQL:
    """Reemplazo compatible con Flask-MySQLdb usando PyMySQL puro."""
    def __init__(self):
        self._local = threading.local()

    def init_app(self, app):
        """Registra el cierre automático de conexiones al terminar cada request."""
        @app.teardown_appcontext
        def close_db(exception):
            self.close_connection()

    @property
    def connection(self):
        """Devuelve la conexión del hilo actual (la crea si no existe)."""
        if not hasattr(self._local, 'conn') or self._local.conn is None:
            # 💡 FIX: Lógica de conexión robusta para local y producción (Railway)
            
            # 1. Intenta obtener las variables de entorno individuales (para desarrollo local)
            host = current_app.config.get('MYSQL_HOST')
            user = current_app.config.get('MYSQL_USER')
            password = current_app.config.get('MYSQL_PASSWORD')
            db = current_app.config.get('MYSQL_DB')
            port = current_app.config.get('MYSQL_PORT')

            # 2. Si no encuentra el host, busca una URL de conexión (para producción en Railway)
            if not host:
                db_url_str = os.getenv('DATABASE_URL') or os.getenv('MYSQL_URL')
                if db_url_str:
                    url = urlparse.urlparse(db_url_str)
                    host = url.hostname
                    user = url.username
                    password = url.password
                    db = url.path[1:]  # Elimina el '/' inicial
                    port = url.port

            self._local.conn = pymysql.connect(
                host=host, user=user, password=password, db=db,
                port=int(port or 3306),
                cursorclass=pymysql.cursors.DictCursor
            )
        return self._local.conn

    def close_connection(self):
        """Cierra la conexión del hilo actual."""
        if hasattr(self._local, 'conn') and self._local.conn:
            try:
                self._local.conn.close()
            except Exception:
                pass
            self._local.conn = None

# --- INSTANCIAS GLOBALES ---
mysql = MySQL()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["500 per day", "100 per hour"],
    storage_uri="memory://"
)