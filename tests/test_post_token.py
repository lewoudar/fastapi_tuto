from typing import Dict

import pydantic
import pytest
from jose import jwt

from pastebin.config import settings
from pastebin.schemas import Token

pytestmark = pytest.mark.anyio


def is_valid_token(data: Dict[str, str]) -> bool:
    try:
        Token(**data)
        return True
    except pydantic.ValidationError:
        return False


@pytest.mark.parametrize(('payload', 'field'), [
    ({'username': 'foo'}, 'password'),
    ({'password': 'foo'}, 'username')
])
async def test_should_return_422_error_when_payload_missed_mandatory_field(client, payload, field):
    response = await client.post('/token', data=payload)

    assert 422 == response.status_code
    assert response.json() == {
        'detail': [
            {
                'loc': ['body', field],
                'msg': 'field required',
                'type': 'value_error.missing'
            }
        ]
    }


@pytest.mark.parametrize('payload', [
    {'username': 'foo', 'password': 'bar'},  # username incorrect
    {'username': 'Bob', 'password': 'bar'}  # password incorrect
])
async def test_should_return_401_error_when_username_or_password_is_incorrect(client, payload):
    response = await client.post('/token', data=payload)

    assert 401 == response.status_code
    assert {'detail': 'Invalid username or password'} == response.json()
    assert 'Bearer' == response.headers['WWW-Authenticate']


async def test_should_return_valid_token_given_correct_credentials(client):
    payload = {'username': 'Bob', 'password': 'hell'}
    response = await client.post('/token', data=payload)

    assert 200 == response.status_code
    data = response.json()
    assert is_valid_token(data)

    token_data = jwt.decode(data['access_token'], settings.secret_key, algorithms=[settings.jwt_algorithm])
    assert payload['username'] == token_data['sub']
