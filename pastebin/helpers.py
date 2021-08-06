from datetime import datetime, timedelta
from typing import Dict, List, Any, Sequence, Type, Union

from fastapi import Response, Request
from jose import jwt
from tortoise import Model

from .config import settings


async def prepare_response(
        request: Request,
        response: Response,
        model_class: Type[Model],
        page: int,
        page_size: int,
        filters: Dict[str, Any] = None,
        to_prefetch: Sequence[str] = None
) -> List[Model]:
    filters = {} if filters is None else filters
    to_prefetch = [] if to_prefetch is None else to_prefetch
    offset = (page * page_size) - page_size
    models = await model_class.filter(**filters).offset(offset).limit(page_size).prefetch_related(*to_prefetch)

    previous_page = 'X-Previous-Page'
    next_page = 'X-Next-Page'
    if offset == 0:
        response.headers[previous_page] = ''
    else:
        response.headers[previous_page] = str(request.url.include_query_params(page=page - 1, page_size=page_size))
    if len(models) < page_size:
        response.headers[next_page] = ''
    else:
        response.headers[next_page] = str(request.url.include_query_params(page=page + 1, page_size=page_size))

    return models


def create_access_token(data: Dict[str, Union[str, datetime]]) -> str:
    to_encode = data.copy()
    expire_time = datetime.utcnow() + timedelta(seconds=settings.jwt_token_expire_seconds)
    to_encode.update({'exp': expire_time})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)
