import uuid
from typing import Dict

import httpx
import pytest
from tortoise import Tortoise

from pastebin.main import app
from pastebin.snippets.models import Language, Style
from pastebin.users.models import User
from tests.helpers import create_snippet


@pytest.fixture(scope='session')
def default_user_id() -> str:
    return str(uuid.uuid4())


async def create_users(default_user_id: str) -> None:
    user_1 = User(id=default_user_id, firstname='Bob', lastname='Fish', pseudo='Bob', email='bob@foo.com')
    user_1.set_password('hell')
    await user_1.save()
    user_2 = User(firstname='Bobby', lastname='Fish', pseudo='fisher', email='fisher@foo.com')
    user_2.set_password('foo')
    await user_2.save()
    # admin user
    user = User(firstname='admin', lastname='admin', pseudo='admin', email='admin@admin.com', is_admin=True)
    user.set_password('admin')
    await user.save()


async def create_languages() -> None:
    for language in ['Python', 'Ruby']:
        await Language.create(name=language)


async def create_styles() -> None:
    for style in ['monokai', 'friendly']:
        await Style.create(name=style)


async def create_snippets(user_id: str):
    for title in ['test 1', 'test 2']:
        await create_snippet(user_id, title=title)

    user = await User.filter(pseudo='fisher').get()
    await create_snippet(user.id, title='test 3')


async def create_models(default_user_id: str) -> None:
    await create_users(default_user_id)
    await create_languages()
    await create_styles()
    await create_snippets(default_user_id)


@pytest.fixture()
async def client(default_user_id) -> httpx.AsyncClient:
    # HTTPX does not support the lifespan agsi protocol so on_startup/on_shutdown callbacks can't be run automatically
    # we need to run them manually here
    # TODO: seems like what I do here does not really work as expected
    await Tortoise.init(
        db_url='sqlite://:memory:',
        modules={'pastebin': ['pastebin.users.models', 'pastebin.snippets.models']}
    )
    await Tortoise.generate_schemas()
    await create_models(default_user_id)
    async with httpx.AsyncClient(app=app, base_url='http://testserver') as test_client:
        yield test_client
    await Tortoise.close_connections()


@pytest.fixture()
async def auth_header(client) -> Dict[str, str]:
    response = await client.post('/token', data={'username': 'Bob', 'password': 'hell'})
    token = response.json()['access_token']
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture(scope='session')
def anyio_backend():
    return 'asyncio'
