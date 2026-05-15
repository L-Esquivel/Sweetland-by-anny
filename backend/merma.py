from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from utils import admin_required, registrar_log
from db import get_db # 🟢 Importamos el nuevo gestor de DB
from psycopg2.extras import DictCursor # 🟢 Para obtener resultados como diccionarios
import datetime

merma_bp = Blueprint("merma_bp", __name__, url_prefix="/merma")

@merma_bp.route("/", methods=["GET"])
@login_required
@admin_required
def get_merma_registros():
    tenant_id = current_user.tenant_id
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            mes = request.args.get('mes', type=int)
            ano = request.args.get('ano', type=int)

            query = "SELECT * FROM merma WHERE tenant_id = %s"
            params = [tenant_id]

            if mes and ano:
                query += " AND EXTRACT(MONTH FROM fecha) = %s AND EXTRACT(YEAR FROM fecha) = %s"
                params.extend([mes, ano])
            
            query += " ORDER BY fecha DESC"

            cursor.execute(query, tuple(params))
            registros_raw = cursor.fetchall()
            # FIX: Convertir a dict para asegurar la serialización JSON y que la tabla se muestre.
            registros = [dict(r) for r in registros_raw]
            for registro in registros:
                if isinstance(registro.get('fecha'), datetime.date):
                    registro['fecha'] = registro['fecha'].isoformat()
            return jsonify(registros)
    except Exception as e:
        current_app.logger.error(f"Error en get_merma_registros: {e}")
        return jsonify({"error": "Error al obtener registros de merma"}), 500

@merma_bp.route("/", methods=["POST"])
@admin_required
def add_merma_registro():
    data = request.get_json()
    id_producto = data.get("id_producto")
    id_ingrediente = data.get("id_ingrediente")
    cantidad = data.get("cantidad")
    fecha = data.get("fecha")
    motivo = data.get("motivo")
    tenant_id = current_user.tenant_id

    if not (id_producto or id_ingrediente) or not cantidad or not fecha:
        return jsonify({"error": "Se requiere un producto/ingrediente, cantidad y fecha."}), 400

    conn = get_db()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            costo_unitario = 0
            descripcion = ""
            if id_producto:
                cursor.execute("SELECT nombre, costo_produccion FROM productos WHERE id_producto = %s AND tenant_id = %s", (id_producto, tenant_id))
                item = cursor.fetchone()
                if not item: return jsonify({"error": "Producto no encontrado"}), 404
                logger.debug(f"Merma (Producto): ID {id_producto}, Nombre '{item.get('nombre')}', Costo Producción: {item.get('costo_produccion', 0)}")
                costo_unitario = item.get('costo_produccion', 0)
                descripcion = f"Producto: {item.get('nombre')}"
            elif id_ingrediente:
                # FIX: El nombre de la columna es 'costo_por_unidad', no 'costo_unitario'.
                # Esto corrige un bug donde el costo de la merma de ingredientes siempre era 0.
                cursor.execute("SELECT nombre, costo_por_unidad FROM ingredientes WHERE id_ingrediente = %s AND tenant_id = %s", (id_ingrediente, tenant_id))
                item = cursor.fetchone()
                if not item: return jsonify({"error": "Ingrediente no encontrado"}), 404
                costo_unitario = item.get('costo_por_unidad', 0)
                descripcion = f"Ingrediente: {item.get('nombre')}"

            costo_perdida = float(costo_unitario or 0) * float(cantidad)
            logger.debug(f"Merma: Cantidad {cantidad}, Costo Unitario {costo_unitario}, Costo Pérdida Calculado: {costo_perdida}")

            cursor.execute("""
                INSERT INTO merma (id_producto, id_ingrediente, descripcion, cantidad, costo_perdida, fecha, motivo, tenant_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (id_producto, id_ingrediente, descripcion, cantidad, costo_perdida, fecha, motivo, tenant_id))
            conn.commit()
            
            registrar_log(f"Registró merma de '{descripcion}' por un costo de ${costo_perdida}")
            return jsonify({"mensaje": "Registro de merma añadido con éxito"}), 201
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error en add_merma_registro: {e}")
        return jsonify({"error": "Error al añadir registro de merma"}), 500

@merma_bp.route("/<int:id>", methods=["DELETE"])
@admin_required
def delete_merma_registro(id):
    tenant_id = current_user.tenant_id
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM merma WHERE id_merma=%s AND tenant_id = %s", (id, tenant_id))
            conn.commit()
            if cursor.rowcount == 0:
                return jsonify({"error": "Registro de merma no encontrado"}), 404
            registrar_log(f"Eliminó registro de merma ID {id}")
            return jsonify({"mensaje": "Registro de merma eliminado"})
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error en delete_merma_registro: {e}")
        return jsonify({"error": "Error al eliminar registro de merma"}), 500