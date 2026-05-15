from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from utils import admin_required, registrar_log # 🛡️ Importamos current_user
from db import get_db # 🟢 Importamos el nuevo gestor de DB
from psycopg2.extras import DictCursor # 🟢 Para obtener resultados como diccionarios
import datetime

gastos_bp = Blueprint("gastos_bp", __name__, url_prefix="/gastos")

@gastos_bp.route("/", methods=["GET"])
@login_required
@admin_required
def get_gastos():
    tenant_id = current_user.tenant_id
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
        # Permite filtrar por mes y año, ej: /gastos?mes=10&ano=2023
            mes = request.args.get('mes', type=int)
            ano = request.args.get('ano', type=int)

            # 💡 SAAS-IFICATION: Filtramos gastos por el tenant_id del usuario logueado.
            query = "SELECT * FROM gastos WHERE tenant_id = %s"
            params = [tenant_id]
            
            if mes and ano:
                query += " AND EXTRACT(MONTH FROM fecha) = %s AND EXTRACT(YEAR FROM fecha) = %s"
                params.extend([mes, ano])
            
            query += " ORDER BY fecha DESC"
            
            cursor.execute(query, tuple(params))
            gastos_raw = cursor.fetchall()
            # FIX: Convertir a dict para asegurar la serialización JSON y que la tabla se muestre.
            gastos = [dict(g) for g in gastos_raw]
            # Convierte objetos de fecha a string para la serialización JSON
            for gasto in gastos:
                if isinstance(gasto.get('fecha'), datetime.date):
                    gasto['fecha'] = gasto['fecha'].isoformat()
            return jsonify(gastos)
    except Exception as e:
        current_app.logger.error(f"Error en get_gastos: {e}")
        return jsonify({"error": "Error al obtener los gastos"}), 500

@gastos_bp.route("/", methods=["POST"])
@admin_required
def add_gasto():
    data = request.get_json()
    descripcion = data.get("descripcion")
    monto = data.get("monto")
    fecha = data.get("fecha")
    tenant_id = current_user.tenant_id
    categoria = data.get("categoria", "Varios")

    if not descripcion or not monto or not fecha:
        return jsonify({"error": "Descripción, monto y fecha son obligatorios"}), 400

    conn = get_db()
    try:
        with conn.cursor() as cursor:
            # 💡 SAAS-IFICATION: Insertamos el tenant_id al crear un nuevo gasto.
            cursor.execute("""
                INSERT INTO gastos (descripcion, monto, categoria, fecha, tenant_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (descripcion, monto, categoria, fecha, tenant_id))
            conn.commit()
            registrar_log(f"Registró nuevo gasto: {descripcion} por ${monto}")
            return jsonify({"mensaje": "Gasto registrado con éxito"}), 201
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error en add_gasto: {e}")
        return jsonify({"error": "Error al registrar el gasto"}), 500

@gastos_bp.route("/<int:id>", methods=["PUT"])
@admin_required
def update_gasto(id):
    tenant_id = current_user.tenant_id
    data = request.get_json()
    descripcion = data.get("descripcion")
    monto = data.get("monto")
    fecha = data.get("fecha")
    categoria = data.get("categoria")

    if not all([descripcion, monto, fecha, categoria]):
        return jsonify({"error": "Descripción, monto, fecha y categoría son obligatorios"}), 400

    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE gastos 
                SET descripcion=%s, monto=%s, categoria=%s, fecha=%s
                WHERE id_gasto=%s AND tenant_id=%s
            """, (descripcion, monto, categoria, fecha, id, tenant_id))
            
            if cursor.rowcount == 0:
                return jsonify({"error": "Gasto no encontrado o no pertenece a tu organización"}), 404

            conn.commit()
            registrar_log(f"Actualizó gasto ID {id}: {descripcion}")
            return jsonify({"mensaje": "Gasto actualizado con éxito"})
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error en update_gasto: {e}")
        return jsonify({"error": "Error al actualizar el gasto"}), 500

@gastos_bp.route("/<int:id>", methods=["DELETE"])
@admin_required
def delete_gasto(id):
    tenant_id = current_user.tenant_id
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            # 💡 SAAS-IFICATION: Aseguramos que solo se pueda borrar un gasto del tenant correcto.
            cursor.execute("DELETE FROM gastos WHERE id_gasto=%s AND tenant_id = %s", (id, tenant_id))
            conn.commit()
            registrar_log(f"Eliminó gasto ID {id}")
            return jsonify({"mensaje": "Gasto eliminado con éxito"})
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error en delete_gasto: {e}")
        return jsonify({"error": "Error al eliminar el gasto"}), 500