import psycopg2
import psycopg2.extras
import threading
import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# NOTA: Ya no se necesita pymysql.install_as_MySQLdb()

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
            # 💡 MIGRACIÓN A POSTGRESQL:
            # La lógica ahora lee directamente la DATABASE_URL, que es el estándar
            # para plataformas como Render y Heroku.
            db_url = os.getenv('DATABASE_URL')
            if not db_url:
                raise RuntimeError("DATABASE_URL no está configurada en el entorno.")
            
            # psycopg2 se conecta directamente usando la URL.
            self._local.conn = psycopg2.connect(
                db_url,
                cursor_factory=psycopg2.extras.DictCursor # Para obtener resultados como diccionarios.
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