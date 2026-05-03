from flask_login import UserMixin
from db import get_db_connection

class User(UserMixin):
    def __init__(self, id, nombre, email, password, telefono=None, direccion=None, rol='cliente'):
        self.id = id
        self.nombre = nombre
        self.email = email
        self.password = password
        self.telefono = telefono
        self.direccion = direccion
        self.rol = rol

    @staticmethod
    def get_by_email(email):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if row:
            return User(
                id=row["id_usuario"],
                nombre=row["nombre"],
                email=row["email"],
                password=row["password"],
                telefono=row.get("telefono"),
                direccion=row.get("direccion"),
                rol=row.get("rol", "cliente")
            )
        return None

    @staticmethod
    def get_by_id(user_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE id_usuario = %s", (user_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if row:
            return User(
                id=row["id_usuario"],
                nombre=row["nombre"],
                email=row["email"],
                password=row["password"],
                telefono=row.get("telefono"),
                direccion=row.get("direccion"),
                rol=row.get("rol", "cliente")
            )
        return None

    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password, password)

    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password = generate_password_hash(password)