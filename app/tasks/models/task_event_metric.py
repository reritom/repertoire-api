from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.tasks.models.task_event import TaskEvent
    from app.tasks.models.task_metric import TaskMetric


class TaskEventMetric(Base):
    __tablename__ = "task_event_metrics"
    __table_args__ = (
        UniqueConstraint(
            "task_metric_id", "task_event_id", name="unique_tast_event_metric"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    task_metric_id: Mapped[int] = mapped_column(
        ForeignKey("task_metrics.id"), nullable=False
    )
    task_metric: Mapped[TaskMetric] = relationship(back_populates="metrics")

    task_event_id: Mapped[int] = mapped_column(
        ForeignKey("task_events.id"), nullable=False
    )
    task_event: Mapped[TaskEvent] = relationship(back_populates="metrics")

    value: Mapped[int] = mapped_column(Integer, nullable=False)
