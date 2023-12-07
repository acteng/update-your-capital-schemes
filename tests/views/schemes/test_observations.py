import pytest

from schemes.domain.schemes import ObservationType
from schemes.views.schemes.observations import ObservationTypeRepr


class TestObservationTypeRepr:
    @pytest.mark.parametrize(
        "observation_type, expected_observation_type",
        [
            ("Planned", ObservationType.PLANNED),
            ("Actual", ObservationType.ACTUAL),
        ],
    )
    def test_to_domain(self, observation_type: str, expected_observation_type: ObservationType) -> None:
        assert ObservationTypeRepr(observation_type).to_domain() == expected_observation_type
