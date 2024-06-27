from factory import (
    SelfAttribute,
    Sequence,
    SubFactory,
    alchemy,
)

from app.accounts.tests.factories import UserFactory
from app.database import Session
from app.tasks.models.category import Category
from app.tasks.models.task import Task
from app.tasks.models.task_event import TaskEvent, TaskEventAround
from app.tasks.models.task_event_metric import TaskEventMetric
from app.tasks.models.task_frequency import (
    FrequencyPeriod,
    FrequencyType,
    TaskFrequency,
)
from app.tasks.models.task_metric import TaskMetric
from app.tasks.models.task_until import TaskUntil, UntilType


class TaskFactory(alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Task
        sqlalchemy_session = Session
        sqlalchemy_session_persistence = "flush"

    name = Sequence(lambda n: f"Task {n}")
    description = Sequence(lambda n: f"I am a task description {n}")
    user = SubFactory(UserFactory)
    frequency = SubFactory("app.tasks.tests.factories.TaskFrequencyFactory")
    until = SubFactory("app.tasks.tests.factories.TaskUntilFactory")


class TaskFrequencyFactory(alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = TaskFrequency
        sqlalchemy_session = Session
        sqlalchemy_session_persistence = "flush"

    type = FrequencyType.per
    period = FrequencyPeriod.week
    amount = 1


class TaskUntilFactory(alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = TaskUntil
        sqlalchemy_session = Session
        sqlalchemy_session_persistence = "flush"

    type = UntilType.amount
    amount = 10


class TaskEventFactory(alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = TaskEvent
        sqlalchemy_session = Session
        sqlalchemy_session_persistence = "flush"

    task = SubFactory(TaskFactory)
    around = TaskEventAround.today


class TaskMetricFactory(alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = TaskMetric
        sqlalchemy_session = Session
        sqlalchemy_session_persistence = "flush"

    task = SubFactory(TaskFactory)
    name = Sequence(lambda n: f"Metric {n}")
    prompt = Sequence(lambda n: f"Enter value for metric {n}")
    required = False


class TaskEventMetricFactory(alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = TaskEventMetric
        sqlalchemy_session = Session
        sqlalchemy_session_persistence = "flush"
        exclude = ("task",)

    task = SubFactory(TaskFactory)
    task_metric = SubFactory(TaskMetricFactory, task=SelfAttribute("..task"))
    task_event = SubFactory(TaskEventFactory, task=SelfAttribute("..task"))
    value = Sequence(lambda n: n)


class CategoryFactory(alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Category
        sqlalchemy_session = Session
        sqlalchemy_session_persistence = "flush"

    user = SubFactory(UserFactory)
    name = Sequence(lambda n: f"Category {n}")
    description = Sequence(lambda n: f"I am a category description {n}")
