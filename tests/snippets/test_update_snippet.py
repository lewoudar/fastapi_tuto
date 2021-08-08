import uuid

import pytest

from pastebin.helpers import create_access_token
from pastebin.snippets.models import Snippet
from tests.helpers import create_snippet, is_valid_snippet, get_authorization_header

pytestmark = pytest.mark.anyio


async def test_should_return_401_error_when_user_is_not_authenticated(client):
    response = await client.patch(f'/snippets/{uuid.uuid4()}')

    assert 401 == response.status_code
    assert {'detail': 'Not authenticated'} == response.json()
    assert 'Bearer' == response.headers['www-authenticate']


@pytest.mark.parametrize('token_data', [
    {'foo': 'bar'},  # unknown claim
    {'sub': 'foo'}  # unknown user pseudo
])
async def test_should_return_401_error_when_token_is_not_valid(client, token_data):
    snippet = await Snippet.first()
    auth_header = {'Authorization': f'Bearer {create_access_token(token_data)}'}
    response = await client.patch(f'/snippets/{snippet.id}', headers=auth_header)

    assert 401 == response.status_code
    assert {'detail': 'Could not validate credentials'} == response.json()
    assert 'Bearer' == response.headers['www-authenticate']


async def test_should_return_403_error_when_user_is_not_allowed_to_access_resource(client, auth_header):
    snippet = await Snippet.filter(user__pseudo='fisher').get()
    response = await client.patch(f'/snippets/{snippet.id}', json={}, headers=auth_header)  # type: ignore

    assert 403 == response.status_code
    assert {'detail': 'Access denied for the resource'} == response.json()


async def test_should_return_404_error_when_snippet_id_is_unknown(client, auth_header):
    snippet_id = uuid.uuid4()
    response = await client.patch(f'/snippets/{snippet_id}', json={}, headers=auth_header)  # type: ignore

    assert 404 == response.status_code
    assert {'detail': f'no snippet with id {snippet_id} found'} == response.json()


async def test_should_return_422_error_when_snippet_id_is_not_a_uuid(client, auth_header):
    response = await client.patch('/snippets/43', json={}, headers=auth_header)  # type: ignore

    assert 422 == response.status_code
    assert response.json() == {
        'detail': [
            {
                'loc': ['path', 'snippet_id'],
                'msg': 'value is not a valid uuid',
                'type': 'type_error.uuid'
            }
        ]
    }


async def test_should_return_422_error_when_payload_is_incorrect(client, default_user_id, auth_header):
    snippet = await create_snippet(default_user_id)
    payload = {
        'title': '',
        'code': '',
        'print_line_number': 2,
        'language': 'python',
        'style': 'monokai'
    }
    response = await client.patch(f'/snippets/{snippet.id}', json=payload, headers=auth_header)  # type: ignore

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


async def test_should_return_422_error_when_language_or_style_is_unknown(client, default_user_id, auth_header):
    snippet = await create_snippet(default_user_id)
    payload = {
        'language': 'foo',
        'style': 'bar'
    }
    response = await client.patch(f'/snippets/{snippet.id}', json=payload, headers=auth_header)  # type: ignore

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


@pytest.mark.parametrize('payload', [
    {'title': 'new title', 'print_line_number': True, 'style': 'monokai'},
    {'code': 'puts "hello world"', 'language': 'Ruby'}
])
@pytest.mark.parametrize(('username', 'password'), [
    ('Bob', 'hell'),  # owner user
    ('admin', 'admin')  # admin user
])
async def test_should_update_snippet_given_correct_input(client, default_user_id, payload, username, password):
    snippet = await create_snippet(default_user_id)
    auth_header = await get_authorization_header(client, username, password)
    response = await client.patch(f'/snippets/{snippet.id}', json=payload, headers=auth_header)

    assert 200 == response.status_code
    data = response.json()
    assert is_valid_snippet(data)

    snippet = await Snippet.filter(pk=snippet.id).get().prefetch_related('language', 'style')
    for key, value in payload.items():
        assert data[key] == value
        if key in ['language', 'style']:
            assert getattr(snippet, key).name == value
        else:
            assert getattr(snippet, key) == value
