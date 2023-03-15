import re

from fastapi import File, Form, HTTPException, UploadFile
from pydantic import BaseModel, validator

from apps import models
from apps.hashing import Hasher
from database import get_db


class User(BaseModel):
    name: str
    email: str
    password: str
    image: str


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
