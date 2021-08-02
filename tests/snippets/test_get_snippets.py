import pytest

from tests.helpers import is_valid_snippet

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
