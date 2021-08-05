from pathlib import Path
from typing import List

from fastapi import FastAPI, Request, Response, Depends
from fastapi.responses import ORJSONResponse
from fastapi.staticfiles import StaticFiles
from tortoise import Tortoise

from .config import TORTOISE_ORM, PAGINATION_HEADERS
from .dependencies import Pagination
from .exceptions import exception_handlers
from .helpers import prepare_response
from .schemas import LanguageSchema, StyleSchema
from .snippets.models import Language, Style
from .snippets.views import router as snippet_router
from .users.views import router as user_router


# tortoise uses decorator on_event which is now deprecated by starlette
# this is why I prefer to implement startup and shutdown functions by myself instead of
# relying of tortoise fastapi helper.
async def init_tortoise():
    await Tortoise.init(config=TORTOISE_ORM)


async def close_tortoise():
    await Tortoise.close_connections()


app = FastAPI(
    title='Pastebin API',
    description='This api allows users to create code snippets and share them',
    version='0.0.1',
    licence_info={
        'name': 'MIT',
        'url': 'https://opensource.org/licenses/MIT'
    },
    redoc_url=None,
    default_response_class=ORJSONResponse,
    exception_handlers=exception_handlers,
    on_startup=[init_tortoise],
    on_shutdown=[close_tortoise]
)
app.include_router(user_router)
app.include_router(snippet_router)

static_dir = Path(__file__).parent / 'static'
app.mount('/static', StaticFiles(directory=f'{static_dir}'), name='static')


@app.get(
    '/languages',
    response_model=List[LanguageSchema],
    tags=['display'],
    responses={200: PAGINATION_HEADERS}
)
async def get_languages(request: Request, response: Response, pagination: Pagination = Depends()):
    return await prepare_response(request, response, Language, pagination.page, pagination.page_size)


@app.get(
    '/styles',
    response_model=List[StyleSchema],
    tags=['display'],
    responses={200: PAGINATION_HEADERS}
)
async def get_styles(request: Request, response: Response, pagination: Pagination = Depends()):
    return await prepare_response(request, response, Style, pagination.page, pagination.page_size)
