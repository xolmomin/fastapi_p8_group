import os
import shutil
from itertools import chain
from random import choice
from time import time

from faker import Faker
from fastapi import APIRouter, HTTPException,Request
from fastapi.params import Depends
from sqlalchemy import select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from starlette import status
from starlette.background import BackgroundTasks

from apps import models, schemas
from apps.forms import CustomOAuth2PasswordRequestForm
from apps.models import Users
from apps.services import authenticate_user
from config.db import get_db
from config.settings import manager

post = APIRouter(tags=['post'])


def _generate_posts(db: Session, n: int) -> None:

    result = db.execute(select(models.Users.id).where(models.Users.type == models.Users.Type.ADMIN.name))
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
    print('Qoshildi')

    # celery - redis, rabbitmq


@post.post('/posts')
async def add_post(
        n: int,
        background: BackgroundTasks,
        db: Session = Depends(get_db),
):
    background.add_task(_generate_posts, db, n)
    return {'message': 'Successfully added posts!'}



@post.get('/product')
async def get_product(
        current_user=Depends(manager),
        db: Session = Depends(get_db)
):
    if current_user.type != models.Users.Type.CLIENT:
        return db.query(models.Post).all()
    else:
        data = db.query(models.Post).filter(models.Post.is_premium == False).all()
        return data


@post.delete('/product/{id}')
async def delete_post(
        id: int,
        current_user = Depends(manager),
        db: Session = Depends(get_db)
):
    product = db.query(models.Post).filter(id == models.Post.id).first()
    if not product:
        return 'there is not product'
    elif current_user.id == product.author_id:
        db.delete(product)
        db.commit()
        return {'message': 'Successfully Deleted'}
    else:
        return 'you can not deleted'


# @post.patch('/posts/{pk}')
# async def update_post(
#         pk: int,
#         form: schemas.UpdateUser = Depends(schemas.UpdateUser.as_form),
#         db: Session = Depends(get_db)
# ):
#     post = await get_or_404(db, models.Users, id=pk)
#     form = form.dict(exclude_none=True)
#     image = form.get('image')
#     if image:
#         folder = 'media/posts/'
#         file_url = folder + image.filename
#         if not os.path.exists(folder):
#             os.mkdir(folder)
#         with open(file_url, "wb") as buffer:
#             shutil.copyfileobj(image.file, buffer)
#         form['image'] = file_url
#     query = update(models.Users).filter_by(id=pk).values(**form)
#     db.execute(query)
#     db.commit()
#     db.refresh(post)
#     return post
#
#
# @post.get('/posts')
# async def get_posts(db: Session = Depends(get_db)):
#     return db.query(models.Users).all()
#
#
# @post.get('/posts/{pk}')
# async def get_post(pk: int, db: Session = Depends(get_db)):
#     return db.query(models.Users).filter_by(id=pk).first()
#
#
# @post.delete('/posts/{pk}', status_code=status.HTTP_204_NO_CONTENT)
# async def delete_post(pk: int, db: Session = Depends(get_db)):
#     post = await get_or_404(db, models.Users, id=pk)
#     db.delete(post)
#     db.commit()
