import smtplib
import os
from email.mime.text import MIMEText

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

def send_email(payload: dict):
    msg = MIMEText(payload["body"])
    msg["Subject"] = payload["subject"]
    msg["From"] = SMTP_USER
    msg["To"] = payload["to"]

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)

    return {"status": "Email sent successfully"}
