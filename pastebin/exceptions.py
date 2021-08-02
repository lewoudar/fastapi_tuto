from typing import List, Dict

from fastapi.responses import ORJSONResponse


class SnippetError(Exception):
    def __init__(self, errors: List[Dict[str, str]]):
        self.errors = errors


async def handle_snippet_error(_, exc: SnippetError) -> ORJSONResponse:
    errors = []
    for error in exc.errors:
        model = error['model']
        value = error['value']
        errors.append({
            'loc': ['body', error['model']],
            'msg': (
                f'No {model} {value} found.'
                f' Please look at /{model}s for the list of available {model}s.'
            ),
            'type': 'value_error'
        })

    return ORJSONResponse(status_code=422, content={'detail': errors})


exception_handlers = {
    SnippetError: handle_snippet_error
}
