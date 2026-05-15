from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from flask import current_app

from db import get_db # 🟢 Import the new DB manager
from psycopg2.extras import DictCursor # 🟢 To get results as dictionaries

class User(UserMixin):
    def __init__(self, id, nombre, email, password, telefono=None, direccion=None, rol='cliente', tenant_id=None, module_settings=None):
        self.id = id
        self.nombre = nombre
        self.email = email
        self.password = password
        self.telefono = telefono
        self.direccion = direccion
        self.rol = rol
        self.tenant_id = tenant_id
        self.module_settings = module_settings or []

    @staticmethod
    def get_by_email(email):
        conn = get_db()
        try:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
                row = cursor.fetchone()
                if row:
                    # 💡 IMPROVEMENT: Fetch custom module settings for the user's tenant.
                    cursor.execute("""
                        SELECT
                            m.module_key,
                            COALESCE(tms.custom_label, m.label) AS label
                        FROM
                            modules m
                        LEFT JOIN
                            tenant_module_settings tms ON m.module_key = tms.module_key AND tms.tenant_id = %s ORDER BY m.order_index ASC
                    """, (row['tenant_id'],))
                    # FIX: Explicitly convert results to a list of dictionaries
                    # to ensure consistent JSON serialization, similar to tenants.py.
                    module_settings_raw = cursor.fetchall()
                    module_settings = [dict(setting) for setting in module_settings_raw]

                    return User(
                        id=row["id_usuario"],
                        nombre=row["nombre"],
                        email=row["email"],
                        password=row["password"],
                        telefono=row.get("telefono"),                        direccion=row.get("direccion"),
                        rol=row.get("rol", "cliente"),
                        tenant_id=row.get("tenant_id"),
                        module_settings=module_settings
                    )
                return None
        except Exception as e:
            # In case of a DB error, it's better for the app to fail than to behave unexpectedly.
            current_app.logger.error(f"Error in User.get_by_email: {e}")
            return None

    @staticmethod
    def get_by_id(user_id):
        conn = get_db()
        try:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute("SELECT * FROM usuarios WHERE id_usuario = %s", (user_id,))
                row = cursor.fetchone()
                if row:
                    # 💡 IMPROVEMENT: Fetch custom module settings for the user's tenant.
                    cursor.execute("""
                        SELECT
                            m.module_key,
                            COALESCE(tms.custom_label, m.label) AS label
                        FROM
                            modules m
                        LEFT JOIN
                            tenant_module_settings tms ON m.module_key = tms.module_key AND tms.tenant_id = %s ORDER BY m.order_index ASC
                    """, (row['tenant_id'],))
                    # FIX: Explicitly convert results to a list of dictionaries.
                    module_settings_raw = cursor.fetchall()
                    module_settings = [dict(setting) for setting in module_settings_raw]

                    return User(
                        id=row["id_usuario"],
                        nombre=row["nombre"],
                        email=row["email"],
                        password=row["password"],
                        telefono=row.get("telefono"),                        direccion=row.get("direccion"),
                        rol=row.get("rol", "cliente"),
                        tenant_id=row.get("tenant_id"),
                        module_settings=module_settings
                    )
                return None
        except Exception as e:
            current_app.logger.error(f"Error in User.get_by_id: {e}")
            return None

    def check_password(self, password):
        return check_password_hash(self.password, password)