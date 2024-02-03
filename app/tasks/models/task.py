from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.accounts.models.user import User

    from .category import Category
    from .task_event import TaskEvent
    from .task_frequency import TaskFrequency
    from .task_until import TaskUntil


class TaskStatus(enum.Enum):
    ongoing = "ongoing"
    completed = "completed"
    paused = "paused"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    created: Mapped[datetime] = mapped_column(insert_default=datetime.utcnow)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    user: Mapped[User] = relationship(back_populates="tasks")

    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )
    category: Mapped[Category | None] = relationship(back_populates="tasks")

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(100), nullable=False)

    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus), default=TaskStatus.ongoing
    )

    frequency_id: Mapped[int] = mapped_column(
        ForeignKey("task_untils.id"), nullable=False
    )
    frequency: Mapped[TaskFrequency] = relationship(back_populates="task")

    until_id: Mapped[int] = mapped_column(
        ForeignKey("task_frequencies.id"), nullable=False
    )
    until: Mapped[TaskUntil] = relationship(back_populates="task")

    events: Mapped[List[TaskEvent]] = relationship(
        back_populates="task", cascade="all, delete-orphan"
    )
