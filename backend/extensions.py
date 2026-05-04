import pymysql
import threading
from db import get_db_connection
from flask_mail import Mail
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
            self._local.conn = get_db_connection()
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
mail = Mail()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["500 per day", "100 per hour"],
    storage_uri="memory://"
)