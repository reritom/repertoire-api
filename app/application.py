from fastapi import APIRouter, FastAPI

from app.accounts.models import *  # noqa
from app.auth.routers import router as auth_router
from app.tasks.models import *  # noqa


def create_app():
    app = FastAPI(title="Repertoire API")

    api = APIRouter(prefix="/api")
    api.include_router(auth_router)

    app.include_router(api)
    return app
