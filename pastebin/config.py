import secrets
from pathlib import Path
from typing import Union

from fastapi.templating import Jinja2Templates
from pydantic import BaseSettings, AnyUrl, PostgresDsn


class MysqlDsn(AnyUrl):
    allowed_schemes = {'mysql'}
    user_required = True


class SqliteDsn(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: str):
        if not isinstance(v, str):
            raise TypeError('string required')
        if not v.startswith('sqlite://'):
            raise ValueError('Not a valid sqlite uri')
        return cls(v)

    def __repr__(self):
        return f'SqliteDsn({super().__repr__()})'


class Settings(BaseSettings):
    db_url: Union[SqliteDsn, MysqlDsn, PostgresDsn] = 'sqlite://pastebin.db'
    secret_key: str = secrets.token_urlsafe(32)
    jwt_algorithm: str = 'HS256'
    jwt_token_expire_seconds: int = 30 * 60


settings = Settings()

TORTOISE_ORM = {
    'connections': {'default': settings.db_url},
    'apps': {
        'pastebin': {
            'models': ['aerich.models', 'pastebin.users.models', 'pastebin.snippets.models'],
            'default_connection': 'default',
        }
    }
}

PAGINATION_HEADERS = {
    'headers': {
        'X-Previous-Page': {
            'schema': {
                'type': 'string',
                'format': 'url',
                'example': 'https://server.com?page=1&page_size=30'
            },
            'description': (
                'The url where to find previous items relative to the current data set. An empty value means there is'
                'no previous item.'
            )
        },
        'X-Next-Page': {
            'schema': {
                'type': 'string',
                'format': 'url',
                'example': 'https://server.com?page=1&page_size=30'
            },
            'description': (
                'The url where to find previous items relative to the current data set. An empty value means there is'
                'no next item.'
            )
        }
    }
}

templates_dir = Path(__file__).parent / 'templates'
templates = Jinja2Templates(directory=f'{templates_dir}')
