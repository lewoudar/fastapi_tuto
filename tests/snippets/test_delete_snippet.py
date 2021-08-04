import uuid

import pytest

from pastebin.snippets.models import Snippet
from tests.helpers import create_snippet

pytestmark = pytest.mark.anyio


async def test_should_return_404_when_snippet_id_is_unknown(client):
    snippet_id = uuid.uuid4()
    response = await client.delete(f'/snippets/{snippet_id}')

    assert 404 == response.status_code
    assert {'detail': f'no snippet with id {snippet_id} found'} == response.json()


async def test_should_return_422_error_when_snippet_id_is_not_a_uuid(client):
    response = await client.delete('/snippets/43')

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


async def test_should_delete_snippet_given_its_id(client, default_user_id):
    snippet = await create_snippet(default_user_id, title='my title')
    snippet_id = str(snippet.id)
    response = await client.delete(f'/snippets/{snippet.id}')

    assert 204 == response.status_code
    snippet = await Snippet.filter(pk=snippet_id).get_or_none()
    assert snippet is None
