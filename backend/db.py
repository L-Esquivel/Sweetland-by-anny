import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

def get_db_connection():
    """Devuelve una conexión PyMySQL fresca."""
    return pymysql.connect(
        host=os.getenv('MYSQL_HOST', 'localhost'),
        user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_PASSWORD', 'Root1234'),
        database=os.getenv('MYSQL_DB', 'sweetland_by_anny'),
        port=int(os.getenv('MYSQL_PORT', 3306)),
        cursorclass=pymysql.cursors.DictCursor,
        charset='utf8mb4',
        autocommit=False
    )