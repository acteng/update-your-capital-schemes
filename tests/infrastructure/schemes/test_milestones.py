import pytest

from schemes.domain.schemes import Milestone
from schemes.infrastructure.schemes.milestones import MilestoneMapper


class TestMilestoneMapper:
    @pytest.mark.parametrize(
        "milestone, id_",
        [
            (Milestone.PUBLIC_CONSULTATION_COMPLETED, 1),
            (Milestone.FEASIBILITY_DESIGN_COMPLETED, 2),
            (Milestone.PRELIMINARY_DESIGN_COMPLETED, 3),
            (Milestone.OUTLINE_DESIGN_COMPLETED, 4),
            (Milestone.DETAILED_DESIGN_COMPLETED, 5),
            (Milestone.CONSTRUCTION_STARTED, 6),
            (Milestone.CONSTRUCTION_COMPLETED, 7),
            (Milestone.INSPECTION, 8),
            (Milestone.NOT_PROGRESSED, 9),
            (Milestone.SUPERSEDED, 10),
            (Milestone.REMOVED, 11),
        ],
    )
    def test_mapper(self, milestone: Milestone, id_: int) -> None:
        mapper = MilestoneMapper()
        assert mapper.to_id(milestone) == id_ and mapper.to_domain(id_) == milestone
