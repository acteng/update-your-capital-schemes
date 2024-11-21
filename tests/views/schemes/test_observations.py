import pytest

from schemes.domain.schemes import ObservationType
from schemes.views.schemes.observations import ObservationTypeRepr


@pytest.mark.parametrize(
    "observation_type, observation_type_repr",
    [
        (ObservationType.PLANNED, "planned"),
        (ObservationType.ACTUAL, "actual"),
    ],
)
class TestObservationTypeRepr:
    def test_from_domain(self, observation_type: ObservationType, observation_type_repr: str) -> None:
        assert ObservationTypeRepr.from_domain(observation_type).value == observation_type_repr

    def test_to_domain(self, observation_type: ObservationType, observation_type_repr: str) -> None:
        assert ObservationTypeRepr(observation_type_repr).to_domain() == observation_type
