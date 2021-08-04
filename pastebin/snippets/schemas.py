import datetime
import uuid
from functools import partial
from typing import Optional

from pydantic import BaseModel, Field

title_field = partial(Field, description='snippet description', example='my super snippet', min_length=1)
code_field = partial(Field, description='snippet code', example="print('Hello world')", min_length=1)
language_field = partial(Field, description='snippet language', example='python')
style_field = partial(Field, description='snippet style when displaying code in html', example='monokai')


class SnippetCreate(BaseModel):
    title: str = title_field(default=...)
    code: str = code_field(default=...)
    print_line_number: bool = Field(
        False, description='choose whether or not to print line number when choosing the html display'
    )
    language: str = language_field(default=...)
    style: str = style_field(default=...)


class SnippetOutput(SnippetCreate):
    id: uuid.UUID = Field(..., description='snippet id')
    created_at: datetime.datetime = Field(..., description='snippet creation date')


class SnippetUpdate(SnippetCreate):
    title: Optional[str] = title_field(default=None)
    code: Optional[str] = code_field(default=None)
    language: Optional[str] = language_field(default=None)
    style: Optional[str] = style_field(default=None)
