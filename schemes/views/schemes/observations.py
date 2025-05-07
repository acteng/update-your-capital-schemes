from __future__ import annotations

from enum import Enum, unique

from schemes.dicts import inverse_dict
from schemes.domain.schemes import ObservationType


@unique
class ObservationTypeRepr(str, Enum):
    PLANNED = "planned"
    ACTUAL = "actual"

    @classmethod
    def from_domain(cls, observation_type: ObservationType) -> ObservationTypeRepr:
        return cls._members()[observation_type]

    def to_domain(self) -> ObservationType:
        return inverse_dict(self._members())[self]

    @staticmethod
    def _members() -> dict[ObservationType, ObservationTypeRepr]:
        return {
            ObservationType.PLANNED: ObservationTypeRepr.PLANNED,
            ObservationType.ACTUAL: ObservationTypeRepr.ACTUAL,
        }
