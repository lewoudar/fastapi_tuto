import uuid

from pydantic import BaseModel, Field


class SnippetCreate(BaseModel):
    title: str = Field(..., description='snippet description', example='my super snippet', min_length=1)
    code: str = Field(..., description='snippet code', example="print('Hello world')", min_length=1)
    print_line_number: bool = Field(
        False,
        description='choose whether or not to print line number when choosing the html display'
    )
    language: str = Field(..., description='snippet language', example='python')
    style: str = Field(..., description='snippet style when displaying code in html')


class SnippetOutput(SnippetCreate):
    id: uuid.UUID = Field(..., description='snippet id', example='')
