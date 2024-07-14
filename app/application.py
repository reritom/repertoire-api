from fastapi import APIRouter, FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError  # noqa
from fastapi.responses import JSONResponse

from app.accounts.models import *  # noqa
from app.auth.routers import router as auth_router
from app.shared.exceptions import ServiceValidationError
from app.tasks.models import *  # noqa


def create_app():
    app = FastAPI(title="Repertoire API")

    api = APIRouter(prefix="/api")
    api.include_router(auth_router)

    app.include_router(api)

    @app.exception_handler(RequestValidationError)
    def request_validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "detail": jsonable_encoder(exc.errors(), exclude={"input", "url"})
            },
        )

    @app.exception_handler(ServiceValidationError)
    async def service_validation_error_handler(
        request: Request, exc: ServiceValidationError
    ):
        return JSONResponse(
            status_code=400,
            content={"message": exc.args[0], "type": "ServiceValidationError"},
        )

    return app
