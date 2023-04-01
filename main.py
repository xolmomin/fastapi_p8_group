import uvicorn
from fastapi import FastAPI

from apps import routes, models
from apps.services.user import generate_fake_users

from config.celery_utils import create_celery
from config.db import engine
from config.settings import settings

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
async def startup_event():
    # models.Base.metadata.drop_all(engine)
    # models.Base.metadata.create_all(engine)
    app.include_router(routes.post)
    app.include_router(routes.auth)
    app.include_router(routes.user)

    # await generate_fake_users()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
