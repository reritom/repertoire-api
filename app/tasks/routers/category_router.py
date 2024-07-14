from typing import List

from fastapi import APIRouter, Depends, Path

from app.accounts.models.user import User
from app.auth.routers.dependencies import (
    authenticated_user_required,
    get_authenticated_user,
)
from app.database import SessionType, get_session
from app.tasks.models.category import Category
from app.tasks.schemas.category_schema import CategoryCreationSchema, CategorySchema
from app.tasks.services.category_service import service as category_service

router = APIRouter(dependencies=[Depends(authenticated_user_required)])


@router.post(
    "/categories",
    response_model=CategorySchema,
    status_code=201,
)
def create_category(
    payload: CategoryCreationSchema,
    authenticated_user: User = Depends(get_authenticated_user),
    session: SessionType = Depends(get_session),
) -> Category:
    return category_service.create_category(
        session=session,
        authenticated_user=authenticated_user,
        category_creation_payload=payload,
    )


@router.get(
    "/categories",
    response_model=List[CategorySchema],
    status_code=200,
)
def get_categories(
    authenticated_user: User = Depends(get_authenticated_user),
    session: SessionType = Depends(get_session),
) -> List[Category]:
    return category_service.get_categories(
        session=session,
        authenticated_user=authenticated_user,
    )


@router.get(
    "/categories/{category_id}",
    response_model=CategorySchema,
    status_code=200,
)
def get_category(
    category_id: int = Path(),
    authenticated_user: User = Depends(get_authenticated_user),
    session: SessionType = Depends(get_session),
) -> Category:
    return category_service.get_category(
        session=session,
        authenticated_user=authenticated_user,
        category_id=category_id,
    )


@router.delete(
    "/categories/{category_id}",
    response_model=None,
    status_code=204,
)
def delete_category(
    category_id: int = Path(),
    authenticated_user: User = Depends(get_authenticated_user),
    session: SessionType = Depends(get_session),
) -> None:
    return category_service.delete_category(
        session=session,
        authenticated_user=authenticated_user,
        category_id=category_id,
    )
