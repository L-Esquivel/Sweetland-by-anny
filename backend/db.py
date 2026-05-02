import pymysql
import urllib.parse as urlparse
from dotenv import load_dotenv
import os

load_dotenv()

def get_db_connection():
    """Devuelve una conexión PyMySQL fresca usando MYSQL_URL."""
    
    mysql_url = os.getenv('MYSQL_URL')
    
    if mysql_url:
        # Parsear la URL de Railway: mysql://user:password@host:port/database
        url = urlparse.urlparse(mysql_url)
        host = url.hostname
        user = url.username
        password = url.password
        database = url.path[1:] if url.path else None  # quita el slash inicial
        port = url.port or 3306
    else:
        # Fallback para desarrollo local con variables separadas
        host = os.getenv('MYSQL_HOST', 'localhost')
        user = os.getenv('MYSQL_USER', 'root')
        password = os.getenv('MYSQL_PASSWORD', 'Root1234')
        database = os.getenv('MYSQL_DB', 'sweetland_by_anny')
        port = int(os.getenv('MYSQL_PORT', 3306))
    
    return pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        port=int(port),
        cursorclass=pymysql.cursors.DictCursor,
        charset='utf8mb4',
        autocommit=False
    )