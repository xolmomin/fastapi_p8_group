import os
import shutil

from faker import Faker
from fastapi import HTTPException, status
from sqlalchemy import update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from apps import models, schemas
from apps.hashing import Hasher
from config.db import get_db


async def get_or_404(db: Session, Users, pk: int):
    try:
        return db.query(Users).filter_by(id=pk).one()
    except NoResultFound as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, e)


async def save_user(db: Session, form: schemas.UserForm):
    form: dict = form.dict(exclude_unset=True)
    image = form.get('image')
    if image:
        folder = 'media/users/'
        file_url = folder + image.filename
        if not os.path.exists(folder):
            os.mkdir(folder)
        with open(file_url, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        form['image'] = file_url
    user = models.Users(**form)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


async def update_user_save(
        pk: int,
        form: schemas.UpdateUser,
        db: Session
):
    user = await get_or_404(db, models.Users, pk)
    form = form.dict(exclude_none=True)
    image = form.get('image')
    if image:
        folder = 'media/users/'
        file_url = folder + image.filename
        if not os.path.exists(folder):
            os.mkdir(folder)
        with open(file_url, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        form['image'] = file_url
    query = update(models.Users).filter_by(id=pk).values(**form)
    db.execute(query)
    db.commit()
    db.refresh(user)
    return user


async def get_all_users(db: Session):
    users = db.query(models.Users).all()
    return users


async def _get_user(db: Session, pk: int):
    user = db.query(models.Users).filter_by(id=pk).first()
    return user


async def _delete_user(pk: int, db: Session):
    user = await get_or_404(db, models.Users, pk)
    db.delete(user)
    db.commit()
    return user


async def generate_fake_users():
    faker = Faker()
    db = next(get_db())
    users = []
    for _ in range(10):  # CLIENT
        users.append(
            models.Users(
                name=faker.name(),
                status='CLIENT',
                email=faker.email(),
                is_active=True,
                password=Hasher.make_hash('1')
            )
        )
    for _ in range(5):  # VIP CLIENT
        users.append(
            models.Users(
                name=faker.name(),
                status='VIP_CLIENT',
                email=faker.email(),
                is_active=True,
                password=Hasher.make_hash('1')
            )
        )
    for _ in range(4):  # ADMIN
        users.append(
            models.Users(
                name=faker.name(),
                status='ADMIN',
                email=faker.email(),
                is_active=True,
                password=Hasher.make_hash('1')
            )
        )
    db.add_all(users)
    db.commit()
    db.close()
