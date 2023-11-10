from __future__ import annotations

from enum import Enum, auto


class Scheme:
    def __init__(self, id_: int, name: str, authority_id: int):
        self.id = id_
        self.name = name
        self.authority_id = authority_id
        self.type: SchemeType | None = None

    @property
    def reference(self) -> str:
        return f"ATE{self.id:05}"


class SchemeType(Enum):
    DEVELOPMENT = auto()
    CONSTRUCTION = auto()
