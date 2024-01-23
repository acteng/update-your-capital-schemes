from typing import TypeVar

K = TypeVar("K")
V = TypeVar("V")


def inverse_dict(d: dict[K, V]) -> dict[V, K]:
    return {value: key for key, value in d.items()}
