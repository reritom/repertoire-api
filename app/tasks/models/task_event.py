from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import DateTime, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from .task import Task
    from .task_event_metric import TaskEventMetric


class TaskEventAround(enum.Enum):
    today = "today"
    yesterday = "yesterday"
    specifically = "specifically"


class TaskEvent(Base):
    __tablename__ = "task_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    created: Mapped[datetime] = mapped_column(insert_default=datetime.utcnow)

    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), nullable=False)
    task: Mapped[Task] = relationship(back_populates="events")

    around: Mapped[TaskEventAround] = mapped_column(
        Enum(TaskEventAround), nullable=False
    )
    at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    metrics: Mapped[List[TaskEventMetric]] = relationship(
        "TaskEventMetric",
        back_populates="task_event",
        cascade="delete,all",
    )
