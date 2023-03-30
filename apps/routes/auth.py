from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import UJSONResponse
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import Response

from apps import schemas, models
from apps.forms import CustomOAuth2PasswordRequestForm
from apps.schemas import Token, User
from apps.services import (authenticate_user, create_access_token,
                           get_current_active_user)
from apps.services.auth import (create_refresh_token,
                                get_access_token_by_refresh_token)
from apps.utils import send_sms
from config.db import get_db

auth = APIRouter(tags=['auth'])


@auth.post('/register')
async def register(
        db: Session = Depends(get_db),
        form: schemas.RegisterForm = Depends(schemas.RegisterForm.as_form)
):
    data = form.dict(exclude_unset=True)
    task = get_ver_code_task.apply_async(args=[(data.get('email'), data.get('ver_code'))])
    user_ = models.Users(**data)
    db.add(user_)
    db.commit()
    return UJSONResponse({'message': 'success'})


# @auth.post('/verification_code')
# async def verification_code(form: schemas.VerificationForm = Depends(schemas.VerificationForm.as_form),
#                             db: Session = Depends(get_db)):
#     user_ = db.query(models.Users).where(models.Users.email == form.email,
#                                          models.Users.ver_code == form.ver_code).first()
#     if not user_:
#         raise status.HTTP_422_UNPROCESSABLE_ENTITY
#     user_.is_active = True
#     db.commit()
#     return status.HTTP_202_ACCEPTED


@auth.post('/token', response_model=Token)
async def login_for_access_token(form_data: CustomOAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.email, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(user.email)
    refresh_token = create_refresh_token(user.email)
    response = {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'bearer'
    }
    return response


@auth.post('/refresh-token', response_model=schemas.ResponseRefreshToken, summary='get access token')
async def login_for_access_token(
        form: schemas.RefreshToken,
        db: Session = Depends(get_db)
):
    access_token = get_access_token_by_refresh_token(db, form.refresh_token)
    response = {
        'access_token': access_token,
        'token_type': 'bearer'
    }
    return response


@auth.get('/users/me/', response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@auth.get("/users/me/items/")
async def read_own_items(current_user: User = Depends(get_current_active_user)):
    return [{"item_id": "Foo", "owner": current_user.email}]
