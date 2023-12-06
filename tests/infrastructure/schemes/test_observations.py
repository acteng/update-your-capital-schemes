import pytest

from schemes.domain.schemes import ObservationType
from schemes.infrastructure.schemes.observations import ObservationTypeMapper


class TestObservationTypeMapper:
    @pytest.mark.parametrize("observation_type, id_", [(ObservationType.PLANNED, 1), (ObservationType.ACTUAL, 2)])
    def test_mapper(self, observation_type: ObservationType, id_: int) -> None:
        mapper = ObservationTypeMapper()
        assert mapper.to_id(observation_type) == id_ and mapper.to_domain(id_) == observation_type
