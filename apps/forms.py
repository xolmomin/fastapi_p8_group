from typing import Optional
import re

from fastapi import Form
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from apps import models
from apps.hashing import Hasher


class CustomOAuth2PasswordRequestForm(OAuth2PasswordRequestForm):
    def __init__(
            self,
            grant_type: str = Form(default=None, regex="password"),
            email: str = Form(),
            password: str = Form(),
            scope: str = Form(default=""),
            client_id: Optional[str] = Form(default=None),
            client_secret: Optional[str] = Form(default=None),
    ):
        self.grant_type = grant_type
        self.email = email
        self.password = password
        self.scopes = scope.split()
        self.client_id = client_id
        self.client_secret = client_secret
        # super().__init__(grant_type,email, password, scope, client_id, client_secret)


class RegisterForm(BaseModel):
    name: str
    email: str
    password: str
    confirm_password: Optional[str]

    def is_valid(self, db: Session):
        errors = []
        if self.confirm_password != self.password:
            errors.append('Password did not match!')

        regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        if not re.search(regex, self.email):
            errors.append('Must be a valid email address')
        self.confirm_password = None
        q = db.query(models.Users).filter(models.Users.email == self.email)
        exists = db.query(q.exists()).first()[0]

        if exists:
            errors.append('Must be a unique email address')

        self.password = Hasher.make_hash(self.password)
        return errors
    @classmethod
    def as_form(
            cls,
            name: str = Form(...),
            email: str = Form(...),
            password: str = Form(...),
            confirm_password: str = Form(...)
    ):
        return cls(name=name, email=email, password=password, confirm_password=confirm_password)