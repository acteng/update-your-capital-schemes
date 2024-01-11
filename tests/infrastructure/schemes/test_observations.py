import pytest

from schemes.domain.schemes import ObservationType
from schemes.infrastructure.schemes.observations import ObservationTypeMapper


@pytest.mark.parametrize("observation_type, id_", [(ObservationType.PLANNED, 1), (ObservationType.ACTUAL, 2)])
class TestObservationTypeMapper:
    def test_to_id(self, observation_type: ObservationType, id_: int) -> None:
        assert ObservationTypeMapper().to_id(observation_type) == id_

    def test_to_domain(self, observation_type: ObservationType, id_: int) -> None:
        assert ObservationTypeMapper().to_domain(id_) == observation_type
