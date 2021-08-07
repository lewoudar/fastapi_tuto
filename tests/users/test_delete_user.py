import uuid

import pytest

from pastebin.helpers import create_access_token
from pastebin.users.models import User
from tests.helpers import create_user

pytestmark = pytest.mark.anyio


async def test_should_return_401_error_when_user_is_not_authenticated(client):
    response = await client.delete(f'/users/{uuid.uuid4()}')

    assert 401 == response.status_code
    assert {'detail': 'Not authenticated'} == response.json()
    assert 'Bearer' == response.headers['www-authenticate']


@pytest.mark.parametrize('token_data', [
    {'foo': 'bar'},  # unknown claim
    {'sub': 'foo'}  # unknown user pseudo
])
async def test_should_return_401_error_when_token_is_not_valid(client, default_user_id, token_data):
    auth_header = {'Authorization': f'Bearer {create_access_token(token_data)}'}
    response = await client.delete(f'/users/{default_user_id}', headers=auth_header)

    assert 401 == response.status_code
    assert {'detail': 'Could not validate credentials'} == response.json()
    assert 'Bearer' == response.headers['www-authenticate']


async def test_should_return_403_error_when_user_is_not_allowed_to_access_resource(client, auth_header):
    user_id = await create_user(client)
    response = await client.patch(f'/users/{user_id}', headers=auth_header)  # type: ignore

    assert 403 == response.status_code
    assert {'detail': 'Access denied for the resource'} == response.json()


async def test_should_return_404_error_when_user_id_is_unknown(client, auth_header):
    user_id = uuid.uuid4()
    response = await client.delete(f'/users/{user_id}', headers=auth_header)  # type: ignore

    assert 404 == response.status_code
    assert {'detail': f'no user with id {user_id} found'} == response.json()


async def test_should_delete_user_when_given_correct_user_id(client, default_user_id, auth_header):
    response = await client.delete(f'/users/{default_user_id}', headers=auth_header)  # type: ignore

    assert 204 == response.status_code
    user = await User.filter(pk=default_user_id).get_or_none()
    assert user is None


async def test_should_delete_user_when_giving_user_id_and_being_admin(client, default_user_id):
    auth_header = {'Authorization': f'Bearer {create_access_token({"sub": "admin"})}'}
    response = await client.delete(f'/users/{default_user_id}', headers=auth_header)

    assert 204 == response.status_code
    user = await User.filter(pk=default_user_id).get_or_none()
    assert user is None
