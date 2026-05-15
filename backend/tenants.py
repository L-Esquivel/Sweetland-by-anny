from flask import Blueprint, jsonify, current_app, request
from flask_login import login_required
from db import get_db
from psycopg2.extras import DictCursor
from utils import superadmin_required
from werkzeug.security import generate_password_hash

tenants_bp = Blueprint("tenants_bp", __name__, url_prefix="/tenants")

@tenants_bp.route("/", methods=["GET"])
@login_required
@superadmin_required
def get_all_tenants():
    """
    Endpoint exclusivo para Super Admins.
    Devuelve una lista de todos los tenants registrados en el sistema.
    """
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("SELECT id_tenant, nombre, fecha_creacion FROM tenants ORDER BY fecha_creacion DESC")
            tenants = cursor.fetchall()
            return jsonify(tenants)
    except Exception as e:
        current_app.logger.error(f"Error en get_all_tenants: {e}")
        return jsonify({"error": "Error al obtener la lista de tenants"}), 500

@tenants_bp.route("/", methods=["POST"])
@login_required
@superadmin_required
def create_tenant_with_admin():
    """
    Crea un nuevo tenant y su primer usuario administrador.
    """
    data = request.json
    tenant_name = data.get('tenant_name')
    admin_name = data.get('admin_name')
    admin_email = data.get('admin_email')
    admin_password = data.get('admin_password')
    enabled_modules = data.get('enabled_modules', [])

    if not all([tenant_name, admin_name, admin_email, admin_password]):
        return jsonify({"error": "Todos los campos son obligatorios"}), 400

    conn = get_db()
    try:
        with conn.cursor() as cursor:
            # 1. Crear el Tenant
            cursor.execute("INSERT INTO tenants (nombre) VALUES (%s) RETURNING id_tenant", (tenant_name,))
            tenant_id = cursor.fetchone()[0]

            # 2. Crear el usuario Admin para ese Tenant
            hashed_password = generate_password_hash(admin_password)
            cursor.execute(
                "INSERT INTO usuarios (nombre, email, password, rol, tenant_id) VALUES (%s, %s, %s, 'admin', %s)",
                (admin_name, admin_email, hashed_password, tenant_id)
            )

            # 3. Asociar los módulos habilitados con el nuevo tenant
            if enabled_modules:
                args_str = ','.join(cursor.mogrify("(%s,%s)", (tenant_id, module_key)).decode('utf-8') for module_key in enabled_modules)
                cursor.execute("INSERT INTO tenant_modules (tenant_id, module_key) VALUES " + args_str)

            conn.commit()
            return jsonify({"mensaje": f"Tenant '{tenant_name}' y su admin '{admin_email}' creados con éxito."}), 201
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error en create_tenant_with_admin: {e}")
        return jsonify({"error": "Error al crear el tenant. El email del admin podría ya existir."}), 500

@tenants_bp.route("/<int:tenant_id>", methods=["PUT"])
@login_required
@superadmin_required
def update_tenant(tenant_id):
    data = request.json
    new_name = data.get('nombre')
    if not new_name:
        return jsonify({"error": "El nombre es obligatorio"}), 400
    
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE tenants SET nombre = %s WHERE id_tenant = %s", (new_name, tenant_id))
            conn.commit()
            return jsonify({"mensaje": "Tenant actualizado con éxito"})
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error en update_tenant: {e}")
        return jsonify({"error": "Error al actualizar el tenant"}), 500

@tenants_bp.route("/<int:tenant_id>", methods=["DELETE"])
@login_required
@superadmin_required
def delete_tenant(tenant_id):
    # ADVERTENCIA: Esto requiere que las foreign keys en la DB tengan 'ON DELETE CASCADE'
    # para borrar todos los datos asociados (productos, usuarios, etc.).
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM tenants WHERE id_tenant = %s", (tenant_id,))
            conn.commit()
            return jsonify({"mensaje": "Tenant y todos sus datos asociados han sido eliminados."})
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error en delete_tenant: {e}")
        return jsonify({"error": "Error al eliminar el tenant."}), 500