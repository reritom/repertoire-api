from fastapi.routing import APIRouter

from .category_router import router as category_router

router = APIRouter()
router.include_router(category_router)
