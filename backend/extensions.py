from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# The MySQL class has been replaced by the db.py module,
# which manages a PostgreSQL connection pool more efficiently.
# The `mysql` object is no longer needed.

# --- GLOBAL INSTANCES ---
# The `mysql` object is removed. Routes will now use `get_db()` from the `db` module.

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["500 per day", "100 per hour"],
    storage_uri="memory://"
)