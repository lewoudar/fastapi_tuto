import uuid

from fastapi import HTTPException, Path, Query, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt

from .config import settings
from .snippets.models import Snippet
from .users.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


async def get_db_user(
        user_id: uuid.UUID = Path(..., description='user id', example='7fef63f3-c616-4a3b-bc4a-11917a46c5aa')
) -> User:
    user = await User.filter(pk=str(user_id)).get_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail=f'no user with id {user_id} found')

    return user


async def parse_authenticated_user(token: str) -> User:
    auth_exception = HTTPException(401, detail='Could not validate credentials', headers={'WWW-Authenticate': 'Bearer'})
    try:
        data = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    except jwt.JWTError:
        raise auth_exception

    username: str = data.get('sub')
    if username is None:
        raise auth_exception

    auth_user = await User.filter(pseudo=username).get_or_none()
    if auth_user is None:
        raise auth_exception

    return auth_user


async def get_authenticated_user(token: str = Depends(oauth2_scheme), user: User = Depends(get_db_user)) -> User:
    authenticated_user = await parse_authenticated_user(token)
    if authenticated_user.pseudo != user.pseudo and not authenticated_user.is_admin:
        raise HTTPException(403, detail='Access denied for the resource')

    return user


async def get_db_snippet(
        snippet_id: uuid.UUID = Path(..., description='snippet id', example='7fef63f3-c616-4a3b-bc4a-11917a46c5aa')
) -> Snippet:
    snippet = await Snippet.filter(pk=str(snippet_id)).get_or_none()
    if snippet is None:
        raise HTTPException(status_code=404, detail=f'no snippet with id {snippet_id} found')

    await snippet.fetch_related('language', 'style', 'user')
    return snippet


async def get_authenticated_snippet(token: str = Depends(oauth2_scheme), snippet: Snippet = Depends(get_db_snippet)):
    authenticated_user = await parse_authenticated_user(token)
    if authenticated_user != snippet.user and not authenticated_user.is_admin:
        raise HTTPException(403, detail='Access denied for the resource')

    return snippet


class Pagination:
    def __init__(
            self,
            page: int = Query(1, description='number of the page to fetch', ge=1),
            page_size: int = Query(50, description='number of items per page', ge=1, le=100)
    ):
        self.page = page
        self.page_size = page_size
