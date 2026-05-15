import os
import psycopg2
from psycopg2 import pool
from psycopg2.extras import DictCursor # Important! To access columns by name.
from flask import g, current_app # g is the request-bound global context

class Database:
    """
    Manages the PostgreSQL connection pool.
    A "pool" is a set of pre-opened connections that the application can
    use and return, which is much more efficient than opening and closing
    a connection for each query.
    """
    _pool = None

    @classmethod
    def initialize_pool(cls):
        """
        Initializes the connection pool using the database URL
        defined in the environment variables.
        """
        if cls._pool is None:
            try:
                database_url = os.getenv('DATABASE_URL')
                if not database_url:
                    raise ValueError("The DATABASE_URL environment variable is not set.")
                
                # Create the connection pool.
                cls._pool = psycopg2.pool.SimpleConnectionPool(
                    minconn=1,      # Minimum number of connections to keep open.
                    maxconn=10,     # Maximum number of simultaneous connections.
                    dsn=database_url # The PostgreSQL connection DSN.
                )
                current_app.logger.info("✅ PostgreSQL connection pool initialized.")
            except psycopg2.OperationalError as e:
                current_app.logger.error(f"❌ Could not connect to PostgreSQL: {e}")
                raise # Re-raise the exception to stop the app if it cannot connect.
            except ValueError as e:
                current_app.logger.error(f"❌ Configuration error: {e}")
                raise

    @classmethod
    def get_connection(cls):
        """Gets a connection from the pool."""
        if cls._pool is None:
            cls.initialize_pool()
        # getconn() will take a free connection from the pool or wait if all are busy.
        return cls._pool.getconn()

    @classmethod
    def release_connection(cls, conn):
        """Returns a connection to the pool so others can use it."""
        if cls._pool:
            cls._pool.putconn(conn)

    @classmethod
    def close_all_connections(cls):
        """Closes all connections in the pool (useful when shutting down the app)."""
        if cls._pool:
            cls._pool.closeall()
            cls._pool = None
            current_app.logger.info("PostgreSQL connection pool closed.")

# --- Helper functions for use in Flask routes ---

def get_db():
    """
    Gets a connection for the current Flask request.
    It uses the `g` object (request global) to store the connection and reuse it
    instead of requesting a new one within the same request.
    """
    if 'db_conn' not in g:
        g.db_conn = Database.get_connection()
    return g.db_conn

def close_db(e=None):
    """
    Closes (returns to the pool) the connection at the end of the request.
    Flask calls this function automatically thanks to `app.teardown_appcontext`.
    """
    conn = g.pop('db_conn', None)
    if conn is not None:
        Database.release_connection(conn)

def init_app(app):
    """Factory function to register the DB manager with the Flask app."""
    app.teardown_appcontext(close_db)
    with app.app_context():
        Database.initialize_pool()