import os

from dotenv import load_dotenv
from fastapi_login import LoginManager

load_dotenv('.env')


class Settings:
    PROJECT_NAME: str = "FastApi api"
    PROJECT_DESCRIPTION: str = "yangi projectimiz"
    PROJECT_VERSION: str = "1.0.0"
    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", 5432)
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "tdd")
    PG_URL: str = f'{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}'
    DATABASE_URL: str = f"postgresql+psycopg2://{PG_URL}"
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", f'db+postgresql://{PG_URL}')

    SECRET_KEY: str = os.getenv('SECRET_KEY')
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # in mins
    DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # in mins
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 120  # in mins

    TEST_USER_EMAIL: str = 'test@example.com'
    SMTP_HOST: str = os.getenv('SMTP_HOST')
    SMTP_PORT: str = os.getenv('SMTP_PORT')
    SMTP_EMAIL: str = os.getenv('SMTP_EMAIL')
    SMTP_PASSWORD: str = os.getenv('SMTP_PASSWORD')
    ESKIZ_EMAIL: str = os.getenv('ESKIZ_EMAIL')
    ESKIZ_PASSWORD: str = os.getenv('ESKIZ_PASSWORD')


settings = Settings()

manager = LoginManager(settings.SECRET_KEY, '/login', use_cookie=True)
