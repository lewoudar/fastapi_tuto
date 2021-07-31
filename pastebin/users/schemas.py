import datetime
import uuid
from functools import partial
from typing import Optional

from pydantic import BaseModel, Field, EmailStr, StrictStr

firstname_field = partial(Field, description='user firstname', example='Kevin')
lastname_field = partial(Field, description='user lastname', example='Bryant')
pseudo_field = partial(Field, description='user pseudo', example='smooth_boy')
email_field = partial(Field, description='user email', example='kevin.bryant@foo.com')
password_field = partial(Field, description='user password', example='supersecretpassword')


class UserBase(BaseModel):
    firstname: StrictStr = firstname_field(default=...)
    lastname: StrictStr = lastname_field(default=...)
    pseudo: StrictStr = pseudo_field(default=...)
    email: EmailStr = email_field(default=...)


class UserCreate(UserBase):
    password: StrictStr = password_field(default=...)


class UserUpdate(UserCreate):
    firstname: Optional[StrictStr] = firstname_field(default=None)
    lastname: Optional[StrictStr] = lastname_field(default=None)
    pseudo: Optional[StrictStr] = pseudo_field(default=None)
    email: Optional[EmailStr] = email_field(default=None)
    password: Optional[StrictStr] = password_field(default=None)


class UserOutput(UserBase):
    id: uuid.UUID = Field(..., description='user id')
    created_at: datetime.datetime = Field(..., description='creation date of a user')
