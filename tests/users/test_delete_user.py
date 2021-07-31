import uuid

import pytest

from pastebin.users.models import User

pytestmark = pytest.mark.anyio


async def test_should_return_404_error_when_user_id_is_unknown(client):
    user_id = uuid.uuid4()
    response = await client.delete(f'/users/{user_id}')

    assert 404 == response.status_code
    assert {'detail': f'user with id {user_id} not found'} == response.json()


async def test_should_delete_user_when_given_correct_user_id(client, default_user_id):
    response = await client.delete(f'/users/{default_user_id}')

    assert 204 == response.status_code
    user = await User.filter(pk=default_user_id).get_or_none()
    assert user is None
