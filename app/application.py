from fastapi import FastAPI

from app.accounts.models import *  # noqa
from app.tasks.models import *  # noqa


def create_app():
    app = FastAPI()
    return app
