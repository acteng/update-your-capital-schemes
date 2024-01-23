from schemes.dicts import inverse_dict
from schemes.domain.schemes import ObservationType


class ObservationTypeMapper:
    _IDS = {
        ObservationType.PLANNED: 1,
        ObservationType.ACTUAL: 2,
    }

    def to_id(self, observation_type: ObservationType) -> int:
        return self._IDS[observation_type]

    def to_domain(self, id_: int) -> ObservationType:
        return inverse_dict(self._IDS)[id_]
