import datetime
import uuid

from pydantic import BaseModel, Field, EmailStr, StrictStr


class UserBase(BaseModel):
    firstname: StrictStr = Field(..., description='user firstname', example='Kevin')
    lastname: StrictStr = Field(..., description='user lastname', example='Bryant')
    pseudo: StrictStr = Field(..., description='user pseudo', example='smooth_boy')
    email: EmailStr = Field(..., description='user email', example='kevin.bryant@foo.com')


class UserCreate(UserBase):
    password: StrictStr = Field(..., description='user password', example='supersecretpassword')


class UserOutput(UserBase):
    id: uuid.UUID = Field(..., description='user id')
    created_at: datetime.datetime = Field(..., description='creation date of a user')
