import base64
import smtplib

from config.settings import settings


def __send_email_message(msg):
    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_EMAIL, settings.SMTP_PASSWORD)
        server.send_message(msg)


def encode_data(pk):
    return base64.urlsafe_b64encode(str(pk).encode('utf-8'))


def decode_data(uid):
    return base64.urlsafe_b64decode(uid).decode('utf-8')
