from typing import List, Dict, Any

from fastapi import Depends, APIRouter
from fastapi.encoders import jsonable_encoder

from pastebin.dependencies import get_db_user, get_db_snippet
from pastebin.exceptions import SnippetError
from pastebin.schemas import HttpError
from pastebin.users.models import User
from pastebin.users.views import router as user_router
from .models import Language, Style, Snippet
from .schemas import SnippetCreate, SnippetOutput, SnippetUpdate

router = APIRouter(prefix='/snippets', tags=['snippets'])


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
    return {**snippet.dict(), 'id': db_snippet.id, 'created_at': db_snippet.created_at}


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


def get_serialized_snippets(snippets: List[Snippet]) -> List[Dict[str, Any]]:
    return jsonable_encoder([get_snippet_info_to_display(snippet) for snippet in snippets])


@user_router.get('/{user_id}/snippets', response_model=List[SnippetOutput], tags=['snippets'])
async def get_user_snippets(user: User = Depends(get_db_user)):
    snippets = await Snippet.filter(user_id=user.id).prefetch_related('language', 'style')
    return get_serialized_snippets(snippets)


@router.get('/', response_model=List[SnippetOutput])
async def get_snippets():
    snippets = await Snippet.all().prefetch_related('language', 'style')
    return get_serialized_snippets(snippets)


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
