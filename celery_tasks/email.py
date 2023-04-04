from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from celery import shared_task

from apps import models
from apps.utils.send_email import __send_email_message
from config.settings import settings


@shared_task
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
