import os
import shutil

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy import update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from starlette import status

from apps import models, schemas
from config.db import get_db

user = APIRouter(tags=['user'])


async def get_or_404(db: Session, model, **kwargs):
    try:
        return db.query(model).filter_by(**kwargs).one()
    except NoResultFound as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, e)


@user.post('/users')
async def add_user(
        form: schemas.UserForm = Depends(schemas.UserForm.as_form),
        db: Session = Depends(get_db)
):
    form = form.dict(exclude_unset=True)
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


@user.patch('/users/{pk}')
async def update_user(
        pk: int,
        form: schemas.UpdateUser = Depends(schemas.UpdateUser.as_form),
        db: Session = Depends(get_db)
):
    user = await get_or_404(db, models.Users, id=pk)
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


@user.get('/users')
async def get_users(db: Session = Depends(get_db)):
    return db.query(models.Users).all()


@user.get('/users/{pk}')
async def get_user(pk: int, db: Session = Depends(get_db)):
    return db.query(models.Users).filter_by(id=pk).first()


@user.delete('/users/{pk}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(pk: int, db: Session = Depends(get_db)):
    user = await get_or_404(db, models.Users, id=pk)
    db.delete(user)
    db.commit()
