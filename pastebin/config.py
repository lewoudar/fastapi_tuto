from typing import Union
from pydantic import BaseSettings, AnyUrl, PostgresDsn


class MysqlDsn(AnyUrl):
    allowed_schemes = {'mysql'}
    user_required = True


class SqliteDsn(AnyUrl):
    allowed_schemes = {'sqlite'}


class Settings(BaseSettings):
    db_url: Union[SqliteDsn, MysqlDsn, PostgresDsn] = 'sqlite://pastebin.db'


settings = Settings()

TORTOISE_ORM = {
    'connections': {'default': settings.db_url},
    'apps': {
        'pastebin': {
            'models': ['aerich.models'],
            'default_connection': 'default',
        }
    }
}
