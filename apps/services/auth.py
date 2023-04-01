from datetime import datetime, timedelta
from random import randint

from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from apps import models
from apps.forms import CustomOAuth2PasswordRequestForm
from apps.hashing import Hasher
from apps.schemas import User, UserInDB
from apps.utils.send_email import send_verification_email
from config.authentication import oauth2_scheme
from config.db import get_db
from config.settings import settings


async def login_create_token(form: CustomOAuth2PasswordRequestForm, db: Session):
    result: dict = await authenticate_user(db, form.email, form.password)
    if result.get('error'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result.get('result'),
            headers={'WWW-Authenticate': 'Bearer'}
        )
    user = result['user']
    access_token = await create_access_token(user.email)
    refresh_token = await create_refresh_token(user.email)
    response = {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'bearer'
    }
    return response


async def get_user(db: Session, email: str):
    user = db.query(models.Users).filter_by(email=email).first()
    if user:
        return UserInDB(**user.__dict__)


async def authenticate_user(db: Session, email: str, password: str):
    user = await get_user(db, email)
    if not user:
        return {
            'error': True,
            'result': 'Email not available'
        }
    if not Hasher.check_hash(password, user.password):
        return {
            'error': True,
            'result': 'Incorrect password'
        }
    return {
        'error': False,
        'user': user,
    }


async def create_access_token(email: str):
    expires_data = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    if expires_data:
        expire = datetime.utcnow() + expires_data
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        'type': 'access',
        'sub': email,
        'exp': expire
    }
    encoded_jwt = await jwt.encode(to_encode, settings.SECRET_KEY)
    return encoded_jwt


async def create_refresh_token(email: str):
    expire = datetime.utcnow() + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    payload = {
        'sub': email,
        'type': 'refresh',
        'exp': expire
    }
    encoded_jwt = jwt.encode(payload, settings.SECRET_KEY)
    return encoded_jwt


async def get_access_token_by_refresh_token(db: Session, refresh_token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'}
    )
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY)
        email: str = payload.get('sub')
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await get_user(db, email)
    access_token = await create_access_token(user.email)
    if user is None:
        raise credentials_exception
    return access_token


def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'}
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
    db.close()
    return user


def get_current_activate_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Inactive user'
        )


async def save_register_user(db: Session, form):
    if errors := form.is_valid(db):
        response = {
            'errors': errors,
        }
        return response
    else:
        data = form.dict(exclude_none=True)
        user = models.Users(**data)
        db.add(user)
        db.commit()
        code = randint(100000, 999999)
        cache = settings.REDIS_CLIENT
        cache.set(user.email, code)
        cache.expire(user.email, timedelta(seconds=settings.REDIS_VERIFY_EMAIL))
        verify_code = cache.get(user.email)
        print(verify_code, 'verify')
        send_verification_email.delay(user, verify_code)
        return {"message": 'Successfully registered your email sending verify code'}


async def check_verify_code_worker(
        verify_email: str, verify_code: int
):
    db: Session = next(get_db())
    cache = settings.REDIS_CLIENT
    code = cache.get(verify_email)
    if code is not None:
        code = int(code)
        if code == verify_code:
            user = db.query(models.Users).filter_by(email=verify_email).first()
            user.is_active = True
            db.commit()
            db.close()
            return {"message": 'successful check'}
        return HTTPException(400, 'Is not true verify code')
    return {'message': "Verification code is out of date"}


async def again_send_code_email_worker(
        verify_email: str
):
    code = randint(100000, 999999)
    cache = settings.REDIS_CLIENT
    cache.set(verify_email, code)
    cache.expire(verify_email, timedelta(seconds=settings.REDIS_VERIFY_EMAIL))
    verify_code = cache.get(verify_email)
    print(verify_code, 'verify')
    send_verification_email.delay(verify_email, verify_code)
    return {"message": 'Successfully again your email sending verify code !'}
