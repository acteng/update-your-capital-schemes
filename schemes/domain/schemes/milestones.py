from __future__ import annotations

from datetime import date, datetime
from enum import IntEnum, auto

from schemes.domain.schemes import DataSource
from schemes.domain.schemes.dates import DateRange
from schemes.domain.schemes.observations import ObservationType


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

    def update_milestone_date(
        self, now: datetime, milestone: Milestone, observation_type: ObservationType, status_date: date
    ) -> None:
        current_milestone_revision = self._current_milestone_revision(milestone, observation_type)
        if current_milestone_revision:
            current_milestone_revision.effective = DateRange(current_milestone_revision.effective.date_from, now)

        self.update_milestone(
            MilestoneRevision(
                id_=None,
                effective=DateRange(now, None),
                milestone=milestone,
                observation_type=observation_type,
                status_date=status_date,
                source=DataSource.AUTHORITY_UPDATE,
            )
        )

    def _ensure_no_current_milestone_revision(self, milestone: Milestone, observation_type: ObservationType) -> None:
        current_milestone_revision = self._current_milestone_revision(milestone, observation_type)
        if current_milestone_revision:
            raise ValueError(f"Current milestone already exists: {current_milestone_revision}")

    def _current_milestone_revision(
        self, milestone: Milestone, observation_type: ObservationType
    ) -> MilestoneRevision | None:
        return next(
            (
                revision
                for revision in self.current_milestone_revisions
                if revision.milestone == milestone and revision.observation_type == observation_type
            ),
            None,
        )

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

    def get_current_status_date(self, milestone: Milestone, observation_type: ObservationType) -> date | None:
        current_milestone_revision = self._current_milestone_revision(milestone, observation_type)
        return current_milestone_revision.status_date if current_milestone_revision else None


class MilestoneRevision:
    # TODO: domain identifier should be mandatory for transient instances
    def __init__(
        self,
        id_: int | None,
        effective: DateRange,
        milestone: Milestone,
        observation_type: ObservationType,
        status_date: date,
        source: DataSource,
    ):
        self.id = id_
        self.effective = effective
        self.milestone = milestone
        self.observation_type = observation_type
        self.status_date = status_date
        self.source = source


class Milestone(IntEnum):
    PUBLIC_CONSULTATION_COMPLETED = auto()
    FEASIBILITY_DESIGN_STARTED = auto()
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
