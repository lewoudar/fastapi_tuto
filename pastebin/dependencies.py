from fastapi import HTTPException

from .users.models import User


async def get_db_user(pseudo: str) -> User:
    user = await User.filter(pseudo=pseudo).get_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail=f'user {pseudo} not found')

    return user
