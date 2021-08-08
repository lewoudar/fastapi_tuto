import anyio
import click
from pygments.lexers import get_all_lexers
from pygments.styles import get_all_styles
from tortoise import Tortoise
from tortoise.exceptions import IntegrityError

from pastebin.config import TORTOISE_ORM
from pastebin.snippets.models import Language, Style
from pastebin.users.models import User


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
        await Tortoise.close_connections()

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
        await Tortoise.close_connections()

    anyio.run(add_styles)
    click.secho('styles inserted!', fg='green')


@cli.command('add-admin-user')
@click.option('-f', '--firstname', prompt='First name', help='your first name')
@click.option('-l', '--lastname', prompt='Last name', help='your last name')
@click.option('-e', '--email', prompt='Email address', help='your email address')
@click.password_option('-p', '--password', help='your user password')
@click.option('-P', '--pseudo', prompt='Pseudo', help='your pseudo or nickname')
def add_admin_user(firstname, lastname, email, password, pseudo):
    """Adds an administrator user."""

    async def create_user(firstname: str, lastname: str, email: str, password: str, pseudo: str) -> None:
        await Tortoise.init(config=TORTOISE_ORM)
        user = User(firstname=firstname, lastname=lastname, email=email, pseudo=pseudo, is_admin=True)
        user.set_password(password)
        try:
            await user.save()
        except IntegrityError as e:
            click.secho(f'Unable to create user, reason: {e}', fg='red')
            raise click.Abort()
        await Tortoise.close_connections()

    anyio.run(create_user, firstname, lastname, email, password, pseudo)
    click.secho(f'admin user {pseudo} created!', fg='green')
