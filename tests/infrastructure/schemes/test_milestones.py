import pytest

from schemes.domain.schemes import Milestone
from schemes.infrastructure.schemes.milestones import MilestoneMapper


class TestMilestoneMapper:
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
    def test_mapper(self, milestone: Milestone, id_: int) -> None:
        mapper = MilestoneMapper()
        assert mapper.to_id(milestone) == id_ and mapper.to_domain(id_) == milestone
