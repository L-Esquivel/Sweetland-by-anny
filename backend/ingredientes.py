from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from utils import admin_required, registrar_log # 🛡️ Importamos registrar_log
from db import get_db # 🟢 Importamos el nuevo gestor de DB
from psycopg2.extras import DictCursor # 🟢 Para obtener resultados como diccionarios
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

ingredientes_bp = Blueprint("ingredientes", __name__, url_prefix="/ingredientes")

@ingredientes_bp.route("/", methods=["GET"])
@login_required
def get_ingredientes():
    tenant_id = current_user.tenant_id
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            # 💡 SAAS-IFICATION: Filtramos por tenant_id.
            cursor.execute("SELECT * FROM ingredientes WHERE tenant_id = %s ORDER BY nombre", (tenant_id,))
            ingredientes = cursor.fetchall()
            return jsonify(ingredientes)
    except Exception as e:
        logger.error(f"Error en get_ingredientes: {e}", exc_info=True)
        return jsonify({"error": "Error al obtener los insumos"}), 500

@ingredientes_bp.route("/", methods=["POST"])
@login_required
@admin_required
def create_ingrediente():
    tenant_id = current_user.tenant_id
    try:
        data = request.get_json() or {}
        nombre = data.get("nombre")
        # 💡 STANDARDIZATION: Using consistent column names from schema.sql
        unidad_medida = data.get("unidad_medida")
        stock = data.get("stock", 0)
        costo_por_unidad = data.get("costo_por_unidad", 0)

        if not nombre or not unidad_medida:
            return jsonify({"error": "Nombre y Unidad de Medida son obligatorios"}), 400

        conn = get_db()
        with conn.cursor() as cursor:
            # 💡 SAAS-IFICATION: Insertamos el tenant_id.
            cursor.execute("""
                INSERT INTO ingredientes (nombre, unidad_medida, stock, costo_por_unidad, tenant_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (nombre, unidad_medida, float(stock), float(costo_por_unidad), tenant_id))
            conn.commit()

        # �️ AUDITORÍA: Registro de creación
        registrar_log(f"Creó nuevo ingrediente: {nombre}")
        
        return jsonify({"mensaje": "Ingrediente creado correctamente"}), 201
    except Exception as e:
        get_db().rollback()
        logger.error(f"Error en create_ingrediente: {e}", exc_info=True)
        return jsonify({"error": "Error al crear el insumo"}), 500

@ingredientes_bp.route("/<int:id>", methods=["PUT"])
@login_required
@admin_required
def update_ingrediente(id):
    tenant_id = current_user.tenant_id
    try:
        data = request.get_json() or {}
        nombre = data.get("nombre")
        # 💡 STANDARDIZATION: Using consistent column names from schema.sql
        unidad_medida = data.get("unidad_medida")
        stock = data.get("stock")
        costo_por_unidad = data.get("costo_por_unidad")

        conn = get_db()
        with conn.cursor() as cursor:
            # 💡 SAAS-IFICATION: Aseguramos que solo se pueda actualizar un ingrediente del tenant correcto.
            cursor.execute("""
                UPDATE ingredientes
                SET nombre=%s, unidad_medida=%s, stock=%s, costo_por_unidad=%s
                WHERE id_ingrediente=%s AND tenant_id = %s
            """, (nombre, unidad_medida, float(stock or 0), float(costo_por_unidad or 0), id, tenant_id))
            conn.commit()

        # �️ AUDITORÍA: Registro de actualización
        registrar_log(f"Actualizó el ingrediente ID {id}: {nombre}")

        return jsonify({"mensaje": "Ingrediente actualizado"})
    except Exception as e:
        get_db().rollback()
        logger.error(f"Error en update_ingrediente: {e}", exc_info=True)
        return jsonify({"error": "Error al actualizar el insumo"}), 500

@ingredientes_bp.route("/<int:id>", methods=["DELETE"])
@login_required
@admin_required
def delete_ingrediente(id):
    tenant_id = current_user.tenant_id
    try:
        conn = get_db()
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            # VERIFICACIÓN: ¿Está este ingrediente en uso por alguna receta?
            cursor.execute("SELECT COUNT(*) as total FROM recetas_ingredientes WHERE id_ingrediente = %s AND tenant_id = %s", (id, tenant_id))
            if cursor.fetchone()['total'] > 0:
                return jsonify({"error": "No se puede eliminar: el ingrediente está en uso en una o más recetas."}), 400

            # 💡 SAAS-IFICATION: Aseguramos que solo se pueda borrar un ingrediente del tenant correcto.
            cursor.execute("DELETE FROM ingredientes WHERE id_ingrediente = %s AND tenant_id = %s", (id, tenant_id))
            
            if cursor.rowcount == 0:
                return jsonify({"error": "Ingrediente no encontrado o no pertenece a tu organización"}), 404

            conn.commit()

        # 🛡️ AUDITORÍA: Registro de eliminación
        registrar_log(f"Eliminó el ingrediente ID {id}")

        return jsonify({"mensaje": "Eliminado correctamente"})
    except Exception as e:
        get_db().rollback()
        logger.error(f"Error en delete_ingrediente: {e}", exc_info=True)
        return jsonify({"error": "Error al eliminar el insumo"}), 500