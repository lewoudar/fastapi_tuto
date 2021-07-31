from typing import List

from fastapi import APIRouter, Response, Depends, HTTPException

from pastebin.schemas import HttpError
from pastebin.dependencies import get_db_user
from .models import User
from .schemas import UserCreate, UserOutput

router = APIRouter(prefix='/users', tags=['users'])


async def check_user_integrity(user_input: UserCreate) -> UserCreate:
    user = await User.filter(pseudo=user_input.pseudo).get_or_none()
    if user:
        raise HTTPException(status_code=409, detail=f'A user with pseudo {user_input.pseudo} already exists')

    user = await User.filter(email=user_input.email).get_or_none()
    if user:
        raise HTTPException(status_code=409, detail=f'A user with email {user_input.email} already exists')
    return user_input


@router.post(
    '/',
    response_model=UserOutput,
    status_code=201,
    responses={
        409: {
            'description': 'Conflict with email or pseudo name',
            'model': HttpError
        }
    }
)
async def create_user(response: Response, user_input: UserCreate = Depends(check_user_integrity)):
    user_dict = user_input.dict()
    password = user_dict.pop('password')
    user = User(**user_dict)
    user.set_password(password)
    await user.save()

    response.status_code = 201
    return user


@router.get('/', response_model=List[UserOutput])
async def get_users():
    return await User.all()


@router.get(
    '/{pseudo}',
    response_model=UserOutput,
    responses={
        404: {
            'description': 'User not found',
            'model': HttpError
        }
    }
)
async def get_user(user: User = Depends(get_db_user)):
    return user
