from flask_login import UserMixin
from extensions import mysql

class User(UserMixin):
    def __init__(self, id, nombre, email, password, telefono=None, direccion=None, rol='cliente', tenant_id=None):
        self.id = id
        self.nombre = nombre
        self.email = email
        self.password = password
        self.telefono = telefono
        self.direccion = direccion
        self.rol = rol
        self.tenant_id = tenant_id

    @staticmethod
    def get_by_email(email):
        cursor = mysql.connection.cursor()
        try:
            cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
            row = cursor.fetchone()
            if row:
                return User(
                    id=row["id_usuario"],
                    nombre=row["nombre"],
                    email=row["email"],
                    password=row["password"],
                    telefono=row.get("telefono"),
                    direccion=row.get("direccion"),
                    rol=row.get("rol", "cliente"),
                    tenant_id=row.get("tenant_id")
                )
            return None
        finally:
            if cursor: cursor.close()

    @staticmethod
    def get_by_id(user_id):
        cursor = mysql.connection.cursor()
        try:
            cursor.execute("SELECT * FROM usuarios WHERE id_usuario = %s", (user_id,))
            row = cursor.fetchone()
            if row:
                return User(
                    id=row["id_usuario"],
                    nombre=row["nombre"],
                    email=row["email"],
                    password=row["password"],
                    telefono=row.get("telefono"),
                    direccion=row.get("direccion"),
                    rol=row.get("rol", "cliente"),
                    tenant_id=row.get("tenant_id")
                )
            return None
        finally:
            if cursor: cursor.close()

    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password, password)

    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password = generate_password_hash(password)