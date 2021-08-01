import pydantic
import pytest

from pastebin.schemas import StyleSchema


def is_valid_style(item: dict) -> bool:
    try:
        StyleSchema.parse_obj(item)
        return True
    except pydantic.ValidationError:
        return False


@pytest.mark.anyio
async def test_returns_styles(client):
    response = await client.get('/styles')

    assert 200 == response.status_code

    data = response.json()
    assert len(data) > 0
    for item in response.json():
        assert is_valid_style(item)
