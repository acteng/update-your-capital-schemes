import pytest

from schemes.domain.schemes.observations import ObservationType
from schemes.infrastructure.api.observation_types import ObservationTypeModel


class TestObservationTypeModel:
    @pytest.mark.parametrize(
        "type_model, expected_type",
        [
            (ObservationTypeModel.PLANNED, ObservationType.PLANNED),
            (ObservationTypeModel.ACTUAL, ObservationType.ACTUAL),
        ],
    )
    def test_to_domain(self, type_model: ObservationTypeModel, expected_type: ObservationType) -> None:
        assert type_model.to_domain() == expected_type
