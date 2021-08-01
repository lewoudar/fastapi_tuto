import pydantic
import pytest

from pastebin.schemas import LanguageSchema


def is_valid_language(item: dict) -> bool:
    try:
        LanguageSchema.parse_obj(item)
        return True
    except pydantic.ValidationError:
        return False


@pytest.mark.anyio
async def test_returns_languages(client):
    response = await client.get('/languages')

    assert 200 == response.status_code
    for item in response.json():
        assert is_valid_language(item)
