from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required
from utils import superadmin_required
from db import get_db
from psycopg2.extras import DictCursor

payments_bp = Blueprint("payments_bp", __name__, url_prefix="/payments")

@payments_bp.route("/tenant/<int:tenant_id>", methods=["GET"])
@superadmin_required
def get_payments_for_tenant(tenant_id):
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(
                "SELECT id_payment, amount, payment_date, notes FROM tenant_payments WHERE tenant_id = %s ORDER BY payment_date DESC",
                (tenant_id,)
            )
            payments = [dict(p) for p in cursor.fetchall()]
            for p in payments:
                p['amount'] = float(p['amount'])
                p['payment_date'] = p['payment_date'].isoformat()
            return jsonify(payments)
    except Exception as e:
        current_app.logger.error(f"Error getting payments for tenant {tenant_id}: {e}")
        return jsonify({"error": "Error fetching payments"}), 500

@payments_bp.route("/", methods=["POST"])
@superadmin_required
def add_payment():
    data = request.json
    tenant_id = data.get('tenant_id')
    amount = data.get('amount')
    payment_date = data.get('payment_date')
    notes = data.get('notes', '')

    if not all([tenant_id, amount, payment_date]):
        return jsonify({"error": "Required fields are missing"}), 400

    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO tenant_payments (tenant_id, amount, payment_date, notes) VALUES (%s, %s, %s, %s)",
                (tenant_id, amount, payment_date, notes)
            )
            conn.commit()
            return jsonify({"message": "Payment registered successfully"}), 201
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error adding payment: {e}")
        return jsonify({"error": "Error registering payment"}), 500

@payments_bp.route("/<int:payment_id>", methods=["DELETE"])
@superadmin_required
def delete_payment(payment_id):
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM tenant_payments WHERE id_payment = %s", (payment_id,))
            conn.commit()
            if cursor.rowcount == 0:
                return jsonify({"error": "Payment not found"}), 404
            return jsonify({"message": "Payment deleted successfully"})
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error deleting payment: {e}")
        return jsonify({"error": "Error deleting payment"}), 500