import pytest

from schemes.domain.schemes import Milestone
from schemes.infrastructure.schemes.milestones import MilestoneMapper


@pytest.mark.parametrize(
    "milestone, id_",
    [
        (Milestone.PUBLIC_CONSULTATION_COMPLETED, 1),
        (Milestone.FEASIBILITY_DESIGN_STARTED, 2),
        (Milestone.FEASIBILITY_DESIGN_COMPLETED, 3),
        (Milestone.PRELIMINARY_DESIGN_COMPLETED, 4),
        (Milestone.OUTLINE_DESIGN_COMPLETED, 5),
        (Milestone.DETAILED_DESIGN_COMPLETED, 6),
        (Milestone.CONSTRUCTION_STARTED, 7),
        (Milestone.CONSTRUCTION_COMPLETED, 8),
        (Milestone.INSPECTION, 9),
        (Milestone.NOT_PROGRESSED, 10),
        (Milestone.SUPERSEDED, 11),
        (Milestone.REMOVED, 12),
    ],
)
class TestMilestoneMapper:
    def test_to_id(self, milestone: Milestone, id_: int) -> None:
        assert MilestoneMapper().to_id(milestone) == id_

    def test_to_domain(self, milestone: Milestone, id_: int) -> None:
        assert MilestoneMapper().to_domain(id_) == milestone
