from fastapi.routing import APIRouter

from .login_router import router as login_router

router = APIRouter()

router.include_router(login_router)
