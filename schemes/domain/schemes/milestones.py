from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum, IntEnum, auto

from schemes.domain.schemes.dates import DateRange


class SchemeMilestones:
    def __init__(self) -> None:
        self._milestone_revisions: list[MilestoneRevision] = []

    @property
    def milestone_revisions(self) -> list[MilestoneRevision]:
        return list(self._milestone_revisions)

    @property
    def current_milestone_revisions(self) -> list[MilestoneRevision]:
        return [revision for revision in self._milestone_revisions if revision.effective.date_to is None]

    def update_milestone(self, milestone_revision: MilestoneRevision) -> None:
        if milestone_revision.effective.date_to is None:
            self._ensure_no_current_milestone_revision(
                milestone_revision.milestone, milestone_revision.observation_type
            )

        self._milestone_revisions.append(milestone_revision)

    def _ensure_no_current_milestone_revision(self, milestone: Milestone, observation_type: ObservationType) -> None:
        current_milestone_revision = next(
            (
                revision
                for revision in self.current_milestone_revisions
                if revision.milestone == milestone and revision.observation_type == observation_type
            ),
            None,
        )
        if current_milestone_revision:
            raise ValueError(f"Current milestone already exists: {current_milestone_revision}")

    def update_milestones(self, *milestone_revisions: MilestoneRevision) -> None:
        for milestone_revision in milestone_revisions:
            self.update_milestone(milestone_revision)

    @property
    def current_milestone(self) -> Milestone | None:
        actual_milestones = [
            revision.milestone
            for revision in self.current_milestone_revisions
            if revision.observation_type == ObservationType.ACTUAL
        ]
        return sorted(actual_milestones)[-1] if actual_milestones else None


@dataclass(frozen=True)
class MilestoneRevision:
    effective: DateRange
    milestone: Milestone
    observation_type: ObservationType
    status_date: date


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
