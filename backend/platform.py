import os
import threading
from flask import Blueprint, jsonify, current_app, request
from flask_login import login_required, current_user
from db import get_db
from psycopg2.extras import DictCursor
from utils import admin_required
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail as SendGridMail

platform_bp = Blueprint("platform_bp", __name__, url_prefix="/platform")

@platform_bp.route("/contact-support", methods=["POST"])
@login_required
@admin_required # Cualquier admin puede contactar a soporte
def contact_support():
    """
    Permite a un admin de cualquier tenant enviar una solicitud de soporte
    al email del superadmin de la plataforma.
    """
    data = request.json
    subject = data.get('subject')
    message_body = data.get('message')

    if not subject or not message_body:
        return jsonify({"error": "El asunto y el mensaje son obligatorios"}), 400

    # Obtenemos el contexto del usuario y su tenant
    user = current_user
    conn = get_db()
    with conn.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute("SELECT nombre FROM tenants WHERE id_tenant = %s", (user.tenant_id,))
        tenant_name = cursor.fetchone()['nombre']

    # Preparamos el email para ser enviado al email de soporte de la plataforma
    support_email_address = os.getenv('SUPPORT_EMAIL_ADDRESS')
    if not support_email_address:
        current_app.logger.error("La variable de entorno SUPPORT_EMAIL_ADDRESS no está configurada.")
        return jsonify({"error": "El servicio de soporte no está disponible en este momento."}), 500

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
                app.logger.info(f"✅ HILO: Correo de soporte enviado a {recipient}.")
            except Exception as e:
                app.logger.error(f"❌ HILO: Error enviando correo de soporte: {e}", exc_info=True)

    email_subject = f"[Soporte Precivox] - {subject} (Tenant: {tenant_name})"
    html_content = f"""
        <h2>Nueva solicitud de soporte</h2>
        <p><strong>Tenant:</strong> {tenant_name} (ID: {user.tenant_id})</p>
        <p><strong>Usuario:</strong> {user.nombre} ({user.email})</p>
        <hr>
        <h3>Mensaje:</h3>
        <p style="white-space: pre-wrap; background-color: #f5f5f5; padding: 15px; border-radius: 5px;">{message_body}</p>
    """

    thread = threading.Thread(target=send_async_email, args=(current_app._get_current_object(), support_email_address, email_subject, html_content))
    thread.start()

    return jsonify({"mensaje": "Tu solicitud de soporte ha sido enviada. Nos pondremos en contacto contigo pronto."}), 200