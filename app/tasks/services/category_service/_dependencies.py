from typing import Optional

from fast_depends import Depends
from sqlalchemy.exc import NoResultFound

from app.accounts.models.user import User
from app.shared.exceptions import ServiceValidationError
from app.tasks.daos.category_dao import CategoryDao
from app.tasks.schemas.category_schema import CategoryCreationSchema
from app.tasks.services._dependencies import get_category_dao


def get_parent_category_id_from_category_creation_schema(
    category_creation_payload: CategoryCreationSchema,
):
    return category_creation_payload.parent_category_id


def validate_optional_parent_category_id_is_valid(
    category_id: Optional[int] = Depends(
        get_parent_category_id_from_category_creation_schema
    ),
    category_dao: CategoryDao = Depends(get_category_dao),
    authenticated_user: User = Depends,
):
    if category_id:
        try:
            category_dao.get(id=category_id, user_id=authenticated_user.id)
        except NoResultFound:
            raise ServiceValidationError("Parent category is invalid")


def get_category_name_from_category_creation_schema(
    category_creation_payload: CategoryCreationSchema,
):
    return category_creation_payload.name


def validate_category_name_is_unique(
    category_name: str = Depends(get_category_name_from_category_creation_schema),
    category_dao: CategoryDao = Depends(get_category_dao),
    authenticated_user: User = Depends,
):
    if category_dao.get(
        name=category_name, user_id=authenticated_user.id, raise_exc=False
    ):
        raise ServiceValidationError("A category already exists with this name")
