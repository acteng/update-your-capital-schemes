from __future__ import annotations

from enum import Enum, auto


class Scheme:
    def __init__(self, id_: int, name: str, authority_id: int):
        self.id = id_
        self.name = name
        self.authority_id = authority_id
        self.type: SchemeType | None = None
        self.funding_programme: FundingProgramme | None = None

    @property
    def reference(self) -> str:
        return f"ATE{self.id:05}"


class SchemeType(Enum):
    DEVELOPMENT = auto()
    CONSTRUCTION = auto()


class FundingProgramme(Enum):
    ATF2 = auto()
    ATF3 = auto()
    ATF4 = auto()
    ATF4E = auto()
    ATF5 = auto()
    MRN = auto()
    LUF = auto()
    CRSTS = auto()
