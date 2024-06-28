from __future__ import annotations

from typing import TYPE_CHECKING, List

from ._service import _create_category, _delete_category, _get_categories, _get_category

if TYPE_CHECKING:
    from app.accounts.models.user import User
    from app.database import SessionType
    from app.tasks.models.category import Category
    from app.tasks.schemas.category_schema import CategoryCreationSchema


def create_category(
    session: SessionType,
    authenticated_user: User,
    category_creation_payload: CategoryCreationSchema,
) -> Category:
    return _create_category(
        session=session,
        authenticated_user=authenticated_user,
        category_creation_payload=category_creation_payload,
    )


def delete_category(
    session: SessionType,
    authenticated_user: User,
    category_id: int,
) -> None:
    return _delete_category(
        session=session,
        authenticated_user=authenticated_user,
        category_id=category_id,
    )


def get_category(
    session: SessionType,
    authenticated_user: User,
    category_id: int,
) -> Category:
    return _get_category(
        session=session,
        authenticated_user=authenticated_user,
        category_id=category_id,
    )


def get_categories(
    session: SessionType,
    authenticated_user: User,
) -> List[Category]:
    return _get_categories(
        session=session,
        authenticated_user=authenticated_user,
    )
