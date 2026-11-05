from datetime import date
from enum import Enum, auto
from typing import Self

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
        milestone: Milestone,
        observation_type: ObservationType,
        status_date: date,
        source: DataSource,
    ):
        self._id = id_
        self._milestone = milestone
        self._observation_type = observation_type
        self._status_date = status_date
        self._source = source

    @property
    def id(self) -> int | None:
        return self._id

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


class SchemeMilestones:
    def __init__(self) -> None:
        self._milestone_revisions: list[MilestoneRevision] = []

    @property
    def milestones_eligible_for_authority_update(self) -> set[Milestone]:
        return {
            Milestone.FEASIBILITY_DESIGN_COMPLETED,
            Milestone.PRELIMINARY_DESIGN_COMPLETED,
            Milestone.DETAILED_DESIGN_COMPLETED,
            Milestone.CONSTRUCTION_STARTED,
            Milestone.CONSTRUCTION_COMPLETED,
        }

    @property
    def milestone_revisions(self) -> list[MilestoneRevision]:
        return list(self._milestone_revisions)

    def update_milestone(self, milestone_revision: MilestoneRevision) -> None:
        self._ensure_no_milestone_revision(milestone_revision.milestone, milestone_revision.observation_type)

        self._milestone_revisions.append(milestone_revision)

    def update_milestone_date(self, milestone: Milestone, observation_type: ObservationType, status_date: date) -> None:
        milestone_revision = self._milestone_revision(milestone, observation_type)
        if milestone_revision:
            self._milestone_revisions.remove(milestone_revision)

        self.update_milestone(
            MilestoneRevision(
                id_=None,
                milestone=milestone,
                observation_type=observation_type,
                status_date=status_date,
                source=DataSource.AUTHORITY_UPDATE,
            )
        )

    def _ensure_no_milestone_revision(self, milestone: Milestone, observation_type: ObservationType) -> None:
        milestone_revision = self._milestone_revision(milestone, observation_type)
        if milestone_revision:
            raise ValueError(f"Milestone already exists: {milestone_revision}")

    def _milestone_revision(self, milestone: Milestone, observation_type: ObservationType) -> MilestoneRevision | None:
        return next(
            (
                revision
                for revision in self.milestone_revisions
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
            for revision in self.milestone_revisions
            if revision.observation_type == ObservationType.ACTUAL
        ]
        return max(actual_milestones, key=lambda milestone: milestone.milestone_order) if actual_milestones else None

    def get_status_date(self, milestone: Milestone, observation_type: ObservationType) -> date | None:
        milestone_revision = self._milestone_revision(milestone, observation_type)
        return milestone_revision.status_date if milestone_revision else None
