from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apps import schemas
from apps.forms import CustomOAuth2PasswordRequestForm
from apps.schemas import Login, VerifyForm, AgainVerifyForm
from apps.services.auth import (get_access_token_by_refresh_token,
                                get_current_activate_user, login_create_token, save_register_user,
                                check_verify_code_worker, again_send_code_email_worker)
from config.db import get_db

auth = APIRouter(tags=['auth'])


@auth.post('/register')
async def add_user(
        form: schemas.RegisterForm = Depends(schemas.RegisterForm.as_form),
        db: Session = Depends(get_db)
):
    response = await save_register_user(db, form)
    return response


@auth.post('/verify-check', description='verify check')
async def verify_check(form: VerifyForm = Depends(VerifyForm.as_form)):
    verify_email, verify_code = form.email, form.verify_code
    result = await check_verify_code_worker(verify_email, verify_code)
    return result


@auth.post('/again-verify-code', description='again verify email code')
async def again_send_code_email(form: AgainVerifyForm = Depends(AgainVerifyForm.as_form)):
    verify_email = form.email
    result = await again_send_code_email_worker(verify_email)
    return result


@auth.post('/login', response_model=Login)
async def login_for_access_token(
        form_data: CustomOAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    result = await login_create_token(form_data, db)
    return result


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


@auth.get('/user/me/', response_model=schemas.User)
async def read_user_me(current_user: schemas.User = Depends(get_current_activate_user)):
    return current_user

# @auth.get('/users/me/items/')
# async def read_own_items(current_user: schemas.User = Depends(get_current_activate_user)):
#     response = [
#         {
#             'item_id': 'Foo',
#             'owner': current_user.email
#         }
#     ]
#     return response
