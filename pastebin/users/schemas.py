import datetime
import uuid
from functools import partial
from typing import Optional

from pydantic import BaseModel, Field, EmailStr, StrictStr, validator

firstname_field = partial(Field, description='user firstname', example='Kevin', minLength=1)
lastname_field = partial(Field, description='user lastname', example='Bryant', minLength=2)
pseudo_field = partial(Field, description='user pseudo', example='smooth_boy', minLength=2)
email_field = partial(Field, description='user email', example='kevin.bryant@foo.com')
password_field = partial(Field, description='user password', example='supersecretpassword', minLength=1)


class UserBase(BaseModel):
    firstname: StrictStr = firstname_field(default=...)
    lastname: StrictStr = lastname_field(default=...)
    pseudo: StrictStr = pseudo_field(default=...)
    email: EmailStr = email_field(default=...)

    @validator('lastname', 'pseudo')
    def validate_lastname_and_pseudo_length(cls, value: str, **kwargs) -> str:
        field = kwargs.pop('field')
        if len(value) < 2:
            raise ValueError(f'{field.name} must have a minimum length of 2')
        return value

    class Config:
        orm_mode = True


class UserCreate(UserBase):
    password: StrictStr = password_field(default=...)

    @validator('firstname', 'password')
    def validate_firstname_and_password_length(cls, value: str, **kwargs) -> str:
        field = kwargs.pop('field')
        if len(value) < 1:
            raise ValueError(f'{field.name} must have a minimum length of 1')
        return value


class UserUpdate(UserCreate):
    firstname: Optional[StrictStr] = firstname_field(default=None)
    lastname: Optional[StrictStr] = lastname_field(default=None)
    pseudo: Optional[StrictStr] = pseudo_field(default=None)
    email: Optional[EmailStr] = email_field(default=None)
    password: Optional[StrictStr] = password_field(default=None)


class UserOutput(UserBase):
    id: uuid.UUID = Field(..., description='user id')
    created_at: datetime.datetime = Field(..., description='creation date of a user')
