import uuid
from datetime import datetime
from typing import Dict

import pydantic

from pastebin.users.schemas import UserOutput


def is_uuid(value: str) -> bool:
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False


def is_datetime(value: str) -> bool:
    try:
        datetime.fromisoformat(value)
        return True
    except (TypeError, ValueError):
        return False


def is_valid_user(user: Dict[str, str]) -> bool:
    try:
        UserOutput(**user)
        return True
    except pydantic.ValidationError:
        return False
