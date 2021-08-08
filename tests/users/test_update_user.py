import uuid

import pytest

from pastebin.helpers import create_access_token
from pastebin.users.models import User
from tests.helpers import is_valid_user, get_authorization_header, create_user

pytestmark = pytest.mark.anyio


async def test_should_return_401_error_when_user_is_not_authenticated(client):
    response = await client.patch(f'/users/{uuid.uuid4()}')

    assert 401 == response.status_code
    assert {'detail': 'Not authenticated'} == response.json()
    assert 'Bearer' == response.headers['www-authenticate']


@pytest.mark.parametrize('token_data', [
    {'foo': 'bar'},  # unknown claim
    {'sub': 'foo'}  # unknown user pseudo
])
async def test_should_return_401_error_when_token_is_not_valid(client, default_user_id, token_data):
    auth_header = {'Authorization': f'Bearer {create_access_token(token_data)}'}
    response = await client.patch(f'/users/{default_user_id}', headers=auth_header)

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
    response = await client.patch(f'/users/{user_id}', headers=auth_header)  # type: ignore

    assert 404 == response.status_code
    assert {'detail': f'no user with id {user_id} found'} == response.json()


async def test_returns_422_error_when_user_id_is_not_a_uuid(client, auth_header):
    response = await client.patch('/users/43', json={}, headers=auth_header)  # type: ignore

    assert 422 == response.status_code
    message = {
        'detail': [
            {
                'loc': ['path', 'user_id'],
                'msg': 'value is not a valid uuid',
                'type': 'type_error.uuid'
            }
        ]
    }
    assert message == response.json()


async def test_should_return_409_error_when_pseudo_already_exists(client, auth_header):
    user_id = await create_user(client)
    response = await client.patch(f'/users/{user_id}', json={'pseudo': 'Bob'}, headers=auth_header)  # type: ignore

    assert 409 == response.status_code
    assert {'detail': 'A user with pseudo Bob already exists'} == response.json()


async def test_should_return_409_error_when_email_already_exists(client, auth_header):
    user_id = await create_user(client)
    response = await client.patch(
        f'/users/{user_id}', json={'email': 'bob@foo.com'}, headers=auth_header  # type: ignore
    )

    assert 409 == response.status_code
    assert {'detail': 'A user with email bob@foo.com already exists'} == response.json()


async def test_returns_422_error_when_field_does_not_have_the_correct_type(client, default_user_id, auth_header):
    payload = {
        'firstname': 42,
        'lastname': 42,
        'pseudo': 42,
        'email': 'hello@bar.com',
        'password': 42
    }
    response = await client.patch(f'/users/{default_user_id}', json=payload, headers=auth_header)  # type: ignore

    assert 422 == response.status_code
    fields = ['firstname', 'lastname', 'pseudo', 'password']
    errors = [{'loc': ['body', field], 'msg': 'str type expected', 'type': 'type_error.str'} for field in fields]
    assert {'detail': errors} == response.json()


async def test_returns_422_error_when_field_does_not_have_the_correct_length(client, default_user_id, auth_header):
    payload = {
        'firstname': '',
        'lastname': 'B',
        'pseudo': 'B',
        'email': 'foo@bar.com',
        'password': ''
    }
    response = await client.patch(f'/users/{default_user_id}', json=payload, headers=auth_header)  # type: ignore

    assert 422 == response.status_code
    errors = []
    for field, min_length in [('firstname', 1), ('lastname', 2), ('pseudo', 2), ('password', 1)]:
        errors.append({
            'loc': ['body', field],
            'msg': f'{field} must have a minimum length of {min_length}',
            'type': 'value_error'
        })
    assert {'detail': errors} == response.json()


async def test_should_return_422_error_when_payload_is_incorrect(client, default_user_id, auth_header):
    payload = {
        'firstname': 43,  # not a string
        'lastname': 'bar',
        'email': 'foo'  # not a valid email
    }
    response = await client.patch(f'/users/{default_user_id}', json=payload, headers=auth_header)  # type: ignore

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


@pytest.mark.parametrize(('username', 'password'), [
    ('escobar', 'leaf'),  # owner user
    ('admin', 'admin')  # admin user
])
async def test_should_update_and_return_user_when_given_correct_payload_without_password(client, username, password):
    user_id = await create_user(client)
    payload = {
        'firstname': 'Santos',
        'lastname': 'Phoenix',
        'pseudo': 'phoenix'
    }
    auth_header = await get_authorization_header(client, username, password)
    response = await client.patch(f'/users/{user_id}', json=payload, headers=auth_header)
    assert 200 == response.status_code

    user = await User.filter(pk=user_id).get_or_none()
    assert user is not None

    for key, value in payload.items():
        assert getattr(user, key) == value

    assert is_valid_user(response.json())


@pytest.mark.parametrize(('username', 'password'), [
    ('escobar', 'leaf'),  # owner user
    ('admin', 'admin')  # admin user
])
async def test_should_update_and_return_user_when_given_correct_payload_with_password(client, username, password):
    user_id = await create_user(client)
    payload = {
        'email': 'phoenix@foo.com',
        'password': 'phoenix'
    }
    auth_header = await get_authorization_header(client, username, password)
    response = await client.patch(f'/users/{user_id}', json=payload, headers=auth_header)
    assert 200 == response.status_code

    user = await User.filter(pk=user_id).get_or_none()
    assert user is not None
    assert user.email == payload['email']
    assert user.check_password(payload['password'])

    assert is_valid_user(response.json())
