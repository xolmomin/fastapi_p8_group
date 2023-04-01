import re

from fastapi import File, Form, HTTPException, UploadFile
from pydantic import BaseModel, validator
from sqlalchemy.orm import Session

from apps import models
from apps.hashing import Hasher
from config.db import get_db


class UserForm(BaseModel):
    name: str
    email: str
    password: str
    image: UploadFile | None

    class Config:
        orm_mode = True

    @validator('password')
    def validate_password(cls, value):
        if len(value) < 1:
            raise HTTPException(400, 'Password should be strong')
        return Hasher.make_hash(value)

    @validator('email')
    def validate_email(cls, value):
        db = next(get_db())
        q = db.query(models.Users).where(models.Users.email == value)
        exists = db.query(q.exists()).first()[0]
        if exists:
            raise HTTPException(400, 'Email is already used !')
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
        if len(value) < 1:
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


class RegisterForm(BaseModel):
    name: str
    email: str
    password: str
    confirm_password: str

    class Config:
        orm_mode = True

    def is_valid(self, db: Session):
        if self.confirm_password != self.password:
            raise HTTPException(400, "Password did not match!")
        regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        if not re.search(regex, self.email):
            raise HTTPException(400, "Must be a valid email address")
        self.confirm_password = None
        q = db.query(models.Users).filter(models.Users.email == self.email)
        exists = db.query(q.exists()).first()[0]
        if exists:
            raise HTTPException(400, 'Must be a unique email address')
        self.password = Hasher.make_hash(self.password)

    @classmethod
    def as_form(
            cls,
            name: str = Form(...),
            email: str = Form(...),
            password: str = Form(...),
            confirm_password: str = Form(...),
    ):
        return cls(
            name=name,
            email=email,
            password=password,
            confirm_password=confirm_password,
        )


class VerifyForm(BaseModel):
    email: str
    verify_code: int

    class Config:
        orm_mode = True

    @validator('email')
    def validate_email(cls, value):
        db: Session = next(get_db())
        regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        if not re.search(regex, value):
            raise HTTPException(400, "Must be a valid email address")
        user = db.query(models.Users).filter_by(email=value).first()
        if not user:
            raise HTTPException(400, "Email address doesn't exists !")
        if user.is_active:
            raise HTTPException(400, "Already confirmed !")
        db.close()
        return value

    @classmethod
    def as_form(
            cls,
            email: str = Form(...),
            verify_code: int = Form(...),
    ):
        return cls(
            email=email,
            verify_code=verify_code,
        )


class AgainVerifyForm(BaseModel):
    email: str

    class Config:
        orm_mode = True

    @validator('email')
    def validate_email(cls, value):
        db: Session = next(get_db())
        regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        if not re.search(regex, value):
            raise HTTPException(400, "Must be a valid email address")
        user = db.query(models.Users).filter_by(email=value).first()
        if not user:
            raise HTTPException(400, "Email address doesn't exists !")
        if user.is_active:
            raise HTTPException(400, "Already confirmed !")
        db.close()
        return value

    @classmethod
    def as_form(
            cls,
            email: str = Form(...),
    ):
        return cls(
            email=email,
        )


class Login(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class Register(BaseModel):
    name: str
    email: str
    password: str


class RefreshToken(BaseModel):
    refresh_token: str


class ResponseRefreshToken(BaseModel):
    access_token: str


class User(BaseModel):
    email: str
    name: str | None = None
    is_active: bool | None = None


class UserInDB(User):
    password: str
