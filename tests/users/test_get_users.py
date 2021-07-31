from typing import Dict

import pydantic
import pytest

from pastebin.users.schemas import UserOutput

pytestmark = pytest.mark.anyio


def is_valid_user(user: Dict[str, str]) -> bool:
    try:
        UserOutput(**user)
        return True
    except pydantic.ValidationError:
        return False


async def test_returns_list_of_users(client):
    response = await client.get('/users/')

    assert 200 == response.status_code
    for user in response.json():
        assert is_valid_user(user)


async def test_returns_a_single_user_given_its_pseudo(client):
    response = await client.get('/users/Bob')
    assert 200 == response.status_code
    assert is_valid_user(response.json())


async def test_returns_404_error_when_pseudo_is_unknown(client):
    response = await client.get('/users/foo')
    assert 404 == response.status_code
    assert {'detail': 'user foo not found'} == response.json()
