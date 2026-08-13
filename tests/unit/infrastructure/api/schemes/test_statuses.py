import pytest

from schemes.domain.schemes.schemes import Status
from schemes.infrastructure.api.schemes.statuses import StatusModel


class TestStatusModel:
    @pytest.mark.parametrize(
        "status_model, expected_status",
        [
            (StatusModel.PIPELINE, Status.PIPELINE),
            (StatusModel.ACTIVE, Status.ACTIVE),
            (StatusModel.PAUSED, Status.PAUSED),
            (StatusModel.CONCLUDED, Status.CONCLUDED),
            (StatusModel.DELETED, Status.DELETED),
        ],
    )
    def test_to_domain(self, status_model: StatusModel, expected_status: Status) -> None:
        assert status_model.to_domain() == expected_status
