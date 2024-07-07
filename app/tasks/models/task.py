from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.tasks.models.task_frequency import FrequencyType

if TYPE_CHECKING:
    from app.accounts.models.user import User
    from app.tasks.models.task_metric import TaskMetric

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
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="unique_user_task_name"),
    )

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
    next_event_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    frequency_id: Mapped[int] = mapped_column(
        ForeignKey("task_frequencies.id"),
        nullable=False,
        unique=True,
    )
    frequency: Mapped[TaskFrequency] = relationship(
        foreign_keys=frequency_id,
        lazy="joined",
        cascade="delete,all",
    )

    until_id: Mapped[int] = mapped_column(
        ForeignKey("task_untils.id"),
        nullable=False,
        unique=True,
    )
    until: Mapped[TaskUntil] = relationship(
        foreign_keys=until_id,
        lazy="joined",
        cascade="delete,all",
    )

    events: Mapped[List[TaskEvent]] = relationship(
        back_populates="task",
        cascade="all, delete-orphan",
        order_by="TaskEvent.effective_datetime.desc()",
        lazy="joined",
    )
    metrics: Mapped[List[TaskMetric]] = relationship(
        back_populates="task", cascade="all, delete-orphan"
    )

    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus), default=TaskStatus.ongoing
    )
    manually_completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    @property
    def is_pausable(self) -> bool:
        return (
            self.status == TaskStatus.ongoing
            and self.frequency.type == FrequencyType.per
        )

    @property
    def latest_event(self) -> Optional[TaskEvent]:
        # TODO join this directly as a relationship
        try:
            return self.events[0]
        except IndexError:
            return None

    @property
    def latest_event_datetime(self) -> Optional[datetime]:
        if latest_event := self.latest_event:
            return latest_event.effective_datetime

    @property
    def second_latest_event(self) -> Optional[TaskEvent]:
        # TODO join this directly as a relationship
        try:
            return self.events[1]
        except IndexError:
            return None
