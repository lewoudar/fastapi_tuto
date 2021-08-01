import typing

from tortoise import fields
from tortoise.validators import MinLengthValidator

from pastebin.abc import AbstractModel

if typing.TYPE_CHECKING:
    from pastebin.users.models import User


class Language(AbstractModel):
    name = fields.CharField(max_length=100, null=False)


class Style(AbstractModel):
    name = fields.CharField(max_length=100, null=False)


class Snippet(AbstractModel):
    title = fields.CharField(max_length=200, null=False, validators=[MinLengthValidator(1)])
    code = fields.TextField(null=False, validators=[MinLengthValidator(1)])
    print_line_number = fields.BooleanField(null=False, default=False)
    language: fields.ForeignKeyRelation[Language] = fields.ForeignKeyField('pastebin.Language')
    style: fields.ForeignKeyRelation[Style] = fields.ForeignKeyField('pastebin.Style')
    user: fields.ForeignKeyRelation['User'] = fields.ForeignKeyField('pastebin.User', related_name='snippets')
