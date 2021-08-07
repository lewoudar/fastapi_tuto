from typing import Dict

import httpx
import pydantic

from pastebin.snippets.models import Snippet, Language, Style
from pastebin.snippets.schemas import SnippetOutput
from pastebin.users.models import User
from pastebin.users.schemas import UserOutput


def is_valid_user(user: Dict[str, str]) -> bool:
    try:
        UserOutput(**user)
        return True
    except pydantic.ValidationError:
        return False


def is_valid_snippet(snippet: Dict[str, str]) -> bool:
    try:
        SnippetOutput(**snippet)
        return True
    except pydantic.ValidationError:
        return False


async def create_snippet(
        user_id: str,
        title: str = 'test',
        code: str = 'print("hello")',
        language: str = 'python',
        style: str = 'friendly',
        print_line_number: bool = False
) -> Snippet:
    language = await Language.filter(name__iexact=language).get()
    style = await Style.filter(name__iexact=style).get()
    user = await User.filter(pk=user_id).get()
    return await Snippet.create(
        title=title,
        code=code,
        language=language,
        style=style,
        print_line_number=print_line_number,
        user=user
    )


def assert_invalid_pagination_type_response(response: httpx.Response) -> None:
    assert 422 == response.status_code
    assert response.json() == {
        'detail': [
            {
                'loc': ['query', 'page'],
                'msg': 'value is not a valid integer',
                'type': 'type_error.integer'
            },
            {
                'loc': ['query', 'page_size'],
                'msg': 'value is not a valid integer',
                'type': 'type_error.integer'
            }
        ]
    }


def assert_invalid_pagination_value_response(
        response: httpx.Response, message: str, error_type: str, context_value: int
) -> None:
    assert 422 == response.status_code
    assert response.json() == {
        'detail': [
            {
                'loc': ['query', 'page'],
                'msg': 'ensure this value is greater than or equal to 1',
                'type': 'value_error.number.not_ge',
                'ctx': {'limit_value': 1}
            },
            {
                'loc': ['query', 'page_size'],
                'msg': message,
                'type': error_type,
                'ctx': {'limit_value': context_value}
            }
        ]
    }


async def create_user(client: httpx.AsyncClient) -> str:
    payload = {
        'firstname': 'Pablo',
        'lastname': 'Escobar',
        'pseudo': 'escobar',
        'email': 'escobar@drug.com',
        'password': 'leaf'
    }
    response = await client.post('/users/', json=payload)
    return response.json()['id']


async def get_authorization_header(client: httpx.AsyncClient, username: str, password: str) -> Dict[str, str]:
    response = await client.post('/token', data={'username': username, 'password': password})
    return {'Authorization': f'Bearer {response.json()["access_token"]}'}
