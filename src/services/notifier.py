import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


def send_email(subject: str, body: str):
    """
    Envía un email de notificación usando Gmail SMTP.
    
    Variables de entorno necesarias:
    - SMTP_EMAIL: tu email de Gmail
    - SMTP_PASSWORD: App Password de Gmail (no tu contraseña normal)
    - NOTIFY_EMAIL: email destino (puede ser el mismo)
    """
    smtp_email = os.getenv("SMTP_EMAIL")
    smtp_password = os.getenv("SMTP_PASSWORD")
    notify_email = os.getenv("NOTIFY_EMAIL", smtp_email)
    
    if not smtp_email or not smtp_password:
        print("⚠️  Notificaciones desactivadas (SMTP_EMAIL o SMTP_PASSWORD no configurados)")
        return False
    
    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_email
        msg['To'] = notify_email
        msg['Subject'] = f"🎰 Primitiva Check: {subject}"
        
        # Añadir timestamp al body
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_body = f"{body}\n\n---\nEnviado: {timestamp}"
        
        msg.attach(MIMEText(full_body, 'plain'))
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(smtp_email, smtp_password)
            server.send_message(msg)
        
        print(f"📧 Email enviado: {subject}")
        return True
        
    except Exception as e:
        print(f"❌ Error enviando email: {e}")
        return False


def notify_error(error_message: str):
    """Notifica un error crítico."""
    send_email(
        subject="❌ Error en ejecución",
        body=f"Se ha producido un error:\n\n{error_message}"
    )


def notify_success(summary: str):
    """Notifica ejecución exitosa (opcional, para debug)."""
    send_email(
        subject="✅ Ejecución completada",
        body=summary
    )


def notify_blocked():
    """Notifica que la IP ha sido bloqueada."""
    send_email(
        subject="🚨 IP BLOQUEADA",
        body="El scraper ha detectado un bloqueo de Akamai/Cloudflare.\n\n"
             "La IP del servidor probablemente está en lista negra.\n"
             "Opciones:\n"
             "1. Cambiar la IP del servidor\n"
             "2. Usar un proxy residencial\n"
             "3. Ejecutar manualmente desde local"
    )
