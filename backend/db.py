import os
import psycopg2
from psycopg2 import pool
from psycopg2.extras import DictCursor # ¡Importante! Para acceder a las columnas por su nombre.
from flask import g, current_app

class Database:
    """
    Clase para gestionar el pool de conexiones a PostgreSQL.
    Un "pool" es un conjunto de conexiones pre-abiertas que la aplicación puede
    usar y devolver, lo cual es mucho más eficiente que abrir y cerrar una
    conexión para cada consulta.
    """
    _pool = None

    @classmethod
    def initialize_pool(cls):
        """
        Inicializa el pool de conexiones usando la URL de la base de datos
        definida en las variables de entorno.
        """
        if cls._pool is None:
            try:
                database_url = os.getenv('DATABASE_URL')
                if not database_url:
                    raise ValueError("La variable de entorno DATABASE_URL no está configurada.")
                
                # Creamos el pool de conexiones.
                cls._pool = psycopg2.pool.SimpleConnectionPool(
                    minconn=1,      # Mínimo de conexiones que se mantienen abiertas.
                    maxconn=10,     # Máximo de conexiones que se pueden abrir simultáneamente.
                    dsn=database_url # La URL de conexión a PostgreSQL.
                )
                current_app.logger.info("✅ Pool de conexiones a PostgreSQL inicializado.")
            except psycopg2.OperationalError as e:
                current_app.logger.error(f"❌ No se pudo conectar a PostgreSQL: {e}")
                raise # Relanzamos la excepción para detener la app si no puede conectar.
            except ValueError as e:
                current_app.logger.error(f"❌ Error de configuración: {e}")
                raise

    @classmethod
    def get_connection(cls):
        """Obtiene una conexión del pool."""
        if cls._pool is None:
            cls.initialize_pool()
        # getconn() tomará una conexión libre del pool o esperará si todas están ocupadas.
        return cls._pool.getconn()

    @classmethod
    def release_connection(cls, conn):
        """Devuelve una conexión al pool para que otros la puedan usar."""
        if cls._pool:
            cls._pool.putconn(conn)

    @classmethod
    def close_all_connections(cls):
        """Cierra todas las conexiones del pool (útil al apagar la app)."""
        if cls._pool:
            cls._pool.closeall()
            cls._pool = None
            current_app.logger.info("Pool de conexiones a PostgreSQL cerrado.")

# --- Funciones de ayuda para usar en las rutas de Flask ---

def get_db():
    """
    Obtiene una conexión para la petición actual de Flask.
    Usa el objeto `g` (global de la petición) para almacenar la conexión y reutilizarla
    en lugar de pedir una nueva en la misma petición.
    """
    if 'db_conn' not in g:
        g.db_conn = Database.get_connection()
    return g.db_conn

def close_db(e=None):
    """
    Cierra (devuelve al pool) la conexión al final de la petición.
    Flask llama a esta función automáticamente gracias a `app.teardown_appcontext`.
    """
    conn = g.pop('db_conn', None)
    if conn is not None:
        Database.release_connection(conn)

def init_app(app):
    """Función de fábrica para registrar el gestor de DB con la app Flask."""
    app.teardown_appcontext(close_db)
    with app.app_context():
        Database.initialize_pool()