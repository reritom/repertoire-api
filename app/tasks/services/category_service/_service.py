from __future__ import annotations

from typing import List

from fast_depends import Depends, inject

from app.accounts.models.user import User
from app.database import SessionType
from app.tasks.daos.category_dao import CategoryDao
from app.tasks.models.category import Category
from app.tasks.schemas.category_schema import CategoryCreationSchema
from app.tasks.services._dependencies import get_category_dao
from app.tasks.services.category_service._dependencies import (
    validate_category_name_is_unique,
    validate_optional_parent_category_id_is_valid,
)


@inject(
    extra_dependencies=[
        Depends(validate_optional_parent_category_id_is_valid),
        Depends(validate_category_name_is_unique),
    ]
)
def _create_category(
    authenticated_user: User = Depends,
    category_creation_payload: CategoryCreationSchema = Depends,
    session: SessionType = Depends,
    # Injected
    category_dao: CategoryDao = Depends(get_category_dao),
) -> Category:
    category = category_dao.create(
        user_id=authenticated_user.id,
        name=category_creation_payload.name,
        description=category_creation_payload.description,
        icon_name=category_creation_payload.icon_name,
        icon_hex_colour=category_creation_payload.icon_hex_colour,
        parent_category_id=category_creation_payload.parent_category_id,
    )
    session.commit()
    return category


@inject
def _delete_category(
    authenticated_user: User = Depends,
    category_id: int = Depends,
    session: SessionType = Depends,
    # Injected
    category_dao: CategoryDao = Depends(get_category_dao),
) -> None:
    """A sqlalchemy.exc.NoResultFound will be raised if the category is not found"""
    category_dao.delete(user_id=authenticated_user.id, id=category_id)
    session.commit()


@inject
def _get_category(
    authenticated_user: User = Depends,
    category_id: int = Depends,
    # Injected
    category_dao: CategoryDao = Depends(get_category_dao),
) -> Category:
    """A sqlalchemy.exc.NoResultFound will be raised if the category is not found"""
    return category_dao.get(user_id=authenticated_user.id, id=category_id)


@inject
def _get_categories(
    authenticated_user: User = Depends,
    # Injected
    category_dao: CategoryDao = Depends(get_category_dao),
) -> List[Category]:
    return category_dao.list(user_id=authenticated_user.id)
