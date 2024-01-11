from schemes.domain.schemes import ObservationType


class ObservationTypeMapper:
    _IDS = {
        ObservationType.PLANNED: 1,
        ObservationType.ACTUAL: 2,
    }

    def to_id(self, observation_type: ObservationType) -> int:
        return self._IDS[observation_type]

    def to_domain(self, id_: int) -> ObservationType:
        return {value: key for key, value in self._IDS.items()}[id_]
