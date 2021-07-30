from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from tortoise import Tortoise

from .config import TORTOISE_ORM
from .users import views


# tortoise uses decorator on_event which is now deprecated by starlette
# this is why I prefer to implement startup and shutdown functions by myself instead of
# relying of tortoise fastapi helper.
async def init_tortoise():
    await Tortoise.init(config=TORTOISE_ORM)


async def close_tortoise():
    await Tortoise.close_connections()


app = FastAPI(
    default_response_class=ORJSONResponse,
    on_startup=[init_tortoise],
    on_shutdown=[close_tortoise]
)
app.include_router(views.router)
