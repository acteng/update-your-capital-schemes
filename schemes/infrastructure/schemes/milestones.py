from schemes.domain.schemes import Milestone


class MilestoneMapper:
    _IDS = {
        Milestone.PUBLIC_CONSULTATION_COMPLETED: 1,
        Milestone.FEASIBILITY_DESIGN_COMPLETED: 2,
        Milestone.PRELIMINARY_DESIGN_COMPLETED: 3,
        Milestone.OUTLINE_DESIGN_COMPLETED: 4,
        Milestone.DETAILED_DESIGN_COMPLETED: 5,
        Milestone.CONSTRUCTION_STARTED: 6,
        Milestone.CONSTRUCTION_COMPLETED: 7,
        Milestone.INSPECTION: 8,
        Milestone.NOT_PROGRESSED: 9,
        Milestone.SUPERSEDED: 10,
        Milestone.REMOVED: 11,
    }

    def to_id(self, milestone: Milestone) -> int:
        return self._IDS[milestone]

    def to_domain(self, id_: int) -> Milestone:
        return next(key for key, value in self._IDS.items() if value == id_)
