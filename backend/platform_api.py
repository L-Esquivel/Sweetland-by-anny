import os
import threading
from flask import Blueprint, jsonify, current_app, request
from flask_login import login_required, current_user
from db import get_db
from psycopg2.extras import DictCursor
from utils import admin_required, superadmin_required
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail as SendGridMail

platform_bp = Blueprint("platform_bp", __name__, url_prefix="/platform")

@platform_bp.route("/contact-support", methods=["POST"])
@login_required
@admin_required # Any admin can contact support
def contact_support():
    """
    Allows an admin from any tenant to send a support request
    to the platform's superadmin email.
    """
    data = request.json
    subject = data.get('subject')
    message_body = data.get('message')

    if not subject or not message_body:
        return jsonify({"error": "Subject and message are required"}), 400

    # Get the user and tenant context
    user = current_user
    conn = get_db()
    with conn.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute("SELECT nombre FROM tenants WHERE id_tenant = %s", (user.tenant_id,))
        tenant_name = cursor.fetchone()['nombre']

    # Prepare the email to be sent to the platform's support email address
    support_email_address = os.getenv('SUPPORT_EMAIL_ADDRESS')
    if not support_email_address:
        current_app.logger.error("The SUPPORT_EMAIL_ADDRESS environment variable is not set.")
        return jsonify({"error": "The support service is currently unavailable."}), 500

    def send_async_email(app, recipient, subject, html_content):
        with app.app_context():
            message = SendGridMail(
                from_email=os.getenv('SENDER_EMAIL'),
                to_emails=recipient,
                subject=subject,
                html_content=html_content
            )
            try:
                sendgrid_client = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
                sendgrid_client.send(message)
                app.logger.info(f"✅ THREAD: Support email sent to {recipient}.")
            except Exception as e:
                app.logger.error(f"❌ THREAD: Error sending support email: {e}", exc_info=True)

    email_subject = f"[Precivox Support] - {subject} (Tenant: {tenant_name})"
    html_content = f"""
        <h2>New Support Request</h2>
        <p><strong>Tenant:</strong> {tenant_name} (ID: {user.tenant_id})</p>
        <p><strong>User:</strong> {user.nombre} ({user.email})</p>
        <hr>
        <h3>Message:</h3>
        <p style="white-space: pre-wrap; background-color: #f5f5f5; padding: 15px; border-radius: 5px;">{message_body}</p>
    """

    thread = threading.Thread(target=send_async_email, args=(current_app._get_current_object(), support_email_address, email_subject, html_content))
    thread.start()

    return jsonify({"message": "Your support request has been sent. We will contact you shortly."}), 200

@platform_bp.route("/dashboard-stats", methods=["GET"])
@login_required
@superadmin_required
def get_platform_stats():
    """
    Returns global platform statistics for the Super Admin dashboard.
    """
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            # Total Tenants
            cursor.execute("SELECT COUNT(*) as total FROM tenants")
            total_tenants = cursor.fetchone()['total']

            # New Tenants in the last 30 days
            cursor.execute("SELECT COUNT(*) as total FROM tenants WHERE fecha_creacion >= NOW() - INTERVAL '30 days'")
            new_tenants_30_days = cursor.fetchone()['total']

            # Total Users on the platform
            cursor.execute("SELECT COUNT(*) as total FROM usuarios")
            total_users = cursor.fetchone()['total']

            # FIX: Platform revenue is now calculated from tenant payments,
            # not from the sum of their sales.
            cursor.execute("SELECT SUM(amount) as total_revenue FROM tenant_payments")
            total_revenue_raw = cursor.fetchone()
            total_revenue = float(total_revenue_raw['total_revenue'] or 0)

            return jsonify({
                "total_tenants": total_tenants,
                "new_tenants_30_days": new_tenants_30_days,
                "total_users": total_users,
                "total_revenue": total_revenue,
            })
    except Exception as e:
        current_app.logger.error(f"Error en get_platform_stats: {e}")
        return jsonify({"error": "Error fetching platform statistics"}), 500