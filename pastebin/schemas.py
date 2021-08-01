import uuid

from pydantic import BaseModel, Field


class BaseLanguage(BaseModel):
    id: uuid.UUID


class LanguageSchema(BaseLanguage):
    name: str = Field(..., example='Python', description='language name')


class StyleSchema(BaseLanguage):
    name: str = Field(..., example='monokai', description='snippet display style')


class HttpError(BaseModel):
    detail: str
