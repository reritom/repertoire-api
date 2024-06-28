from enum import Enum
from typing import Literal, TypeVar, Union


class Sentinels(Enum):
    NO_OP = "No action performed"
    NO_FILTER = "No filter applied"


NO_OP = Sentinels.NO_OP
NO_FILTER = Sentinels.NO_FILTER


T = TypeVar("T")
OptionalFilter = Union[Literal[Sentinels.NO_FILTER], T]
OptionalAction = Union[Literal[Sentinels.NO_OP], T]
