import re
from typing import Optional

from fastapi import File, Form, HTTPException, UploadFile
from fastapi.params import Body
from pydantic import BaseModel, validator, root_validator

from apps import models
from apps.hashing import Hasher
from config.db import get_db, Session


class Country(BaseModel):
    countries: list[str]

    class Config:
        schema_extra = {
            "example": {
                "countries": ['turkey', 'india', 'uzbekistan', 'russia', 'china', 'usa', 'uk', 'australia'],
            }
        }


class University(BaseModel):
    country: Optional[str] = None
    web_pages: list[str] = []
    name: Optional[str] = None
    alpha_two_code: Optional[str] = None
    domains: list[str] = []


class RegisterForm(BaseModel):
    name: str
    email: str
    password: str
    confirm_password: str

    class Config:
        orm_mode = True

    @validator('email')
    def validate_email(cls, value):
        db = next(get_db())
        q = db.query(models.Users).where(models.Users.email == value)
        exists = db.query(q.exists()).first()[0]
        if exists:
            raise HTTPException(400, 'Email address must be unique')
        regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        if not re.search(regex, value):
            raise HTTPException(400, 'Must be a valid email address')
        return value

    @root_validator
    def check_passwords_match(cls, values):
        pw1: str = values.get('password')
        pw2: str = values.pop('confirm_password')
        if pw1 is not None and pw2 is not None and pw1 != pw2:
            raise HTTPException(400, 'passwords do not match')
        values['password'] = Hasher.make_hash(pw1)
        return values

    @classmethod
    def as_form(
            cls,
            name: str = Form(...),
            email: str = Form(...),
            password: str = Form(...),
            confirm_password: str = Form(...),
    ):
        return cls(name=name, email=email, password=password, confirm_password=confirm_password)


class UserForm(BaseModel):
    name: str
    email: str
    password: str
    image: UploadFile | None

    class Config:
        orm_mode = True

    @validator('password')
    def validate_password(cls, value):
        if len(value) < 4:
            raise HTTPException(400, 'Password should be strong')
        return Hasher.make_hash(value)

    @validator('email')
    def validate_email(cls, value):
        db = next(get_db())
        q = db.query(models.Users).where(models.Users.email == value)
        exists = db.query(q.exists()).first()[0]
        if exists:
            raise HTTPException(400, 'Email address must be unique')
        regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        if not re.search(regex, value):
            raise HTTPException(400, 'Must be a valid email address')
        return value

    @classmethod
    def as_form(
            cls,
            name: str = Form(...),
            email: str = Form(...),
            password: str = Form(...),
            image: UploadFile = File(None)
    ):
        return cls(name=name, email=email, password=password, image=image)


class UpdateUser(BaseModel):
    name: str | None
    email: str | None
    password: str | None
    image: UploadFile | None

    class Config:
        orm_mode = True

    @validator('password')
    def validate_password(cls, value):
        if not value:
            return
        if len(value) < 4:
            raise HTTPException(400, 'Password should be strong')
        return Hasher.make_hash(value)

    @validator('email')
    def validate_email(cls, value):
        if not value:
            return
        db = next(get_db())
        q = db.query(models.Users).where(models.Users.email == value)
        exists = db.query(q.exists()).first()[0]
        if exists:
            raise HTTPException(400, 'Email address must be unique')
        regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        if not re.search(regex, value):
            raise HTTPException(400, 'Must be a valid email address')
        return value

    @classmethod
    def as_form(
            cls,
            email: str = Form(None),
            name: str = Form(None),
            password: str = Form(None),
            image: UploadFile = File(None)
    ):
        return cls(name=name, email=email, password=password, image=image)


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RefreshToken(BaseModel):
    refresh_token: str


class ResponseRefreshToken(BaseModel):
    access_token: str


class User(BaseModel):
    email: str
    name: str | None = None
    is_active: bool | None = None


class UserData(BaseModel):
    id: int | None = None
    email: str
    name: str | None = None
    phone: int | None = None
    is_active: bool | None = None
    is_verified_phone: bool | None = None


class UserInDB(UserData):
    password: str


class VerificationPhoneForm(BaseModel):
    phone: str
    code: str

    class Config:
        orm_mode = True

    @validator('phone')
    def validate_phone(cls, value):
        db = next(get_db())
        user = db.query(models.Users).where(models.Users.phone == value).count()
        if not user:
            raise HTTPException(400, "Phone doesn't exists")
        return value

    @classmethod
    def as_form(
            cls,
            phone: str = Form(...),
            code: str = Form(...),
    ):
        return cls(phone=phone, code=code)


class VerificationForm(BaseModel):
    email: str
    code: str

    class Config:
        orm_mode = True

    @validator('email')
    def validate_email(cls, value):
        db = next(get_db())
        user = db.query(models.Users).where(models.Users.email == value).count()
        if not user:
            raise HTTPException(400, "Email address doesn't exists")
        return value

    @classmethod
    def as_form(
            cls,
            email: str = Form(...),
            code: str = Form(...),
    ):
        return cls(email=email, code=code)



class LoginForm(BaseModel):
    email: str
    password: str

    class Config:
        orm_mode = True

    def is_valid(self, db: Session):
        errors = []

        user: models.Users = db.query(models.Users).filter(models.Users.email == self.email).first()
        if not user:
            errors.append('User not found!')
        elif not Hasher.check_hash(self.password, user.password):
            errors.append('Password does not match!')

        return errors, user

    @classmethod
    def as_form(
            cls,
            email: str = Form(...),
            password: str = Form(...),
    ):
        return cls(email=email, password=password)