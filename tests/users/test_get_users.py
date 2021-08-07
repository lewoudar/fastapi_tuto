import uuid

import pytest

from tests.helpers import (
    is_valid_user, assert_invalid_pagination_type_response, assert_invalid_pagination_value_response
)

pytestmark = pytest.mark.anyio


class TestGetListOfUsers:
    """Tests GET /users/"""

    async def test_returns_422_error_when_pagination_params_have_invalid_type(self, client):
        response = await client.get('/users/', params={'page': 'foo', 'page_size': 'bar'})
        assert_invalid_pagination_type_response(response)

    @pytest.mark.parametrize(('page_size', 'message', 'error_type', 'context_value'), [
        (101, 'ensure this value is less than or equal to 100', 'value_error.number.not_le', 100),
        (0, 'ensure this value is greater than or equal to 1', 'value_error.number.not_ge', 1)
    ])
    async def test_should_return_422_error_when_pagination_params_have_invalid_value(
            self, client, page_size, message, error_type, context_value
    ):
        response = await client.get('/users/', params={'page': 0, 'page_size': page_size})
        assert_invalid_pagination_value_response(response, message, error_type, context_value)

    async def test_returns_list_of_users_without_pagination(self, client):
        response = await client.get('/users/')

        assert 200 == response.status_code
        assert '' == response.headers['x-previous-page'] == response.headers['x-next-page']
        for user in response.json():
            assert is_valid_user(user)

    @pytest.mark.parametrize(('previous_url', 'next_url', 'page', 'page_size', 'data_length'), [
        ('', 'http://testserver/users/?page=2&page_size=1', 1, 1, 1),
        ('http://testserver/users/?page=1&page_size=1', 'http://testserver/users/?page=3&page_size=1', 2, 1, 1),
        ('http://testserver/users/?page=2&page_size=1', 'http://testserver/users/?page=4&page_size=1', 3, 1, 1),
        ('http://testserver/users/?page=3&page_size=1', '', 4, 1, 0)
    ])
    async def test_return_list_of_users_with_pagination(
            self, client, previous_url, next_url, page, page_size, data_length
    ):
        response = await client.get('/users/', params={'page': page, 'page_size': page_size})

        assert 200 == response.status_code
        assert previous_url == response.headers['x-previous-page']
        assert next_url == response.headers['x-next-page']
        data = response.json()
        assert data_length == len(data)
        for item in data:
            assert is_valid_user(item)


class TestGetSingleUser:
    """Tests GET /users/{user_id}"""

    async def test_returns_a_single_user_given_its_id(self, client, default_user_id):
        response = await client.get(f'/users/{default_user_id}')

        assert 200 == response.status_code
        assert is_valid_user(response.json())

    async def test_returns_404_error_when_user_id_is_unknown(self, client):
        user_id = uuid.uuid4()
        response = await client.get(f'/users/{user_id}')

        assert 404 == response.status_code
        assert {'detail': f'no user with id {user_id} found'} == response.json()

    async def test_returns_422_error_when_user_id_is_not_a_uuid(self, client):
        response = await client.get('/users/43')

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
