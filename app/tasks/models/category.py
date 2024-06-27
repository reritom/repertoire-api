from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.accounts.models.user import User

    from .task import Task


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

    tasks: Mapped[List[Task]] = relationship(back_populates="category")

    parent_category_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("categories.id"), nullable=True
    )
