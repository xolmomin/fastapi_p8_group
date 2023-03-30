from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import UJSONResponse
from pydantic import Field
from sqlalchemy import update
from sqlalchemy.orm import Session
from starlette import status

from apps import models, schemas
from apps.forms import CustomOAuth2PasswordRequestForm
from apps.schemas import Token, User, UserData
from apps.services import (authenticate_user, create_access_token,
                           get_current_active_user)
from apps.services.auth import (create_refresh_token,
                                get_access_token_by_refresh_token)
from apps.utils import generate_number, send_message
from celery_tasks.tasks import async_send_email
from config.db import get_db

auth = APIRouter(tags=['auth'])


@auth.post('/register')
async def register(
        db: Session = Depends(get_db),
        form: schemas.RegisterForm = Depends(schemas.RegisterForm.as_form)
):
    form = form.dict(exclude_unset=True)

    code = generate_number()
    user_ = models.Users(**form)
    db.add(user_)
    db.commit()

    data = {
        'code': code,
        'user_id': user_.id,
    }
    db.add(models.Verification(**data))
    db.commit()
    async_send_email.delay(form['email'], code)
    return UJSONResponse({'message': 'success'})


@auth.post('/verify-account')
async def verification_code(
        form: schemas.VerificationForm = Depends(schemas.VerificationForm.as_form),
        db: Session = Depends(get_db)
):
    user = db.query(models.Users).filter_by(email=form.email, is_active=False).first()

    verify = db.query(models.Verification).where(
        models.Verification.user == user,
        models.Verification.code == form.code,
        models.Verification.type == models.Verification.VerifyType.EMAIL
    ).first()

    if not verify:
        raise HTTPException(400, "Doesn't match verification")

    user.is_active = True
    db.commit()
    return UJSONResponse({'message': 'success'})


@auth.post('/verify-send-code')
async def verification_phone(
        phone: int,
        current_user: UserData = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    phone = '998' + str(phone)
    current_user.phone = phone
    current_user.is_verified_phone = False
    query = update(models.Users).values(phone=phone, is_verified_phone=False).where(models.Users.id == current_user.id)
    db.execute(query)
    db.commit()
    code = 123
    # code, status = send_message(str(phone))
    data = {
        'user_id': current_user.id,
        'type': models.Verification.VerifyType.PHONE,
    }
    verification = db.query(models.Verification).filter_by(**data).first()
    if verification:
        verification.code = code
    else:
        db.add(models.Verification(**data, code=code))
    db.commit()
    return UJSONResponse({'message': 'Send code!'})


@auth.post('/verify-phone')
async def verification_phone(
        form: schemas.VerificationPhoneForm = Depends(schemas.VerificationPhoneForm.as_form),
        db: Session = Depends(get_db)
):
    user = db.query(models.Users).filter_by(phone=form.phone).first()

    verify = db.query(models.Verification).where(
        models.Verification.user == user,
        models.Verification.code == form.code,
        models.Verification.type == models.Verification.VerifyType.PHONE
    ).first()

    if not verify:
        raise HTTPException(400, "Doesn't match verification")

    user.is_verified_phone = True
    db.commit()
    return status.HTTP_200_OK


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
