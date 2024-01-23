from dataclasses import fields
from typing import Any, TypeVar

K = TypeVar("K")
V = TypeVar("V")


def inverse_dict(d: dict[K, V]) -> dict[V, K]:
    return {value: key for key, value in d.items()}


def as_shallow_dict(obj: Any) -> dict[str, Any]:
    return dict((field_.name, getattr(obj, field_.name)) for field_ in fields(obj))
