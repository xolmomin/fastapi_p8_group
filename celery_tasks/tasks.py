import os
import time

from celery import shared_task

from apps.api import universities
from apps.utils.send_email import send_verification_email


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 5},
             name='universities:get_all_universities_task')
def get_all_universities_task(self, countries: list[str]):
    data: dict = {}
    for cnt in countries:
        data.update(universities.get_all_universities_for_country(cnt))
    return data


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 5},
             name='university:get_university_task')
def get_university_task(self, country: str):
    university = universities.get_all_universities_for_country(country)
    return university


@shared_task
def calculate():
    time.sleep(50)
    return 1


@shared_task
def register1():
    return 'sent email'


@shared_task
def async_send_email(user, host):
    send_verification_email(user['email'], user['name'], host)
    return 'sent email'


# from celery import Celery
#
# celery = Celery(__name__)
#
# celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
# celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")
#
#
# @celery.task(name='create_task')
# def async_send_email(user, host):
#     send_verification_email(user['email'], user['name'], host)
#     return 'sent email'

# memory, cpu
# speed
