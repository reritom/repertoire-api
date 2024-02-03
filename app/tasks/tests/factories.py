from factory import (
    Sequence,
    SubFactory,
    alchemy,
)

from app.accounts.tests.factories import UserFactory
from app.database import Session
from app.tasks.models.category import Category
from app.tasks.models.task import Task
from app.tasks.models.task_event import TaskEvent, TaskEventAround
from app.tasks.models.task_frequency import (
    FrequencyPeriod,
    FrequencyType,
    TaskFrequency,
)
from app.tasks.models.task_until import TaskUntil, UntilType


class TaskFactory(alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Task
        sqlalchemy_session = Session
        sqlalchemy_session_persistence = "flush"

    name = Sequence(lambda n: "Task{}".format(n))
    description = Sequence(lambda n: "I am a task description{}".format(n))
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


class CategoryFactory(alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Category
        sqlalchemy_session = Session
        sqlalchemy_session_persistence = "flush"

    user = SubFactory(UserFactory)
    name = Sequence(lambda n: "Category{}".format(n))
    description = Sequence(lambda n: "I am a category description{}".format(n))
