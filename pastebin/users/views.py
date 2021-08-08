from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, Response

from pastebin.config import PAGINATION_HEADERS
from pastebin.dependencies import get_db_user, get_authenticated_user, Pagination
from pastebin.helpers import prepare_response
from pastebin.schemas import HttpError
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
    description='Creates a user',
    responses={
        409: {
            'description': 'Conflict with email or pseudo name',
            'model': HttpError
        }
    }
)
async def create_user(user_input: UserCreate = Depends(check_create_user_integrity)):
    user_dict = user_input.dict()
    password = user_dict.pop('password')
    user = User(**user_dict)
    user.set_password(password)
    await user.save()
    return user


@router.get(
    '/',
    description='Gets a list of users',
    response_model=List[UserOutput],
    responses={200: PAGINATION_HEADERS}
)
async def get_users(request: Request, response: Response, pagination: Pagination = Depends()):
    return await prepare_response(request, response, User, pagination.page, pagination.page_size)


@router.get(
    '/{user_id}',
    response_model=UserOutput,
    description='Gets a user given its id',
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


@router.patch(
    '/{user_id}',
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
async def update_user(
        user: UserUpdate = Depends(check_update_user_integrity),
        db_user: User = Depends(get_authenticated_user)
):
    """
    Updates user information either partially or completely.
    The update can only be done by the concerned user or an admin user.
    """
    user_dict = user.dict(exclude_unset=True)
    if 'password' in user_dict:
        db_user.set_password(user_dict.pop('password'))

    for key, value in user_dict.items():
        setattr(db_user, key, value)

    await db_user.save()
    return db_user


@router.delete(
    '/{user_id}',
    status_code=204,
    response_class=Response,
    response_description='User deleted',
    responses={
        404: {
            'description': 'User not found',
            'model': HttpError
        }
    }
)
async def delete_user(user: User = Depends(get_authenticated_user)):
    """
    Deletes a user. The deletion can only be done by the concerned user or an admin user.
    """
    await user.delete()
