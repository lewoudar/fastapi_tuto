import uuid

import pytest

from tests.helpers import (
    is_valid_snippet, create_snippet, assert_invalid_pagination_type_response,
    assert_invalid_pagination_value_response
)

pytestmark = pytest.mark.anyio


class TestGetUserSnippets:
    """Tests GET /users/{user_id}/snippets"""

    async def test_returns_422_error_when_pagination_params_have_invalid_type(self, client, default_user_id):
        response = await client.get(f'/users/{default_user_id}/snippets', params={'page': 'foo', 'page_size': 'bar'})
        assert_invalid_pagination_type_response(response)

    @pytest.mark.parametrize(('page_size', 'message', 'error_type', 'context_value'), [
        (101, 'ensure this value is less than or equal to 100', 'value_error.number.not_le', 100),
        (0, 'ensure this value is greater than 0', 'value_error.number.not_gt', 0)
    ])
    async def test_should_return_422_error_when_pagination_params_have_invalid_value(
            self, client, default_user_id, page_size, message, error_type, context_value
    ):
        response = await client.get(f'/users/{default_user_id}/snippets', params={'page': 0, 'page_size': page_size})
        assert_invalid_pagination_value_response(response, message, error_type, context_value)

    async def test_returns_user_list_of_snippets_without_pagination(self, client, default_user_id):
        response = await client.get(f'/users/{default_user_id}/snippets')

        assert 200 == response.status_code
        data = response.json()
        assert '' == response.headers['x-previous-page'] == response.headers['x-next-page']
        assert 2 == len(data)
        for item in data:
            assert is_valid_snippet(item)

    @pytest.mark.parametrize(('previous_url', 'next_url', 'page', 'page_size', 'data_length'), [
        ('', '?page=2&page_size=1', 1, 1, 1),
        ('?page=1&page_size=1', '?page=3&page_size=1', 2, 1, 1),
        ('?page=2&page_size=1', '', 3, 1, 0)
    ])
    async def test_returns_user_list_of_snippets_with_pagination(
            self, client, default_user_id, previous_url, next_url, page, page_size, data_length
    ):
        response = await client.get(f'/users/{default_user_id}/snippets', params={'page': page, 'page_size': page_size})

        assert 200 == response.status_code
        if page == 1:
            assert response.headers['x-previous-page'] == ''
        else:
            assert response.headers['x-previous-page'].endswith(previous_url)
        if page == 3:
            assert response.headers['x-next-page'] == ''
        else:
            assert response.headers['x-next-page'].endswith(next_url)

        data = response.json()
        assert data_length == len(data)
        for item in data:
            assert is_valid_snippet(item)


class TestGetSnippets:
    """Tests GET /snippets/"""

    async def test_returns_422_error_when_pagination_params_have_invalid_type(self, client):
        response = await client.get('/snippets/', params={'page': 'foo', 'page_size': 'bar'})
        assert_invalid_pagination_type_response(response)

    @pytest.mark.parametrize(('page_size', 'message', 'error_type', 'context_value'), [
        (101, 'ensure this value is less than or equal to 100', 'value_error.number.not_le', 100),
        (0, 'ensure this value is greater than 0', 'value_error.number.not_gt', 0)
    ])
    async def test_should_return_422_error_when_pagination_params_have_invalid_value(
            self, client, page_size, message, error_type, context_value
    ):
        response = await client.get('/snippets/', params={'page': 0, 'page_size': page_size})
        assert_invalid_pagination_value_response(response, message, error_type, context_value)

    async def test_returns_list_of_all_snippets_without_pagination(self, client, default_user_id):
        response = await client.get('/snippets/')

        assert 200 == response.status_code
        data = response.json()
        assert '' == response.headers['x-previous-page'] == response.headers['x-next-page']
        assert 3 == len(data)
        for item in data:
            assert is_valid_snippet(item)

    @pytest.mark.parametrize(('previous_url', 'next_url', 'page', 'page_size', 'data_length'), [
        ('', 'http://testserver/snippets/?page=2&page_size=2', 1, 2, 2),
        ('http://testserver/snippets/?page=1&page_size=2', '', 2, 2, 1),
        ('http://testserver/snippets/?page=2&page_size=2', '', 3, 2, 0)
    ])
    async def test_return_list_of_snippets_with_pagination(
            self, client, previous_url, next_url, page, page_size, data_length
    ):
        response = await client.get('/snippets/', params={'page': page, 'page_size': page_size})

        assert 200 == response.status_code
        assert previous_url == response.headers['x-previous-page']
        assert next_url == response.headers['x-next-page']
        data = response.json()
        assert data_length == len(data)
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
