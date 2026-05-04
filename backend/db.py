import pymysql
import urllib.parse as urlparse
from dotenv import load_dotenv
import os

load_dotenv()

def get_db_connection():
    """Devuelve una conexión PyMySQL fresca usando variables de entorno."""
    
    # Intentamos obtener las variables individuales directamente
    host = os.getenv('MYSQL_HOST')
    user = os.getenv('MYSQL_USER')
    password = os.getenv('MYSQL_PASSWORD')
    database = os.getenv('MYSQL_DB')
    port = os.getenv('MYSQL_PORT')

    # Si no están las individuales, buscamos la URL (por si acaso en producción)
    if not host:
        mysql_url = os.getenv('MYSQL_URL')
        if mysql_url:
            url = urlparse.urlparse(mysql_url)
            host = url.hostname
            user = url.username
            password = url.password
            database = url.path[1:]
            port = url.port

    return pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        port=int(port or 3306),
        cursorclass=pymysql.cursors.DictCursor,
        charset='utf8mb4',
        autocommit=False,
        # AÑADIMOS ESTO PARA MAYOR COMPATIBILIDAD CON RAILWAY
        connect_timeout=10
    )