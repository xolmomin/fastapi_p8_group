from celery import shared_task

from apps.api import universities
from apps.utils import send_email


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
def async_send_email(email: str, code: int):
    send_email(email, str(code))
