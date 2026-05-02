import pymysql
pymysql.install_as_MySQLdb()

# No usamos Flask-MySQLdb, solo la compatibilidad
# El objeto mysql se usa en el código como extensión
from flask_mysqldb import MySQL

mysql = MySQL()