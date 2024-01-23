from schemes.dicts import inverse_dict
from schemes.domain.schemes import Milestone


class MilestoneMapper:
    _IDS = {
        Milestone.PUBLIC_CONSULTATION_COMPLETED: 1,
        Milestone.FEASIBILITY_DESIGN_STARTED: 2,
        Milestone.FEASIBILITY_DESIGN_COMPLETED: 3,
        Milestone.PRELIMINARY_DESIGN_COMPLETED: 4,
        Milestone.OUTLINE_DESIGN_COMPLETED: 5,
        Milestone.DETAILED_DESIGN_COMPLETED: 6,
        Milestone.CONSTRUCTION_STARTED: 7,
        Milestone.CONSTRUCTION_COMPLETED: 8,
        Milestone.INSPECTION: 9,
        Milestone.NOT_PROGRESSED: 10,
        Milestone.SUPERSEDED: 11,
        Milestone.REMOVED: 12,
    }

    def to_id(self, milestone: Milestone) -> int:
        return self._IDS[milestone]

    def to_domain(self, id_: int) -> Milestone:
        return inverse_dict(self._IDS)[id_]
