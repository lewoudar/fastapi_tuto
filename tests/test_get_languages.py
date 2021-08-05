import pydantic
import pytest

from pastebin.schemas import LanguageSchema
from tests.helpers import assert_invalid_pagination_type_response, assert_invalid_pagination_value_response

pytestmark = pytest.mark.anyio


def is_valid_language(item: dict) -> bool:
    try:
        LanguageSchema.parse_obj(item)
        return True
    except pydantic.ValidationError:
        return False


async def test_returns_422_error_when_pagination_params_have_invalid_type(client):
    response = await client.get('/languages', params={'page': 'foo', 'page_size': 'bar'})
    assert_invalid_pagination_type_response(response)


@pytest.mark.parametrize(('page_size', 'message', 'error_type', 'context_value'), [
    (101, 'ensure this value is less than or equal to 100', 'value_error.number.not_le', 100),
    (0, 'ensure this value is greater than or equal to 1', 'value_error.number.not_ge', 1)
])
async def test_should_return_422_error_when_pagination_params_have_invalid_value(
        client, page_size, message, error_type, context_value
):
    response = await client.get('/languages', params={'page': 0, 'page_size': page_size})
    assert_invalid_pagination_value_response(response, message, error_type, context_value)


async def test_returns_languages_without_pagination(client):
    response = await client.get('/languages')

    assert 200 == response.status_code
    assert '' == response.headers['x-previous-page'] == response.headers['x-next-page']

    data = response.json()
    assert len(data) > 0
    for item in response.json():
        assert is_valid_language(item)


@pytest.mark.parametrize(('previous_url', 'next_url', 'page', 'page_size', 'data_length'), [
    ('', 'http://testserver/languages?page=2&page_size=1', 1, 1, 1),
    ('http://testserver/languages?page=1&page_size=1', 'http://testserver/languages?page=3&page_size=1', 2, 1, 1),
    ('http://testserver/languages?page=2&page_size=1', '', 3, 1, 0)
])
async def test_returns_languages_with_pagination(client, previous_url, next_url, page, page_size, data_length):
    response = await client.get('/languages', params={'page': page, 'page_size': page_size})

    assert 200 == response.status_code
    assert previous_url == response.headers['x-previous-page']
    assert next_url == response.headers['x-next-page']

    data = response.json()
    assert data_length == len(data)
    for item in data:
        assert is_valid_language(item)
