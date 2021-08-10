from pathlib import Path
from typing import List

from fastapi import FastAPI, Request, Response, Depends, HTTPException
from fastapi.responses import ORJSONResponse, HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from starlette_i18n import get_locale
from tortoise import Tortoise

from .config import TORTOISE_ORM, PAGINATION_HEADERS, templates
from .dependencies import Pagination, set_language
from .exceptions import exception_handlers
from .helpers import prepare_response, create_access_token, SetupTranslations
from .schemas import LanguageSchema, StyleSchema, Token, HttpError
from .snippets.models import Language, Style
from .snippets.views import router as snippet_router
from .users.models import User
from .users.views import router as user_router


# tortoise uses decorator on_event which is now deprecated by starlette
# this is why I prefer to implement startup and shutdown functions by myself instead of
# relying of tortoise fastapi helper.
async def init_tortoise():
    await Tortoise.init(config=TORTOISE_ORM)


async def close_tortoise():
    await Tortoise.close_connections()


current_dir = Path(__file__).parent
locales_dir = current_dir / 'locales'
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
    on_startup=[init_tortoise, SetupTranslations(locales_dir=f'{locales_dir}')],
    on_shutdown=[close_tortoise]
)
app.include_router(user_router)
app.include_router(snippet_router)

static_dir = current_dir / 'static'
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


@app.post(
    '/token',
    response_model=Token,
    summary='Get an access token',
    tags=['auth'],
    responses={
        401: {
            'description': 'Invalid username or password',
            'model': HttpError,
            'headers': {
                'WWW-Authenticate': {
                    'schema': {
                        'type': 'string',
                        'example': 'Bearer'
                    },
                    'description': 'Specify the type of authentication'
                }
            }
        }
    }
)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    auth_exception = HTTPException(
        status_code=401, detail='Invalid username or password', headers={'WWW-Authenticate': 'Bearer'},
    )
    user = await User.filter(pseudo=form_data.username).get_or_none()
    if user is None:
        raise auth_exception

    if not user.check_password(form_data.password):
        raise auth_exception

    token = create_access_token({'sub': form_data.username})
    return {'access_token': token, 'token_type': 'bearer'}


@app.get(
    '/internationalization',
    response_class=HTMLResponse,
    description='A dummy html content to test internationalization with FastAPI',
    summary='Tests i18n with FastAPI',
    dependencies=[Depends(set_language)]
)
async def about(request: Request):
    context = {'request': request, 'locale': get_locale()}
    templates.env.install_gettext_translations(get_locale().translations)  # type: ignore
    return templates.TemplateResponse('i18n.jinja2', context)
