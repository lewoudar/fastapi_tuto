from typing import List, Dict, Any, cast

from fastapi import Depends, APIRouter, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response, HTMLResponse
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name

from pastebin.config import templates
from pastebin.dependencies import get_db_user, get_db_snippet, Pagination
from pastebin.exceptions import SnippetError
from pastebin.schemas import HttpError
from pastebin.users.models import User
from pastebin.users.views import router as user_router
from .models import Language, Style, Snippet
from .schemas import SnippetCreate, SnippetOutput, SnippetUpdate
from ..helpers import prepare_response

router = APIRouter(prefix='/snippets', tags=['snippets'])


def get_snippet_info_to_display(snippet: Snippet) -> Dict[str, Any]:
    return {
        'id': snippet.id,
        'title': snippet.title,
        'code': snippet.code,
        'print_line_number': snippet.print_line_number,
        'language': snippet.language.name,
        'style': snippet.style.name,
        'created_at': snippet.created_at
    }


@user_router.post('/{user_id}/snippets', tags=['snippets'], status_code=201, response_model=SnippetOutput)
async def create_snippet(snippet: SnippetCreate, user: User = Depends(get_db_user)):
    errors: List[Dict[str, str]] = []
    language = await Language.filter(name__iexact=snippet.language).get_or_none()
    if language is None:
        errors.append({'model': 'language', 'value': snippet.language})

    style = await Style.filter(name__iexact=snippet.style).get_or_none()
    if style is None:
        errors.append({'model': 'style', 'value': snippet.style})

    if errors:
        raise SnippetError(errors=errors)

    db_snippet = await Snippet.create(
        title=snippet.title,
        code=snippet.code,
        print_line_number=snippet.print_line_number,
        language=language,
        style=style,
        user=user
    )
    return jsonable_encoder(get_snippet_info_to_display(db_snippet))


def get_serialized_snippets(snippets: List[Snippet]) -> List[Dict[str, Any]]:
    return jsonable_encoder([get_snippet_info_to_display(snippet) for snippet in snippets])


@user_router.get('/{user_id}/snippets', response_model=List[SnippetOutput], tags=['snippets'])
async def get_user_snippets(
        request: Request,
        response: Response,
        user: User = Depends(get_db_user),
        pagination: Pagination = Depends()
):
    filters = {'user_id': user.id}
    to_prefetch = ['language', 'style']
    snippets = await prepare_response(
        request, response, Snippet, pagination.page, pagination.page_size, filters, to_prefetch
    )
    return get_serialized_snippets(cast(List[Snippet], snippets))


@router.get('/', response_model=List[SnippetOutput])
async def get_snippets(request: Request, response: Response, pagination: Pagination = Depends()):
    to_prefetch = ['language', 'style']
    snippets = await prepare_response(
        request, response, Snippet, pagination.page, pagination.page_size, to_prefetch=to_prefetch
    )
    return get_serialized_snippets(cast(List[Snippet], snippets))


@router.get(
    '/{snippet_id}',
    response_model=SnippetOutput,
    responses={
        404: {
            'description': 'Snippet not found',
            'model': HttpError
        }
    }
)
async def get_snippet(snippet: Snippet = Depends(get_db_snippet)):
    return jsonable_encoder(get_snippet_info_to_display(snippet))


@router.get(
    '/{snippet_id}/highlight',
    response_class=HTMLResponse,
    responses={
        404: {
            'description': 'Snippet not found',
            'model': HttpError
        }
    }
)
async def get_highlighted_snippet(request: Request, snippet: Snippet = Depends(get_db_snippet)):
    lexer = get_lexer_by_name(snippet.language.name)
    formatter = HtmlFormatter(title=snippet.title, style=snippet.style.name, linenos=snippet.print_line_number)
    context = {
        'request': request,
        'title': snippet.title,
        'highlighted': highlight(snippet.code, lexer, formatter)
    }
    return templates.TemplateResponse('highlight.jinja2', context)


@router.patch(
    '/{snippet_id}',
    response_model=SnippetOutput,
    responses={
        404: {
            'description': 'Snippet not found',
            'model': HttpError
        }
    }
)
async def update_snippet(snippet: SnippetUpdate, db_snippet: Snippet = Depends(get_db_snippet)):
    errors: List[Dict[str, str]] = []
    snippet_dict = snippet.dict(exclude_unset=True)
    if snippet.language is not None:
        language = await Language.filter(name__iexact=snippet.language).get_or_none()
        if language is None:
            errors.append({'model': 'language', 'value': snippet.language})
        else:
            snippet_dict['language'] = language

    if snippet.style is not None:
        style = await Style.filter(name__iexact=snippet.style).get_or_none()
        if style is None:
            errors.append({'model': 'style', 'value': snippet.style})
        else:
            snippet_dict['style'] = style

    if errors:
        raise SnippetError(errors=errors)

    for key, value in snippet_dict.items():
        setattr(db_snippet, key, value)
    await db_snippet.save()
    await db_snippet.fetch_related('language', 'style')

    return jsonable_encoder(get_snippet_info_to_display(db_snippet))


@router.delete(
    '/{snippet_id}',
    response_class=Response,
    status_code=204,
    responses={
        204: {
            'description': 'Snippet deleted'
        },
        404: {
            'description': 'Snippet not found',
            'model': HttpError
        }
    }
)
async def delete_snippet(snippet: Snippet = Depends(get_db_snippet)):
    await snippet.delete()
