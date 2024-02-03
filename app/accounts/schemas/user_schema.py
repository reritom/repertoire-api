from pydantic import BaseModel
from pydantic.fields import Field

from app.accounts.models.user import User


class UserCreationSchema(BaseModel):
    email: str = Field(max_length=User.email.type.length)
    password: str = Field(min_length=5)


class UserSchema(BaseModel):
    email: str
