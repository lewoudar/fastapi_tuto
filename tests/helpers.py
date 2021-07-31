from typing import Dict

import pydantic

from pastebin.users.schemas import UserOutput


def is_valid_user(user: Dict[str, str]) -> bool:
    try:
        UserOutput(**user)
        return True
    except pydantic.ValidationError:
        return False
