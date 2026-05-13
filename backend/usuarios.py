from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from extensions import mysql
from utils import admin_required  # Importamos tu nuevo decorador

usuarios_bp = Blueprint("usuarios_bp", __name__, url_prefix="/usuarios")

# ============================================================
# TODAS LAS RUTAS ABAJO REQUIEREN ROL 'admin' 🛡️
# ============================================================

@usuarios_bp.route("/", methods=["GET"])
@login_required
@admin_required
def get_usuarios():
    tenant_id = current_user.tenant_id
    cursor = mysql.connection.cursor()
    try:
        # 💡 SAAS-IFICATION: Un admin solo puede ver los usuarios de su propio tenant.
        cursor.execute("SELECT id_usuario, nombre, email, telefono, direccion, rol FROM usuarios WHERE tenant_id = %s", (tenant_id,))
        rows = cursor.fetchall()
        return jsonify(rows)
    finally:
        if cursor: cursor.close()

@usuarios_bp.route("/<int:id>", methods=["GET"])
@login_required
@admin_required
def get_usuario(id):
    tenant_id = current_user.tenant_id
    cursor = mysql.connection.cursor()
    try:
        # 💡 SAAS-IFICATION: Un admin solo puede ver un usuario de su propio tenant.
        cursor.execute("SELECT id_usuario, nombre, email, telefono, direccion, rol FROM usuarios WHERE id_usuario = %s AND tenant_id = %s", (id, tenant_id))
        row = cursor.fetchone()
        if row:
            return jsonify(row)
        return jsonify({"error": "Usuario no encontrado"}), 404
    finally:
        if cursor: cursor.close()

@usuarios_bp.route("/", methods=["POST"])
@login_required
@admin_required
def add_usuario():
    tenant_id = current_user.tenant_id
    data = request.json
    nombre    = data.get("nombre")
    email     = data.get("email")
    password  = data.get("password")
    telefono  = data.get("telefono")
    direccion = data.get("direccion")
    rol       = data.get("rol", "cliente")

    if not nombre or not email or not password:
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    hashed_pw = generate_password_hash(password)
    cursor = mysql.connection.cursor()
    try:
        # 💡 SAAS-IFICATION: Un nuevo usuario creado por un admin pertenece al mismo tenant.
        cursor.execute("""
            INSERT INTO usuarios (nombre, email, password, telefono, direccion, rol, tenant_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (nombre, email, hashed_pw, telefono, direccion, rol, tenant_id))
        mysql.connection.commit()
        return jsonify({"mensaje": "Usuario agregado con éxito"}), 201
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"error": "El email ya podría estar registrado"}), 400
    finally:
        if cursor: cursor.close()

@usuarios_bp.route("/<int:id>", methods=["PUT"])
@login_required
@admin_required
def update_usuario(id):
    tenant_id = current_user.tenant_id
    data      = request.json
    nombre    = data.get("nombre")
    email     = data.get("email")
    telefono  = data.get("telefono")
    direccion = data.get("direccion")
    rol       = data.get("rol")
    password  = data.get("password")

    cursor = mysql.connection.cursor()
    try:
        if password:
            hashed_pw = generate_password_hash(password)
            cursor.execute("""
                UPDATE usuarios
                SET nombre=%s, email=%s, telefono=%s, direccion=%s, rol=%s, password=%s
                WHERE id_usuario=%s AND tenant_id = %s
            """, (nombre, email, telefono, direccion, rol, hashed_pw, id, tenant_id))
        else:
            cursor.execute("""
                UPDATE usuarios
                SET nombre=%s, email=%s, telefono=%s, direccion=%s, rol=%s
                WHERE id_usuario=%s AND tenant_id = %s
            """, (nombre, email, telefono, direccion, rol, id, tenant_id))
        mysql.connection.commit()
        return jsonify({"mensaje": "Usuario actualizado correctamente"})
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor: cursor.close()

@usuarios_bp.route("/<int:id>", methods=["DELETE"])
@login_required
@admin_required
def delete_usuario(id):
    tenant_id = current_user.tenant_id
    # 🛡️ Protección: Evitar que un admin se borre a sí mismo.
    if current_user.id == id:
        return jsonify({"error": "No puedes eliminar tu propio usuario administrador"}), 403

    cursor = mysql.connection.cursor()
    try:
        cursor.execute("DELETE FROM usuarios WHERE id_usuario=%s AND tenant_id = %s", (id, tenant_id))
        mysql.connection.commit()
        return jsonify({"mensaje": "Usuario eliminado"})
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor: cursor.close()