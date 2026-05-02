import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('MYSQL_HOST', 'localhost'),
        user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_PASSWORD', 'Root1234'),
        database=os.getenv('MYSQL_DB', 'sweetland_by_anny')
    )