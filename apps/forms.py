from typing import Optional

from fastapi import Form
from fastapi.security import OAuth2PasswordRequestForm


class CustomOAuth2PasswordRequestForm(OAuth2PasswordRequestForm):
    def __init__(
            self,
            grant_type: str = Form(default=None, regex="password"),
            email: str = Form(),
            password: str = Form(),
            scope: str = Form(default=""),
            client_id: Optional[str] = Form(default=None),
            client_secret: Optional[str] = Form(default=None)
    ):
        self.grant_type = grant_type
        self.email = email
        self.password = password
        self.scopes = scope.split()
        self.client_id = client_id
        self.client_secret = client_secret

