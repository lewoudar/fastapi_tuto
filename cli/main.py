import anyio
import click
from pygments.lexers import get_all_lexers
from pygments.styles import get_all_styles
from tortoise import Tortoise

from pastebin.config import TORTOISE_ORM
from pastebin.snippets.models import Language, Style


@click.group()
def cli():
    """Pastebin CLI manager"""


@cli.command('add-lang-to-db')
def add_languages_to_db():
    """Add pygments languages in the database."""

    async def insert_language(language: str) -> None:
        await Language.create(name=language)

    async def add_languages() -> None:
        await Tortoise.init(config=TORTOISE_ORM)
        async with anyio.create_task_group() as tg:
            for item in get_all_lexers():
                tg.start_soon(insert_language, item[0])

    anyio.run(add_languages)
    click.secho('languages inserted!', fg='green')


@cli.command('add-styles-to-db')
def add_styles_to_db():
    """Add pygments styles in the database."""

    async def insert_style(style: str) -> None:
        await Style.create(name=style)

    async def add_styles() -> None:
        await Tortoise.init(config=TORTOISE_ORM)
        async with anyio.create_task_group() as tg:
            for style in get_all_styles():
                tg.start_soon(insert_style, style)

    anyio.run(add_styles)
    click.secho('styles inserted!', fg='green')
