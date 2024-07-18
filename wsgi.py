from app import create_app
from app.celery import celery

app = create_app()

__all__ = ["app", "celery"]
