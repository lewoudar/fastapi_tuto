import uuid

import pytest

from tests.helpers import is_valid_snippet, create_snippet

pytestmark = pytest.mark.anyio


async def test_returns_user_list_of_snippets(client, default_user_id):
    response = await client.get(f'/users/{default_user_id}/snippets')

    assert 200 == response.status_code
    data = response.json()
    assert 2 == len(data)
    for item in data:
        assert is_valid_snippet(item)


async def test_returns_list_of_all_snippets(client, default_user_id):
    response = await client.get('/snippets/')

    assert 200 == response.status_code
    data = response.json()
    assert 3 == len(data)
    for item in data:
        assert is_valid_snippet(item)


class TestGetSingleSnippet:
    """Tests GET /{snippet_id}"""

    async def test_returns_404_error_when_snippet_id_is_unknown(self, client):
        snippet_id = str(uuid.uuid4())
        response = await client.get(f'/snippets/{snippet_id}')

        assert 404 == response.status_code
        assert {'detail': f'no snippet with id {snippet_id} found'} == response.json()

    async def test_returns_422_error_when_snippet_id_is_not_a_uuid(self, client):
        response = await client.get('/snippets/43')

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

    async def test_returns_a_single_snippet_given_its_id(self, client, default_user_id):
        snippet = await create_snippet(default_user_id)
        response = await client.get(f'/snippets/{snippet.id}')

        assert 200 == response.status_code
        data = response.json()

        assert is_valid_snippet(data)
        assert str(snippet.id) == data['id']


class TestGetHighlightedSnippet:
    """Tests GET /snippets/{snippet_id}/highlight"""

    async def test_should_return_404_error_when_snippet_id_is_unknown(self, client):
        snippet_id = uuid.uuid4()
        response = await client.get(f'/snippets/{snippet_id}/highlight')

        assert 404 == response.status_code
        assert {'detail': f'no snippet with id {snippet_id} found'} == response.json()

    async def test_should_return_422_error_when_snippet_id_is_not_a_uuid(self, client):
        response = await client.get(f'/snippets/43/highlight')

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

    async def test_should_return_highlighted_snippet_when_given_its_id(self, client, default_user_id):
        snippet = await create_snippet(default_user_id)
        response = await client.get(f'/snippets/{snippet.id}/highlight')

        assert 200 == response.status_code
        assert 'text/html; charset=utf-8' == response.headers['content-type']
        assert f'<title>{snippet.title}</title>' in response.text
        assert f'<h2>{snippet.title}</h2>' in response.text
        assert '<div class="highlight">' in response.text
        assert 'hello' in response.text
