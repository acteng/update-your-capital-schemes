from datetime import date, datetime
from enum import Enum, auto
from typing import Self

from schemes.domain.dates import DateRange
from schemes.domain.schemes.data_sources import DataSource
from schemes.domain.schemes.observations import ObservationType


class Milestone(Enum):
    PUBLIC_CONSULTATION_COMPLETED = (auto(), 0)
    FEASIBILITY_DESIGN_STARTED = (auto(), 1)
    FEASIBILITY_DESIGN_COMPLETED = (auto(), 2)
    PRELIMINARY_DESIGN_COMPLETED = (auto(), 3)
    OUTLINE_DESIGN_COMPLETED = (auto(), 4)
    DETAILED_DESIGN_COMPLETED = (auto(), 5)
    CONSTRUCTION_STARTED = (auto(), 6)
    CONSTRUCTION_COMPLETED = (auto(), 7)
    FUNDING_COMPLETED = (auto(), 8)
    NOT_PROGRESSED = (auto(), 9)
    SUPERSEDED = (auto(), 10)
    REMOVED = (auto(), 11)

    milestone_order: int

    def __new__(cls, value: int, milestone_order: int) -> Self:
        obj = object.__new__(cls)
        obj._value_ = value
        obj.milestone_order = milestone_order
        return obj


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
        self._id = id_
        self._effective = effective
        self._milestone = milestone
        self._observation_type = observation_type
        self._status_date = status_date
        self._source = source

    @property
    def id(self) -> int | None:
        return self._id

    @property
    def effective(self) -> DateRange:
        return self._effective

    @property
    def milestone(self) -> Milestone:
        return self._milestone

    @property
    def observation_type(self) -> ObservationType:
        return self._observation_type

    @property
    def status_date(self) -> date:
        return self._status_date

    @property
    def source(self) -> DataSource:
        return self._source

    def close(self, effective_date_to: datetime) -> None:
        self._effective = DateRange(self.effective.date_from, effective_date_to)


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
            current_milestone_revision.close(now)

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
        return max(actual_milestones, key=lambda milestone: milestone.milestone_order) if actual_milestones else None

    def get_current_status_date(self, milestone: Milestone, observation_type: ObservationType) -> date | None:
        current_milestone_revision = self._current_milestone_revision(milestone, observation_type)
        return current_milestone_revision.status_date if current_milestone_revision else None
