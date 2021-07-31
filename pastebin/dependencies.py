import uuid

from fastapi import HTTPException

from .users.models import User


async def get_db_user(user_id: uuid.UUID) -> User:
    user = await User.filter(pk=str(user_id)).get_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail=f'user with id {user_id} not found')

    return user
