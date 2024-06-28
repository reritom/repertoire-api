from typing import Optional

from app.shared.dao import BaseDao
from app.shared.sentinels import NO_FILTER, OptionalFilter
from app.tasks.models.category import Category, IconNameEnum


class CategoryDao(BaseDao[Category]):
    class Meta:
        model = Category

    def create(
        self,
        user_id: int,
        name: str,
        description: str,
        icon_name: IconNameEnum,
        icon_hex_colour: str,
        parent_category_id: Optional[int] = None,
    ) -> Category:
        category = Category(
            user_id=user_id,
            name=name,
            description=description,
            icon_name=icon_name,
            icon_hex_colour=icon_hex_colour,
            parent_category_id=parent_category_id,
        )

        with self.session.begin_nested():
            self.session.add(category)

        self.session.flush()
        return category

    def query(
        self,
        id: OptionalFilter[int] = NO_FILTER,
        user_id: OptionalFilter[int] = NO_FILTER,
        name: OptionalFilter[int] = NO_FILTER,
    ):
        statement = super().query()

        if id is not NO_FILTER:
            statement = statement.where(Category.id == id)

        if user_id is not NO_FILTER:
            statement = statement.where(Category.user_id == user_id)

        if name is not NO_FILTER:
            statement = statement.where(Category.name == name)

        return statement

    def delete(self, id: int, user_id: int):
        category = self.get(id=id, user_id=user_id)
        self.session.delete(category)
        self.session.flush()
