from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from flask import current_app

from db import get_db # 🟢 Importamos el nuevo gestor de DB
from psycopg2.extras import DictCursor # 🟢 Para obtener resultados como diccionarios

class User(UserMixin):
    def __init__(self, id, nombre, email, password, telefono=None, direccion=None, rol='cliente', tenant_id=None, enabled_modules=None):
        self.id = id
        self.nombre = nombre
        self.email = email
        self.password = password
        self.telefono = telefono
        self.direccion = direccion
        self.rol = rol
        self.tenant_id = tenant_id
        self.enabled_modules = enabled_modules or []

    @staticmethod
    def get_by_email(email):
        conn = get_db()
        try:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
                row = cursor.fetchone()
                if row:
                    # 💡 FIX: Obtenemos los módulos activos para el tenant de este usuario.
                    cursor.execute("SELECT module_key FROM tenant_modules WHERE tenant_id = %s", (row['tenant_id'],))
                    module_rows = cursor.fetchall()
                    enabled_modules = [m_row[0] for m_row in module_rows]

                    return User(
                        id=row["id_usuario"],
                        nombre=row["nombre"],
                        email=row["email"],
                        password=row["password"],
                        telefono=row.get("telefono"),
                        direccion=row.get("direccion"),
                        rol=row.get("rol", "cliente"),
                        tenant_id=row.get("tenant_id"),
                        enabled_modules=enabled_modules
                    )
                return None
        except Exception as e:
            # En caso de error de DB, es mejor que la app falle a que se comporte de forma inesperada
            current_app.logger.error(f"Error en User.get_by_email: {e}")
            return None

    @staticmethod
    def get_by_id(user_id):
        conn = get_db()
        try:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute("SELECT * FROM usuarios WHERE id_usuario = %s", (user_id,))
                row = cursor.fetchone()
                if row:
                    # 💡 FIX: Obtenemos los módulos activos para el tenant de este usuario.
                    cursor.execute("SELECT module_key FROM tenant_modules WHERE tenant_id = %s", (row['tenant_id'],))
                    module_rows = cursor.fetchall()
                    enabled_modules = [m_row[0] for m_row in module_rows]

                    return User(
                        id=row["id_usuario"],
                        nombre=row["nombre"],
                        email=row["email"],
                        password=row["password"],
                        telefono=row.get("telefono"),
                        direccion=row.get("direccion"),
                        rol=row.get("rol", "cliente"),
                        tenant_id=row.get("tenant_id"),
                        enabled_modules=enabled_modules
                    )
                return None
        except Exception as e:
            current_app.logger.error(f"Error en User.get_by_id: {e}")
            return None

    def check_password(self, password):
        return check_password_hash(self.password, password)