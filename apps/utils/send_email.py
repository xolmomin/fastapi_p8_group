import base64
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from celery import shared_task

from apps import models
from config.settings import settings


def __send_email_message(msg):
    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_EMAIL, settings.SMTP_PASSWORD)
        server.send_message(msg)


def encode_data(pk):
    return base64.urlsafe_b64encode(str(pk).encode('utf-8'))


def decode_data(uid):
    return base64.urlsafe_b64decode(uid).decode('utf-8')


@shared_task()
def send_verification_email(user: models.Users, verify_code: str) -> None:
    message = MIMEMultipart()
    message['Subject'] = 'Activation Code'
    message['From'] = settings.SMTP_EMAIL
    message['To'] = user.email
    html = f"""\
    <html>
      <body>
      <h1>
      Hi {user.name} 
      </h1>
      <br>
      <h2>
      Activate verify code your account 👇 
      <br>
      <b><code>{verify_code}</code></b>
      </h2>
    </html> 
    """
    message.attach(MIMEText(html, 'html'))
    __send_email_message(message)
