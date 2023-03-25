import math
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from starlette import status

from apps import models
from apps.hashing import Hasher
from apps.schemas import User, UserInDB
from config.authentication import oauth2_scheme
from config.db import get_db
from config.settings import settings


def get_user(db, email: str):
    user = db.query(models.Users).filter_by(email=email).first()
    if user:
        return UserInDB(**user.__dict__)


def authenticate_user(db, email: str, password: str):
    user = get_user(db, email)
    if not user:
        return False
    if not Hasher.check_hash(password, user.password):
        return False
    return user


def get_access_token_by_refresh_token(db: Session, refresh_token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY)
        email: str = payload.get('sub')
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user(db, email)
    access_token = create_access_token(user.email)
    if user is None:
        raise credentials_exception
    return access_token


def create_access_token(email: str):
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        'type': 'access',
        'sub': email,
        'exp': expire
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY)
    return encoded_jwt

def create_refresh_token(email: str):
    expire = datetime.utcnow() + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    payload = {
        'sub': email,
        'type': 'refresh',
        'exp': expire
    }
    encoded_jwt = jwt.encode(payload, settings.SECRET_KEY)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY)
        email: str = payload.get('sub')
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(db, email)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Inactive user'
        )
    return current_user
