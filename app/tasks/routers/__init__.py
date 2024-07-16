from fastapi.routing import APIRouter

from .category_router import router as category_router
from .task_event_metric_router import router as task_event_metric_router
from .task_event_router import router as task_event_router
from .task_metric_router import router as task_metric_router
from .task_router import router as task_router

router = APIRouter()
router.include_router(category_router)
router.include_router(task_router)
router.include_router(task_event_router)
router.include_router(task_metric_router)
router.include_router(task_event_metric_router)
