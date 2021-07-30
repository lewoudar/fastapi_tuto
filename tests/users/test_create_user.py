import pytest

from tests.helpers import is_uuid, is_datetime

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


@pytest.mark.parametrize('field', ['firstname', 'lastname', 'pseudo', 'password'])
async def test_returns_422_error_when_field_does_not_have_the_correct_type(client, field):
    payload = {
        'firstname': 'Bob',
        'lastname': 'Bar',
        'pseudo': 'Bob',
        'email': 'hello@bar.com',
        'password': 'oops',
        **{field: 42}
    }
    response = await client.post('/users/', json=payload)

    assert 422 == response.status_code
    message = {'detail': [{'loc': ['body', field], 'msg': 'str type expected', 'type': 'type_error.str'}]}
    assert message == response.json()


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
    data = response.json()
    assert is_datetime(data.pop('created_at'))
    assert is_uuid(data.pop('id'))
    payload.pop('password')
    assert data == payload
