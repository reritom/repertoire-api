from dataclasses import asdict
from typing import Any

import pydantic
from pydantic import WrapSerializer


def as_dict(dataclass_instance) -> dict:
    """Convert a dataclass to a dictionary, excluding None values"""
    return asdict(
        dataclass_instance,
        dict_factory=lambda x: {k: v for (k, v) in x if v is not None},
    )


def _datetime_serializer(
    value: Any,
    nxt: pydantic.SerializerFunctionWrapHandler,
    info: pydantic.FieldSerializationInfo,
) -> str:
    return value.strftime("%Y-%m-%dT%H:%M:%S")


datetime_serialiser = WrapSerializer(
    _datetime_serializer,
    return_type=str,
    when_used="json-unless-none",
)


def _decimal_serializer(
    value: Any,
    nxt: pydantic.SerializerFunctionWrapHandler,
    info: pydantic.FieldSerializationInfo,
) -> str:
    return f"{value:.2f}"


decimal_serializer = WrapSerializer(
    _decimal_serializer,
    return_type=str,
    when_used="json-unless-none",
)

__all__ = ["as_dict", "datetime_serialiser"]
