from enum import Enum
from typing import Self

from schemes.domain.schemes.observations import ObservationType


class ObservationTypeModel(str, Enum):
    PLANNED = "planned"
    ACTUAL = "actual"

    @classmethod
    def from_domain(cls, type_: ObservationType) -> Self:
        return cls[type_.name]

    def to_domain(self) -> ObservationType:
        return ObservationType[self.name]
