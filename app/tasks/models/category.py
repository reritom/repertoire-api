from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.accounts.models.user import User

    from .task import Task


class IconNameEnum(enum.Enum):
    gymnastics = "gymnastics"
    swimming = "swimming"
    circle = "circle"
    circle_outline = "circle_outline"
    square = "square"
    square_outline = "square_outline"
    hexagon = "hexagon"
    hexagon_outline = "hexagon_outline"
    work = "work"
    beach = "beach"
    favourite = "favourite"
    people = "people"


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="unique_user_category_name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    created: Mapped[datetime] = mapped_column(insert_default=datetime.utcnow)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped[User] = relationship(back_populates="categories")

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(100))
    icon_name: Mapped[IconNameEnum] = mapped_column(Enum(IconNameEnum), nullable=False)
    icon_hex_colour: Mapped[str] = mapped_column(String(length=6), nullable=False)

    tasks: Mapped[List[Task]] = relationship(back_populates="category")

    parent_category_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("categories.id"), nullable=True
    )
    parent_category: Mapped[Category] = relationship(
        "Category",
        foreign_keys=parent_category_id,
        back_populates="child_categories",
    )

    child_categories: Mapped[List[Category]] = relationship(
        "Category",
        cascade="delete,all",
    )
