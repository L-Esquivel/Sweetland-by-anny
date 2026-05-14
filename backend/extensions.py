from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# La clase MySQL ha sido reemplazada por el módulo db.py,
# que gestiona un pool de conexiones a PostgreSQL de forma más eficiente.
# El objeto `mysql` ya no es necesario.

# --- INSTANCIAS GLOBALES ---
# El objeto `mysql` se elimina. Las rutas ahora usarán `get_db()` del módulo `db`.

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["500 per day", "100 per hour"],
    storage_uri="memory://"
)