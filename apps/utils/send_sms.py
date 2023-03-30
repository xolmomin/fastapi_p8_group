import os
import httpx
from dotenv import load_dotenv

from apps.utils.generate import generate_number

load_dotenv('.env')


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
    return response.text


def auth_eskiz():
    url = "https://notify.eskiz.uz/api/auth/login"

    payload = {
        'email': os.getenv('ESKIZ_EMAIL'),
        'password': os.getenv('ESKIZ_PASSWORD')
    }

    response = httpx.post(url, data=payload)

    if response.status_code == 200:
        return True, response.json()['data']['token']
    return False, response.text


number = '976749997'
message = 'JAvohir'
# send_message(message, number)
