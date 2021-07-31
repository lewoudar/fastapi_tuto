import pytest

from pastebin.users.models import User
from tests.helpers import is_valid_user

pytestmark = pytest.mark.anyio


@pytest.mark.parametrize('field', ['firstname', 'lastname', 'pseudo', 'email', 'password'])
async def test_returns_422_error_when_missing_field_in_input(client, field):
    payload = {
        'firstname': 'Bob',
        'lastname': 'Bar',
        'pseudo': 'Bob',
        'email': 'hello@bar.com',
        'password': 'oops'
    }
    payload.pop(field)
    response = await client.post('/users/', json=payload)

    assert 422 == response.status_code
    message = {'detail': [{'loc': ['body', field], 'msg': 'field required', 'type': 'value_error.missing'}]}
    assert message == response.json()


async def test_returns_422_error_when_field_does_not_have_the_correct_type(client):
    payload = {
        'firstname': 42,
        'lastname': 42,
        'pseudo': 42,
        'email': 'hello@bar.com',
        'password': 42
    }
    response = await client.post('/users/', json=payload)

    assert 422 == response.status_code
    fields = ['firstname', 'lastname', 'pseudo', 'password']
    errors = [{'loc': ['body', field], 'msg': 'str type expected', 'type': 'type_error.str'} for field in fields]
    assert {'detail': errors} == response.json()


@pytest.mark.parametrize('email', [42, 'foo'])
async def test_returns_422_when_email_is_not_valid(client, email):
    payload = {
        'firstname': 'Bob',
        'lastname': 'Bar',
        'pseudo': 'Bob',
        'email': email,
        'password': 'oops'
    }
    response = await client.post('/users/', json=payload)

    assert 422 == response.status_code
    message = {
        'detail': [{
            'loc': ['body', 'email'], 'msg': 'value is not a valid email address', 'type': 'value_error.email'
        }]
    }
    assert message == response.json()


async def test_returns_422_error_when_field_does_not_have_the_correct_length(client):
    payload = {
        'firstname': '',
        'lastname': 'B',
        'pseudo': 'B',
        'email': 'foo@bar.com',
        'password': ''
    }
    response = await client.post('/users/', json=payload)

    assert 422 == response.status_code
    errors = []
    for field, min_length in [('firstname', 1), ('lastname', 2), ('pseudo', 2), ('password', 1)]:
        errors.append({
            'loc': ['body', field],
            'msg': f'{field} must have a minimum length of {min_length}',
            'type': 'value_error'
        })
    assert {'detail': errors} == response.json()


async def test_returns_409_error_when_pseudo_already_exists(client):
    payload = {
        'firstname': 'Bob',
        'lastname': 'Bar',
        'pseudo': 'Bob',
        'email': 'hello@bar.com',
        'password': 'oops'
    }
    response = await client.post('/users/', json=payload)

    assert 409 == response.status_code
    assert {'detail': 'A user with pseudo Bob already exists'} == response.json()


async def test_returns_409_error_when_email_already_exists(client):
    payload = {
        'firstname': 'Bob',
        'lastname': 'Bar',
        'pseudo': 'Pseudo',
        'email': 'bob@foo.com',
        'password': 'oops'
    }
    response = await client.post('/users/', json=payload)

    assert 409 == response.status_code
    assert {'detail': 'A user with email bob@foo.com already exists'} == response.json()


async def test_creates_user_and_returns_it_when_passing_valid_input(client):
    payload = {
        'firstname': 'Kevin',
        'lastname': 'Bar',
        'pseudo': 'Kevin',
        'email': 'kevin@foo.com',
        'password': 'pass'
    }
    response = await client.post('/users/', json=payload)

    assert 201 == response.status_code

    user = await User.filter(pseudo='Kevin').get_or_none()
    assert user is not None
    password = payload.pop('password')
    for key, value in payload.items():
        assert getattr(user, key) == value

    assert user.check_password(password)
    assert is_valid_user(response.json())
