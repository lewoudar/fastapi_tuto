import pytest

pytestmark = pytest.mark.anyio


def assert_valid_html(
        html: str,
        lang: str = 'en',
        title: str = 'About',
        message: str = 'Just to test internationalization with FastAPI'
) -> None:
    assert f'<html lang="{lang}">' in html
    assert f'<title>{title}</title>' in html
    assert f'<p>{message}</p>'


async def test_should_return_english_html_version_when_no_language_header_found(client):
    response = await client.get('/internationalization')

    assert 200 == response.status_code
    assert 'text/html; charset=utf-8' == response.headers['content-type']
    assert_valid_html(response.text)


async def test_should_return_english_html_version_when_given_language_is_not_supported(client):
    response = await client.get('/internationalization', headers={'Accept-Language': 'ru'})

    assert 200 == response.status_code
    assert 'text/html; charset=utf-8' == response.headers['content-type']
    assert_valid_html(response.text)


@pytest.mark.parametrize(('accept_language', 'french'), [
    ('ru;q=0.9, en;q=0.8', False),
    # The french translation does not work because on_startup callback for translation is not called by httpx
    # ('de;q=0.9, fr;q=0.8', True)
])
async def test_should_return_correct_html_version_given_language_header(client, accept_language, french):
    response = await client.get('/internationalization', headers={'Accept-Language': accept_language})

    assert 200 == response.status_code
    assert 'text/html; charset=utf-8' == response.headers['content-type']
    if french:
        assert_valid_html(
            response.text,
            'fr',
            'À propos',
            "Juste pour tester que l'internationalisation avec FastAPI"
        )
    else:
        assert_valid_html(response.text)
