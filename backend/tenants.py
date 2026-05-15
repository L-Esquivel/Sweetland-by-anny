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
    Endpoint exclusive to Super Admins.
    Returns a list of all tenants registered in the system.
    """
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("SELECT id_tenant, nombre, fecha_creacion FROM tenants ORDER BY fecha_creacion DESC")
            tenants_raw = cursor.fetchall()
            # Explicitly convert results to a list of dictionaries
            # to ensure consistent and predictable JSON serialization.
            tenants = [dict(row) for row in tenants_raw]
            return jsonify(tenants)
    except Exception as e:
        current_app.logger.error(f"Error en get_all_tenants: {e}")
        return jsonify({"error": "Error fetching tenant list"}), 500

@tenants_bp.route("/", methods=["POST"])
@login_required
@superadmin_required
def create_tenant_with_admin():
    """
    Creates a new tenant and its first admin user.
    """
    data = request.json
    tenant_name = data.get('tenant_name')
    admin_name = data.get('admin_name')
    admin_email = data.get('admin_email')
    admin_password = data.get('admin_password')
    custom_labels = data.get('custom_labels', {})

    if not all([tenant_name, admin_name, admin_email, admin_password]):
        return jsonify({"error": "All fields are required"}), 400

    conn = get_db()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            # 1. Create the Tenant
            cursor.execute("INSERT INTO tenants (nombre) VALUES (%s) RETURNING id_tenant", (tenant_name,))
            tenant_id = cursor.fetchone()[0]

            # 2. Create the Admin user for that Tenant
            hashed_password = generate_password_hash(admin_password)
            cursor.execute(
                "INSERT INTO usuarios (nombre, email, password, rol, tenant_id) VALUES (%s, %s, %s, 'admin', %s)",
                (admin_name, admin_email, hashed_password, tenant_id)
            )

            # 3. Get all available modules and their default labels
            cursor.execute("SELECT module_key, label FROM modules")
            all_modules = cursor.fetchall()

            # 4. Prepare label settings for insertion
            settings_to_insert = []
            for module in all_modules:
                module_key = module['module_key']
                # FIX: If the custom label is empty, use the default label.
                # This prevents saving blank labels if the user doesn't customize a module.
                custom_value = custom_labels.get(module_key)
                final_label = custom_value if custom_value else module['label']
                settings_to_insert.append((tenant_id, module_key, final_label))

            # 5. Insert all module settings for the new tenant
            if settings_to_insert:
                args_str = ','.join(cursor.mogrify("(%s,%s,%s)", s).decode('utf-8') for s in settings_to_insert)
                cursor.execute("INSERT INTO tenant_module_settings (tenant_id, module_key, custom_label) VALUES " + args_str)

            conn.commit()
            return jsonify({"message": f"Tenant '{tenant_name}' and its admin '{admin_email}' created successfully."}), 201
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error en create_tenant_with_admin: {e}")
        return jsonify({"error": "Error creating the tenant. The admin's email might already exist."}), 500

@tenants_bp.route("/<int:tenant_id>", methods=["PUT"])
@login_required
@superadmin_required
def update_tenant(tenant_id):
    data = request.json
    new_name = data.get('nombre')
    if not new_name:
        return jsonify({"error": "Name is required"}), 400
    
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE tenants SET nombre = %s WHERE id_tenant = %s", (new_name, tenant_id))
            conn.commit()
            return jsonify({"message": "Tenant updated successfully"})
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error en update_tenant: {e}")
        return jsonify({"error": "Error updating the tenant"}), 500

@tenants_bp.route("/<int:tenant_id>", methods=["DELETE"])
@login_required
@superadmin_required
def delete_tenant(tenant_id):
    # WARNING: This requires foreign keys in the DB to have 'ON DELETE CASCADE'
    # to delete all associated data (products, users, etc.).
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM tenants WHERE id_tenant = %s", (tenant_id,))
            conn.commit()
            return jsonify({"message": "Tenant and all its associated data have been deleted."})
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error en delete_tenant: {e}")
        return jsonify({"error": "Error deleting the tenant."}), 500