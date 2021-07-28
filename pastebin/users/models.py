import bcrypt
import pydantic
from tortoise import fields
from tortoise.exceptions import ValidationError

from pastebin.abc import AbstractModel


def email_validator(value: str) -> None:
    email_class = pydantic.create_model('Email', email=(pydantic.EmailStr, ...))
    try:
        email_class(email=value)  # type: ignore
    except pydantic.ValidationError:
        raise ValidationError(f'{value} is not a valid email')


class User(AbstractModel):
    id = fields.UUIDField(pk=True)
    firstname = fields.CharField(max_length=255, null=False)
    lastname = fields.CharField(max_length=255, null=False)
    password_hash = fields.CharField(max_length=255, null=False)
    email = fields.CharField(max_length=255, null=False, validators=[email_validator])
    is_admin = fields.BooleanField(null=False, default=False)

    def set_password(self, password: str) -> None:
        _hash = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
        self.password_hash = _hash.decode('utf8')

    def check_password(self, password: str) -> bool:
        if self.password_hash is not None:
            expected_hash = self.password_hash.encode('utf8')
            return bcrypt.checkpw(password.encode('utf8'), expected_hash)
        return False

    class Meta:
        table = 'user'
