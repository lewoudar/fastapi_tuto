import pytest
import httpx

from pastebin.users.models import User
from tests.helpers import is_valid_user

pytestmark = pytest.mark.anyio


async def create_user(client: httpx.AsyncClient) -> None:
    payload = {
        'firstname': 'Pablo',
        'lastname': 'Escobar',
        'pseudo': 'escobar',
        'email': 'escobar@drug.com',
        'password': 'leaf'
    }
    await client.post('/users/', json=payload)


async def test_should_return_404_error_when_pseudo_is_unknown(client):
    response = await client.patch('/users/foo', json={})

    assert 404 == response.status_code
    assert {'detail': 'user foo not found'} == response.json()


async def test_should_return_409_error_when_pseudo_already_exists(client):
    await create_user(client)
    response = await client.patch('/users/escobar', json={'pseudo': 'Bob'})

    assert 409 == response.status_code
    assert {'detail': 'A user with pseudo Bob already exists'} == response.json()


async def test_should_return_409_error_when_email_already_exists(client):
    await create_user(client)
    response = await client.patch('/users/escobar', json={'email': 'bob@foo.com'})

    assert 409 == response.status_code
    assert {'detail': 'A user with email bob@foo.com already exists'} == response.json()


async def test_should_return_422_error_when_payload_is_incorrect(client):
    payload = {
        'firstname': 43,  # not a string
        'lastname': 'bar',
        'email': 'foo'  # not a valid email
    }
    response = await client.patch('/users/Bob', json=payload)

    assert 422 == response.status_code
    message = {
        'detail': [
            {
                'loc': ['body', 'firstname'],
                'msg': 'str type expected',
                'type': 'type_error.str'
            },
            {
                'loc': ['body', 'email'],
                'msg': 'value is not a valid email address',
                'type': 'value_error.email'
            }
        ]
    }
    assert message == response.json()


async def test_should_update_and_return_user_when_given_correct_payload_without_password(client):
    await create_user(client)
    payload = {
        'firstname': 'Santos',
        'lastname': 'Phoenix',
        'pseudo': 'phoenix'
    }
    response = await client.patch('/users/escobar', json=payload)
    assert 200 == response.status_code

    user = await User.filter(pseudo='phoenix').get_or_none()
    assert user is not None

    for key, value in payload.items():
        assert getattr(user, key) == value

    assert is_valid_user(response.json())


async def test_should_update_and_return_user_when_given_correct_payload_with_password(client):
    await create_user(client)
    payload = {
        'email': 'phoenix@foo.com',
        'password': 'phoenix'
    }
    response = await client.patch('/users/escobar', json=payload)
    assert 200 == response.status_code

    user = await User.filter(pseudo='escobar').get_or_none()
    assert user is not None
    assert user.email == payload['email']
    assert user.check_password(payload['password'])

    assert is_valid_user(response.json())
