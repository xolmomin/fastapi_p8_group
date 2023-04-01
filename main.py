from itertools import chain

import uvicorn
from fastapi import Depends, FastAPI
from sqlalchemy import select
from sqlalchemy.orm import Session

from apps import models, routes
from apps.hashing import Hasher
from config.celery_utils import create_celery
from config.db import engine, get_db
from config.settings import settings, manager

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION
)
app.celery_app = create_celery()

celery = app.celery_app


def generate_fake_users():
    '''
    generate fake users
    :return:
    '''
    # from faker import Faker
    # faker = Faker()
    # db = next(get_db())

    # users = []
    # for _ in range(10):  # CLIENT
    #     users.append(
    #         models.Users(
    #             name=faker.name(),
    #             type='CLIENT',
    #             email=faker.email(),
    #             is_active=True,
    #             password=Hasher.make_hash('1')
    #         )
    #     )
    # for _ in range(5):  # VIP CLIENT
    #     users.append(
    #         models.Users(
    #             name=faker.name(),
    #             type='VIP_CLIENT',
    #             email=faker.email(),
    #             is_active=True,
    #             password=Hasher.make_hash('1')
    #         )
    #     )
    # for _ in range(4):  # VIP CLIENT
    #     users.append(
    #         models.Users(
    #             name=faker.name(),
    #             type='ADMIN',
    #             email=faker.email(),
    #             is_active=True,
    #             password=Hasher.make_hash('1')
    #         )
    #     )
    # db.add_all(users)
    # db.commit()


@app.on_event('startup')
def startup_event():
    # models.Base.metadata.drop_all(engine)
    # models.Base.metadata.create_all(engine)
    app.include_router(routes.post)
    app.include_router(routes.router)
    app.include_router(routes.user)
    app.include_router(routes.auth)
    generate_fake_users()


@manager.user_loader()
def load_user(email: str):
    db = next(get_db())
    user = db.query(models.Users).where(models.Users.email == email, models.Users.is_active).first()
    db.close()
    return user


@app.on_event('shutdown')
def shutdown_event():
    pass


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
