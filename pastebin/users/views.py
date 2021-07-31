from typing import List

from fastapi import APIRouter, Response, Depends, HTTPException

from pastebin.schemas import HttpError
from pastebin.dependencies import get_db_user
from .models import User
from .schemas import UserCreate, UserUpdate, UserOutput

router = APIRouter(prefix='/users', tags=['users'])


async def check_field_integrity(field_name: str, value: str) -> None:
    filters = {field_name: value}
    user = await User.filter(**filters).get_or_none()
    if user:
        raise HTTPException(status_code=409, detail=f'A user with {field_name} {value} already exists')


async def check_create_user_integrity(user_input: UserCreate) -> UserCreate:
    await check_field_integrity('pseudo', user_input.pseudo)
    await check_field_integrity('email', user_input.email)
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
async def create_user(response: Response, user_input: UserCreate = Depends(check_create_user_integrity)):
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


async def check_update_user_integrity(user_input: UserUpdate) -> UserUpdate:
    if user_input.pseudo:
        await check_field_integrity('pseudo', user_input.pseudo)
    if user_input.email:
        await check_field_integrity('email', user_input.email)
    return user_input


# In real applications you probably don't want to change user given a path parameter whose value can changed
# but for simplicity here, we will just use that
@router.patch(
    '/{pseudo}',
    response_model=UserOutput,
    responses={
        404: {
            'description': 'User not found',
            'model': HttpError
        },
        409: {
            'description': 'Conflict with email or pseudo name',
            'model': HttpError
        }
    }
)
async def update_user(user: UserUpdate = Depends(check_update_user_integrity), db_user: User = Depends(get_db_user)):
    user_dict = user.dict(exclude_unset=True)
    if 'password' in user_dict:
        db_user.set_password(user_dict.pop('password'))

    for key, value in user_dict.items():
        setattr(db_user, key, value)

    await db_user.save()
    return db_user
