import bcrypt
import pydantic
from tortoise import fields
from tortoise.exceptions import ValidationError
from tortoise.validators import MinLengthValidator

from pastebin.abc import AbstractModel


def email_validator(value: str) -> None:
    email_class = pydantic.create_model('Email', email=(pydantic.EmailStr, ...))
    try:
        email_class(email=value)  # type: ignore
    except pydantic.ValidationError:
        raise ValidationError(f'{value} is not a valid email')


class User(AbstractModel):
    id = fields.UUIDField(pk=True)
    firstname = fields.CharField(max_length=255, null=False, validators=[MinLengthValidator(1)])
    lastname = fields.CharField(max_length=255, null=False, validators=[MinLengthValidator(2)])
    pseudo = fields.CharField(max_length=255, null=False, unique=True, validators=[MinLengthValidator(2)])
    password_hash = fields.CharField(max_length=255, null=False)
    email = fields.CharField(max_length=255, null=False, unique=True, validators=[email_validator])
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

    class PydanticMeta:
        exclude = ['is_admin', 'updated_at', 'password_hash']
