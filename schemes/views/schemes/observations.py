from __future__ import annotations

from enum import Enum, unique

from schemes.domain.schemes import ObservationType


@unique
class ObservationTypeRepr(Enum):
    PLANNED = "Planned"
    ACTUAL = "Actual"

    def to_domain(self) -> ObservationType:
        members = {
            ObservationTypeRepr.PLANNED: ObservationType.PLANNED,
            ObservationTypeRepr.ACTUAL: ObservationType.ACTUAL,
        }
        return members[self]
