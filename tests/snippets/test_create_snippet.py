import uuid

import pytest

from pastebin.helpers import create_access_token
from pastebin.snippets.models import Snippet
from pastebin.users.models import User
from tests.helpers import is_valid_snippet, create_user, get_authorization_header

pytestmark = pytest.mark.anyio


async def test_should_return_401_error_when_user_is_not_authenticated(client):
    response = await client.post(f'/users/{uuid.uuid4()}/snippets')

    assert 401 == response.status_code
    assert {'detail': 'Not authenticated'} == response.json()
    assert 'Bearer' == response.headers['www-authenticate']


@pytest.mark.parametrize('token_data', [
    {'foo': 'bar'},  # unknown claim
    {'sub': 'foo'}  # unknown user pseudo
])
async def test_should_return_401_error_when_token_is_not_valid(client, default_user_id, token_data):
    auth_header = {'Authorization': f'Bearer {create_access_token(token_data)}'}
    response = await client.post(f'/users/{default_user_id}/snippets', headers=auth_header)

    assert 401 == response.status_code
    assert {'detail': 'Could not validate credentials'} == response.json()
    assert 'Bearer' == response.headers['www-authenticate']


async def test_should_return_403_error_when_user_is_not_allowed_to_access_resource(client, auth_header):
    user_id = await create_user(client)
    response = await client.post(f'/users/{user_id}/snippets', headers=auth_header)  # type: ignore

    assert 403 == response.status_code
    assert {'detail': 'Access denied for the resource'} == response.json()


async def test_should_return_404_error_when_user_id_is_unknown(client, auth_header):
    user_id = uuid.uuid4()
    response = await client.post(f'/users/{user_id}/snippets', headers=auth_header)  # type: ignore

    assert 404 == response.status_code
    assert {'detail': f'no user with id {user_id} found'} == response.json()


async def test_should_return_422_error_when_payload_is_incorrect(client, default_user_id, auth_header):
    payload = {
        'title': '',
        'code': '',
        'print_line_number': 2,
        'language': 4.5,  # passes pydantic validation
        'style': False  # passes pydantic validation
    }
    response = await client.post(
        f'/users/{default_user_id}/snippets', json=payload, headers=auth_header  # type: ignore
    )

    assert 422 == response.status_code
    errors = {
        'detail': [
            {
                'loc': ['body', 'title'],
                'msg': 'ensure this value has at least 1 characters',
                'type': 'value_error.any_str.min_length',
                'ctx': {'limit_value': 1}
            },
            {
                'loc': ['body', 'code'],
                'msg': 'ensure this value has at least 1 characters',
                'type': 'value_error.any_str.min_length',
                'ctx': {'limit_value': 1}
            },
            {
                'loc': ['body', 'print_line_number'],
                'msg': 'value could not be parsed to a boolean',
                'type': 'type_error.bool'
            }
        ]
    }
    assert errors == response.json()


async def test_should_return_422_when_language_or_style_is_unknown(client, default_user_id, auth_header):
    payload = {
        'title': 'test',
        'code': 'print("hello!")',
        'print_line_number': False,
        'language': 'foo',
        'style': 'bar'
    }
    response = await client.post(
        f'/users/{default_user_id}/snippets', json=payload, headers=auth_header  # type: ignore
    )

    assert 422 == response.status_code
    errors = {
        'detail': [
            {
                'loc': ['body', 'language'],
                'msg': f'No language foo found. Please look at /languages for the list of available languages.',
                'type': 'value_error'
            },
            {
                'loc': ['body', 'style'],
                'msg': f'No style bar found. Please look at /styles for the list of available styles.',
                'type': 'value_error'
            }
        ]
    }
    assert errors == response.json()


@pytest.mark.parametrize(('partial_payload', 'print_line_number'), [
    ({}, False),
    ({'print_line_number': True}, True)
])
@pytest.mark.parametrize(('username', 'password'), [
    ('Bob', 'hell'),  # owner user
    ('admin', 'admin')  # admin user
])
async def test_should_create_user_snippet_given_correct_input(
        client, default_user_id, partial_payload, print_line_number, username, password
):
    payload = {
        'title': 'Test',
        'code': 'print("hello")',
        'language': 'python',
        'style': 'monokai',
        **partial_payload
    }
    auth_header = await get_authorization_header(client, username, password)
    response = await client.post(
        f'/users/{default_user_id}/snippets', json=payload, headers=auth_header
    )

    assert 201 == response.status_code
    data = response.json()
    assert data['print_line_number'] == print_line_number
    assert is_valid_snippet(data)

    user = await User.filter(pk=default_user_id).get()
    snippet = await Snippet.first()
    await snippet.fetch_related('user')
    assert snippet.user == user
