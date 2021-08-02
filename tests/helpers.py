from typing import Dict

import pydantic

from pastebin.snippets.schemas import SnippetOutput
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
