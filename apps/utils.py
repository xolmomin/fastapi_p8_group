import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from random import randint

import httpx

from config.settings import settings


def generate_number():
    return randint(100000, 999999)


def __send_email(receiver_mail: str, msg):
    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_EMAIL, settings.SMTP_PASSWORD)
        server.sendmail(settings.SMTP_EMAIL, receiver_mail, msg.as_string())


def send_email(email: str, code: str):
    message = MIMEMultipart()
    message['Subject'] = 'Activation code'
    message['From'] = settings.SMTP_EMAIL
    message['To'] = email
    message.attach(MIMEText(code, 'plain'))
    __send_email(email, message)


def send_message(phone: str, msg: str = None):
    url = 'https://notify.eskiz.uz/api/message/sms/send'

    code: int = generate_number()
    payload = {
        'mobile_phone': '998' + phone,
        'message': msg if msg else code,
        'from': '4546'
    }
    is_auth, token = auth_eskiz()
    if not is_auth:
        raise ValueError('Xatolik bor!')

    headers = {
        'Authorization': f'Bearer {token}'
    }

    response = httpx.post(url, headers=headers, data=payload)

    print(response.text)
    return code, response.text


def auth_eskiz():
    url = "https://notify.eskiz.uz/api/auth/login"

    payload = {
        'email': settings.ESKIZ_EMAIL,
        'password': settings.ESKIZ_PASSWORD
    }

    response = httpx.post(url, data=payload)

    if response.status_code == 200:
        return True, response.json()['data']['token']
    return False, response.text

