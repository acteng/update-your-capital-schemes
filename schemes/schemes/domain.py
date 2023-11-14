from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum, IntEnum, auto


class Scheme:
    def __init__(self, id_: int, name: str, authority_id: int):
        self.id = id_
        self.name = name
        self.authority_id = authority_id
        self.type: SchemeType | None = None
        self.funding_programme: FundingProgramme | None = None
        self._milestone_revisions: list[MilestoneRevision] = []

    @property
    def reference(self) -> str:
        return f"ATE{self.id:05}"

    @property
    def milestone_revisions(self) -> list[MilestoneRevision]:
        return list(self._milestone_revisions)

    def update_milestone(self, milestone_revision: MilestoneRevision) -> None:
        self._milestone_revisions.append(milestone_revision)

    @property
    def current_milestone(self) -> Milestone | None:
        current_milestone_revisions = [
            revision for revision in self._milestone_revisions if revision.effective_date_to is None
        ]
        actual_milestone_revisions = [
            revision for revision in current_milestone_revisions if revision.observation_type == ObservationType.ACTUAL
        ]
        actual_milestones = [revision.milestone for revision in actual_milestone_revisions]
        return sorted(actual_milestones)[-1] if actual_milestones else None


class SchemeType(Enum):
    DEVELOPMENT = auto()
    CONSTRUCTION = auto()


class FundingProgramme(Enum):
    ATF2 = auto()
    ATF3 = auto()
    ATF4 = auto()
    ATF4E = auto()
    ATF5 = auto()
    MRN = auto()
    LUF = auto()
    CRSTS = auto()


@dataclass(frozen=True)
class MilestoneRevision:
    effective_date_from: date
    effective_date_to: date | None
    milestone: Milestone
    observation_type: ObservationType
    status_date: date

    def __post_init__(self) -> None:
        if not (self.effective_date_to is None or self.effective_date_from <= self.effective_date_to):
            raise ValueError(
                f"Effective date from '{self.effective_date_from}' must not "
                f"be after effective date to '{self.effective_date_to}'"
            )


class Milestone(IntEnum):
    PUBLIC_CONSULTATION_COMPLETED = auto()
    FEASIBILITY_DESIGN_COMPLETED = auto()
    PRELIMINARY_DESIGN_COMPLETED = auto()
    OUTLINE_DESIGN_COMPLETED = auto()
    DETAILED_DESIGN_COMPLETED = auto()
    CONSTRUCTION_STARTED = auto()
    CONSTRUCTION_COMPLETED = auto()
    INSPECTION = auto()
    NOT_PROGRESSED = auto()
    SUPERSEDED = auto()
    REMOVED = auto()


class ObservationType(Enum):
    PLANNED = auto()
    ACTUAL = auto()
