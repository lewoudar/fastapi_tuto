from pydantic import BaseModel


class HttpError(BaseModel):
    detail: str
