from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from utils import admin_required, register_log
from db import get_db # 🟢 Importamos el nuevo gestor de DB
from psycopg2.extras import DictCursor # 🟢 Para obtener resultados como diccionarios
import datetime

merma_bp = Blueprint("merma_bp", __name__, url_prefix="/merma")

@merma_bp.route("/", methods=["GET"])
@admin_required
def get_waste_records():
    tenant_id = current_user.tenant_id
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            month = request.args.get('month', type=int)
            year = request.args.get('year', type=int)

            query = "SELECT * FROM merma WHERE tenant_id = %s"
            params = [tenant_id]

            if month and year:
                query += " AND EXTRACT(MONTH FROM fecha) = %s AND EXTRACT(YEAR FROM fecha) = %s"
                params.extend([month, year])
            
            query += " ORDER BY fecha DESC"

            cursor.execute(query, tuple(params))
            records_raw = cursor.fetchall()
            # FIX: Convert to dict to ensure JSON serialization and that the table is displayed.
            records = [dict(r) for r in records_raw]
            for record in records:
                if isinstance(record.get('fecha'), datetime.date):
                    record['fecha'] = record['fecha'].isoformat()
            return jsonify(records)
    except Exception as e:
        current_app.logger.error(f"Error in get_waste_records: {e}")
        return jsonify({"error": "Error fetching waste records"}), 500

@merma_bp.route("/", methods=["POST"])
@admin_required
def add_waste_record():
    data = request.get_json()
    id_producto = data.get("id_producto")
    id_ingrediente = data.get("id_ingrediente")
    cantidad = data.get("cantidad")
    fecha = data.get("fecha")
    motivo = data.get("motivo")
    tenant_id = current_user.tenant_id

    if not (id_producto or id_ingrediente) or not cantidad or not fecha:
        return jsonify({"error": "A product/ingredient, quantity, and date are required."}), 400

    conn = get_db()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            unit_cost = 0
            description = ""
            if id_producto:
                # FIX: The logic is changed to use the sale price ('precio') instead of the production cost.
                # This aligns the value of the waste with the actual sale value of the product.
                cursor.execute("SELECT nombre, precio FROM productos WHERE id_producto = %s AND tenant_id = %s", (id_producto, tenant_id))
                item = cursor.fetchone()
                if not item: return jsonify({"error": "Product not found"}), 404
                current_app.logger.debug(f"Waste (Product): ID {id_producto}, Name '{item.get('nombre')}', Sale Price: {item.get('precio', 0)}")
                unit_cost = item.get('precio', 0)
                description = f"Product: {item.get('nombre')}"
            elif id_ingrediente:
                # FIX: The column name is 'costo_por_unidad', not 'costo_unitario'.
                # This fixes a bug where the cost of ingredient waste was always 0.
                cursor.execute("SELECT nombre, costo_por_unidad FROM ingredientes WHERE id_ingrediente = %s AND tenant_id = %s", (id_ingrediente, tenant_id))
                item = cursor.fetchone()
                if not item: return jsonify({"error": "Ingredient not found"}), 404
                unit_cost = item.get('costo_por_unidad', 0)
                description = f"Ingredient: {item.get('nombre')}"

            loss_cost = float(unit_cost or 0) * float(cantidad)
            current_app.logger.debug(f"Waste: Quantity {cantidad}, Unit Cost {unit_cost}, Calculated Loss Cost: {loss_cost}")

            cursor.execute("""
                INSERT INTO merma (id_producto, id_ingrediente, descripcion, cantidad, costo_perdida, fecha, motivo, tenant_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (id_producto, id_ingrediente, description, cantidad, loss_cost, fecha, motivo, tenant_id))
            conn.commit()
            
            register_log(f"Registered waste for '{description}' with a cost of ${loss_cost}")
            return jsonify({"message": "Waste record added successfully"}), 201
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error in add_waste_record: {e}")
        return jsonify({"error": "Error adding waste record"}), 500

@merma_bp.route("/<int:id>", methods=["DELETE"])
@admin_required
def delete_waste_record(id):
    tenant_id = current_user.tenant_id
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM merma WHERE id_merma=%s AND tenant_id = %s", (id, tenant_id))
            conn.commit()
            if cursor.rowcount == 0:
                return jsonify({"error": "Waste record not found"}), 404
            register_log(f"Deleted waste record ID {id}")
            return jsonify({"message": "Waste record deleted successfully"})
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error in delete_waste_record: {e}")
        return jsonify({"error": "Error deleting waste record"}), 500