from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from .task import Task
    from .task_event_metric import TaskEventMetric


class TaskMetric(Base):
    __tablename__ = "task_metrics"
    __table_args__ = (
        UniqueConstraint("task_id", "name", name="unique_task_metric_name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), nullable=False)
    task: Mapped[Task] = relationship(back_populates="metrics")

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    prompt: Mapped[str] = mapped_column(String(100), nullable=False)
    required: Mapped[bool] = mapped_column(Boolean, nullable=False)

    metrics: Mapped[List[TaskEventMetric]] = relationship(
        "TaskEventMetric",
        back_populates="task_metric",
        cascade="delete,all",
    )
