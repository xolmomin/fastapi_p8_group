import re
from typing import Optional

from fastapi import Form
from pydantic import BaseModel
from sqlalchemy.orm import Session

from apps import models
from apps.hashing import Hasher


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
