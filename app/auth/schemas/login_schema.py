from datetime import datetime

from pydantic import BaseModel


class LoginSchema(BaseModel):
    email: str
    password: str


class LoginResponseSchema(BaseModel):
    token: str
    expires: datetime
