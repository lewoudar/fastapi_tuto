import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class LanguageSchema(BaseModel):
    id: uuid.UUID
    name: str = Field(..., example='Python', description='Language name')
    created_at: datetime


class HttpError(BaseModel):
    detail: str
