from enum import Enum

from schemes.domain.schemes.observations import ObservationType


class ObservationTypeModel(str, Enum):
    PLANNED = "planned"
    ACTUAL = "actual"

    def to_domain(self) -> ObservationType:
        return ObservationType[self.name]
