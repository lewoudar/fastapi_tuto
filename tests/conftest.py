import uuid

import httpx
import pytest
from tortoise import Tortoise

from pastebin.main import app
from pastebin.snippets.models import Language, Style
from pastebin.users.models import User


@pytest.fixture(scope='session')
def default_user_id() -> str:
    return str(uuid.uuid4())


async def create_users(default_user_id: str) -> None:
    user = User(id=default_user_id, firstname='Bob', lastname='Fish', pseudo='Bob', email='bob@foo.com')
    user.set_password('hell')
    await user.save()


async def create_languages() -> None:
    for language in ['Python', 'Ruby']:
        await Language.create(name=language)


async def create_styles() -> None:
    for style in ['monokai', 'friendly']:
        await Style.create(name=style)


async def create_models(default_user_id: str) -> None:
    await create_users(default_user_id)
    await create_languages()
    await create_styles()


@pytest.fixture()
async def client(default_user_id) -> httpx.AsyncClient:
    # Hum... it seems like the startup events are not taken in account, at least for Tortoise
    # so it is necessary to initialize the test database here
    await Tortoise.init(
        db_url='sqlite://:memory:',
        modules={'pastebin': ['pastebin.users.models', 'pastebin.snippets.models']}
    )
    await Tortoise.generate_schemas()
    await create_models(default_user_id)
    async with httpx.AsyncClient(app=app, base_url='http://testserver') as test_client:
        yield test_client
    await Tortoise.close_connections()


@pytest.fixture(scope='session')
def anyio_backend():
    return 'asyncio'
