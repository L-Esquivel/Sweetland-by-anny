import pymysql
pymysql.install_as_MySQLdb()

class MySQL:
    def __init__(self):
        self.connection = None

    def init_app(self, app):
        pass  # Flask-MySQLdb compatibility

mysql = MySQL()