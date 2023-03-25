
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from apps import schemas
from apps.forms import CustomOAuth2PasswordRequestForm
from apps.schemas import Token, User
from apps.services import (authenticate_user, create_access_token,
                           get_current_active_user)
from apps.services.auth import (create_refresh_token,
                                get_access_token_by_refresh_token)
from config.db import get_db

auth = APIRouter(tags=['auth'])


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
