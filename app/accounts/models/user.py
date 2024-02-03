from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.tasks.models.category import Category
    from app.tasks.models.task import Task

    from .user_preference import UserPreference


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    created: Mapped[datetime] = mapped_column(insert_default=datetime.utcnow)

    email: Mapped[str] = mapped_column(String(100))
    password_hash: Mapped[str] = mapped_column(String(260))
    preferences: Mapped[List[UserPreference]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    categories: Mapped[List[Category]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    tasks: Mapped[List[Task]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
