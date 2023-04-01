from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from apps import schemas
from apps.services.user import (_delete_user, _get_user, get_all_users,
                                save_user, update_user_save)
from config.db import get_db

user = APIRouter(tags=['user'])


@user.post('/users')
async def add_user(
        form: schemas.UserForm = Depends(schemas.UserForm.as_form),
        db: Session = Depends(get_db)
):
    user = await save_user(db, form)
    return user


@user.patch('/users/{pk}')
async def update_user(
        pk: int,
        form: schemas.UpdateUser = Depends(schemas.UpdateUser.as_form),
        db: Session = Depends(get_db)
):
    user = await update_user_save(pk, form, db)
    return user


@user.get('/users')
async def get_users(db: Session = Depends(get_db)):
    users = await get_all_users(db)
    return users


@user.get('/user/{pk}')
async def get_user(pk: int, db: Session = Depends(get_db)):
    user = await _get_user(db, pk)
    return user


@user.delete('/users/{pk}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(pk: int, db: Session = Depends(get_db)):
    await _delete_user(pk, db)
