from typing import Dict

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
