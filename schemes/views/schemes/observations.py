from __future__ import annotations

from enum import Enum, unique

from schemes.domain.schemes import ObservationType


@unique
class ObservationTypeRepr(Enum):
    PLANNED = "Planned"
    ACTUAL = "Actual"

    @classmethod
    def from_domain(cls, observation_type: ObservationType) -> ObservationTypeRepr:
        return cls._members()[observation_type]

    def to_domain(self) -> ObservationType:
        return {value: key for key, value in self._members().items()}[self]

    @staticmethod
    def _members() -> dict[ObservationType, ObservationTypeRepr]:
        return {
            ObservationType.PLANNED: ObservationTypeRepr.PLANNED,
            ObservationType.ACTUAL: ObservationTypeRepr.ACTUAL,
        }
