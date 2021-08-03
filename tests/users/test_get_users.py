import uuid

import pytest

from tests.helpers import is_valid_user

pytestmark = pytest.mark.anyio


async def test_returns_list_of_users(client):
    response = await client.get('/users/')

    assert 200 == response.status_code
    for user in response.json():
        assert is_valid_user(user)


async def test_returns_a_single_user_given_its_id(client, default_user_id):
    response = await client.get(f'/users/{default_user_id}')

    assert 200 == response.status_code
    assert is_valid_user(response.json())


async def test_returns_404_error_when_user_id_is_unknown(client):
    user_id = uuid.uuid4()
    response = await client.get(f'/users/{user_id}')

    assert 404 == response.status_code
    assert {'detail': f'no user with id {user_id} found'} == response.json()


async def test_returns_422_error_when_user_id_is_not_a_uuid(client):
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
