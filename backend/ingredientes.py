from flask import Blueprint, jsonify, request
from flask_login import login_required
from db import get_db_connection
from utils import admin_required, registrar_log # 🛡️ Importamos registrar_log
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

ingredientes_bp = Blueprint("ingredientes", __name__, url_prefix="/ingredientes")

@ingredientes_bp.route("/", methods=["GET"])
@login_required
def get_ingredientes():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ingredientes ORDER BY nombre")
        filas = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(list(filas))
    except Exception as e:
        logger.error(f"Error en get_ingredientes: {str(e)}")
        return jsonify({"error": str(e)}), 500

@ingredientes_bp.route("/", methods=["POST"])
@login_required
@admin_required
def create_ingrediente():
    try:
        data = request.get_json() or {}
        nombre = data.get("nombre")
        if not nombre or not data.get("unidad"):
            return jsonify({"error": "Nombre y Unidad son obligatorios"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO ingredientes (nombre, unidad, cantidad, costo_unitario)
            VALUES (%s, %s, %s, %s)
        """, (nombre, data.get("unidad"), float(data.get("cantidad") or 0), float(data.get("costo_unitario") or 0)))
        conn.commit()
        cursor.close()
        conn.close()

        # 🛡️ AUDITORÍA: Registro de creación
        registrar_log(f"Creó nuevo ingrediente: {nombre}")
        
        return jsonify({"mensaje": "Ingrediente creado correctamente"}), 201
    except Exception as e:
        return jsonify({"error": "Error interno al guardar"}), 500

@ingredientes_bp.route("/<int:id>", methods=["PUT"])
@login_required
@admin_required
def update_ingrediente(id):
    try:
        data = request.get_json() or {}
        nombre = data.get("nombre")
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE ingredientes
            SET nombre=%s, unidad=%s, cantidad=%s, costo_unitario=%s
            WHERE id_ingrediente=%s
        """, (nombre, data.get("unidad"), float(data.get("cantidad") or 0), 
              float(data.get("costo_unitario") or 0), id))
        conn.commit()
        cursor.close()
        conn.close()

        # 🛡️ AUDITORÍA: Registro de actualización
        registrar_log(f"Actualizó el ingrediente ID {id}: {nombre}")

        return jsonify({"mensaje": "Ingrediente actualizado"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ingredientes_bp.route("/<int:id>", methods=["DELETE"])
@login_required
@admin_required
def delete_ingrediente(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as total FROM recetas WHERE id_ingrediente = %s", (id,))
        if cursor.fetchone().get('total', 0) > 0:
            return jsonify({"error": "No se puede eliminar: está en uso en una receta"}), 400
        
        cursor.execute("DELETE FROM ingredientes WHERE id_ingrediente = %s", (id,))
        conn.commit()
        cursor.close()
        conn.close()

        # 🛡️ AUDITORÍA: Registro de eliminación
        registrar_log(f"Eliminó el ingrediente ID {id}")

        return jsonify({"mensaje": "Eliminado correctamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500