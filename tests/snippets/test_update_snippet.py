import uuid

import pytest

from pastebin.snippets.models import Snippet
from tests.helpers import create_snippet, is_valid_snippet

pytestmark = pytest.mark.anyio


async def test_should_return_404_error_when_snippet_id_is_unknown(client):
    snippet_id = uuid.uuid4()
    response = await client.patch(f'/snippets/{snippet_id}', json={})

    assert 404 == response.status_code
    assert {'detail': f'no snippet with id {snippet_id} found'} == response.json()


async def test_should_return_422_error_when_snippet_id_is_not_a_uuid(client):
    response = await client.patch('/snippets/43', json={})

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


async def test_should_return_422_error_when_payload_is_incorrect(client, default_user_id):
    snippet = await create_snippet(default_user_id)
    payload = {
        'title': '',
        'code': '',
        'print_line_number': 2,
        'language': 'python',
        'style': 'monokai'
    }
    response = await client.patch(f'/snippets/{snippet.id}', json=payload)

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


async def test_should_return_422_error_when_language_or_style_is_unknown(client, default_user_id):
    snippet = await create_snippet(default_user_id)
    payload = {
        'language': 'foo',
        'style': 'bar'
    }
    response = await client.patch(f'/snippets/{snippet.id}', json=payload)

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
async def test_should_update_snippet_given_correct_input(client, default_user_id, payload):
    snippet = await create_snippet(default_user_id)
    snippet_id = str(snippet.id)
    response = await client.patch(f'/snippets/{snippet.id}', json=payload)

    assert 200 == response.status_code
    data = response.json()
    assert is_valid_snippet(data)

    snippet = await Snippet.filter(pk=snippet_id).get().prefetch_related('language', 'style')
    for key, value in payload.items():
        assert data[key] == value
        if key in ['language', 'style']:
            assert getattr(snippet, key).name == value
        else:
            assert getattr(snippet, key) == value
