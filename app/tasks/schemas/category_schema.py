from typing import Optional

from pydantic import BaseModel, Field

from app.tasks.models.category import Category, IconNameEnum


class CategoryCreationSchema(BaseModel):
    icon_name: IconNameEnum
    name: str = Field(max_length=Category.name.type.length)
    description: str = Field(max_length=Category.description.type.length)
    icon_hex_colour: str = Field(max_length=6, min_length=6)
    parent_category_id: Optional[int] = None


class CategorySchema(CategoryCreationSchema):
    id: int
