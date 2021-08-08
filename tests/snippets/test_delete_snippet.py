import uuid

import pytest

from pastebin.helpers import create_access_token
from pastebin.snippets.models import Snippet
from tests.helpers import create_snippet, get_authorization_header

pytestmark = pytest.mark.anyio


async def test_should_return_401_error_when_user_is_not_authenticated(client):
    response = await client.delete(f'/snippets/{uuid.uuid4()}')

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
    response = await client.delete(f'/snippets/{snippet.id}', headers=auth_header)

    assert 401 == response.status_code
    assert {'detail': 'Could not validate credentials'} == response.json()
    assert 'Bearer' == response.headers['www-authenticate']


async def test_should_return_403_error_when_user_is_not_allowed_to_access_resource(client, auth_header):
    snippet = await Snippet.filter(user__pseudo='fisher').get()
    response = await client.delete(f'/snippets/{snippet.id}', headers=auth_header)  # type: ignore

    assert 403 == response.status_code
    assert {'detail': 'Access denied for the resource'} == response.json()


async def test_should_return_404_when_snippet_id_is_unknown(client, auth_header):
    snippet_id = uuid.uuid4()
    response = await client.delete(f'/snippets/{snippet_id}', headers=auth_header)  # type: ignore

    assert 404 == response.status_code
    assert {'detail': f'no snippet with id {snippet_id} found'} == response.json()


async def test_should_return_422_error_when_snippet_id_is_not_a_uuid(client, auth_header):
    response = await client.delete('/snippets/43', headers=auth_header)  # type: ignore

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


@pytest.mark.parametrize(('username', 'password'), [
    ('Bob', 'hell'),  # owner user
    ('admin', 'admin')  # admin user
])
async def test_should_delete_snippet_given_its_id(client, default_user_id, username, password):
    snippet = await create_snippet(default_user_id, title='my title')
    auth_header = await get_authorization_header(client, username, password)
    response = await client.delete(f'/snippets/{snippet.id}', headers=auth_header)

    assert 204 == response.status_code
    snippet = await Snippet.filter(pk=snippet.id).get_or_none()
    assert snippet is None
