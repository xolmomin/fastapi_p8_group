from itertools import chain
from random import choice

from celery import shared_task
from faker import Faker
from sqlalchemy import select
from sqlalchemy.orm import Session

from apps import models
from config.db import get_db


@shared_task
def generate_posts(n: int):
    db: Session = next(get_db())
    result = db.execute(select(models.Users.id).where(models.Users.status == models.Users.Status.ADMIN.name))
    users_id = tuple(chain(*result))
    fake = Faker()
    posts = []
    for _ in range(n):
        posts.append(
            models.Post(
                title=fake.name(),
                description=' '.join(fake.sentences(nb=150)),
                is_premium=choice((True, False)),
                author_id=choice(users_id)
            )
        )
    db.add_all(posts)
    db.commit()
    db.close()
    print("Successfully added posts !")


@shared_task()
def delete_all_post_worker():
    db = next(get_db())
    try:
        db.query(models.Post).delete()
        db.commit()
        print('Successfully deleted !')
    except:
        db.rollback()
