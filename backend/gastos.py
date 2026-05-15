from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from utils import admin_required, register_log # 🛡️ Import the log utility
from db import get_db # 🟢 Importamos el nuevo gestor de DB
from psycopg2.extras import DictCursor # 🟢 Para obtener resultados como diccionarios
import datetime

gastos_bp = Blueprint("gastos_bp", __name__, url_prefix="/gastos")

@gastos_bp.route("/", methods=["GET"])
@admin_required
def get_expenses():
    tenant_id = current_user.tenant_id
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            # Allows filtering by month and year, e.g., /gastos?month=10&year=2023
            month = request.args.get('month', type=int)
            year = request.args.get('year', type=int)

            # 💡 SAAS-IFICATION: Filter expenses by the logged-in user's tenant_id.
            query = "SELECT * FROM gastos WHERE tenant_id = %s"
            params = [tenant_id]
            
            if month and year:
                query += " AND EXTRACT(MONTH FROM fecha) = %s AND EXTRACT(YEAR FROM fecha) = %s"
                params.extend([month, year])
            
            query += " ORDER BY fecha DESC"
            
            cursor.execute(query, tuple(params))
            expenses_raw = cursor.fetchall()
            # FIX: Convert to dict to ensure JSON serialization and that the table is displayed.
            expenses = [dict(g) for g in expenses_raw]
            # Convert date objects to string for JSON serialization
            for expense in expenses:
                if isinstance(expense.get('fecha'), datetime.date):
                    expense['fecha'] = expense['fecha'].isoformat()
            return jsonify(expenses)
    except Exception as e:
        current_app.logger.error(f"Error in get_expenses: {e}")
        return jsonify({"error": "Error fetching expenses"}), 500

@gastos_bp.route("/", methods=["POST"])
@admin_required
def add_expense():
    data = request.get_json()
    description = data.get("descripcion")
    amount = data.get("monto")
    date = data.get("fecha")
    tenant_id = current_user.tenant_id
    category = data.get("categoria", "Miscellaneous")

    if not description or not amount or not date:
        return jsonify({"error": "Description, amount, and date are required"}), 400

    conn = get_db()
    try:
        with conn.cursor() as cursor:
            # 💡 SAAS-IFICATION: Insert the tenant_id when creating a new expense.
            cursor.execute("""
                INSERT INTO gastos (descripcion, monto, categoria, fecha, tenant_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (description, amount, category, date, tenant_id))
            conn.commit()
            register_log(f"Registered new expense: {description} for ${amount}")
            return jsonify({"message": "Expense registered successfully"}), 201
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error in add_expense: {e}")
        return jsonify({"error": "Error registering expense"}), 500

@gastos_bp.route("/<int:id>", methods=["PUT"])
@admin_required
def update_expense(id):
    tenant_id = current_user.tenant_id
    data = request.get_json()
    description = data.get("descripcion")
    amount = data.get("monto")
    date = data.get("fecha")
    category = data.get("categoria")

    if not all([description, amount, date, category]):
        return jsonify({"error": "Description, amount, date, and category are required"}), 400

    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE gastos 
                SET descripcion=%s, monto=%s, categoria=%s, fecha=%s
                WHERE id_gasto=%s AND tenant_id=%s
            """, (description, amount, category, date, id, tenant_id))
            
            if cursor.rowcount == 0:
                return jsonify({"error": "Expense not found or does not belong to your organization"}), 404

            conn.commit()
            register_log(f"Updated expense ID {id}: {description}")
            return jsonify({"message": "Expense updated successfully"})
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error in update_expense: {e}")
        return jsonify({"error": "Error updating expense"}), 500

@gastos_bp.route("/<int:id>", methods=["DELETE"])
@admin_required
def delete_expense(id):
    tenant_id = current_user.tenant_id
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            # 💡 SAAS-IFICATION: Ensure only an expense from the correct tenant can be deleted.
            cursor.execute("DELETE FROM gastos WHERE id_gasto=%s AND tenant_id = %s", (id, tenant_id))
            
            if cursor.rowcount == 0:
                return jsonify({"error": "Expense not found or does not belong to your organization"}), 404

            conn.commit()
            register_log(f"Deleted expense ID {id}")
            return jsonify({"message": "Expense deleted successfully"})
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error in delete_expense: {e}")
        return jsonify({"error": "Error deleting expense"}), 500