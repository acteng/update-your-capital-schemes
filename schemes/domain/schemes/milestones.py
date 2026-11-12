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


class SchemeMilestone:
    def __init__(
        self,
        surrogate_id: int | None,
        milestone: Milestone,
        observation_type: ObservationType,
        status_date: date,
        source: DataSource,
    ):
        self._surrogate_id = surrogate_id
        self._milestone = milestone
        self._observation_type = observation_type
        self._status_date = status_date
        self._source = source

    @property
    def surrogate_id(self) -> int | None:
        return self._surrogate_id

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
        self._milestones: list[SchemeMilestone] = []

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
    def milestones(self) -> list[SchemeMilestone]:
        return list(self._milestones)

    def update_milestone(self, milestone: SchemeMilestone) -> None:
        self._ensure_no_milestone(milestone.milestone, milestone.observation_type)

        self._milestones.append(milestone)

    def update_milestone_date(self, milestone: Milestone, observation_type: ObservationType, status_date: date) -> None:
        scheme_milestone = self._milestone(milestone, observation_type)
        if scheme_milestone:
            self._milestones.remove(scheme_milestone)

        self.update_milestone(
            SchemeMilestone(
                surrogate_id=None,
                milestone=milestone,
                observation_type=observation_type,
                status_date=status_date,
                source=DataSource.AUTHORITY_UPDATE,
            )
        )

    def _ensure_no_milestone(self, milestone: Milestone, observation_type: ObservationType) -> None:
        scheme_milestone = self._milestone(milestone, observation_type)
        if scheme_milestone:
            raise ValueError(f"Milestone already exists: {scheme_milestone}")

    def _milestone(self, milestone: Milestone, observation_type: ObservationType) -> SchemeMilestone | None:
        return next(
            (
                scheme_milestone
                for scheme_milestone in self.milestones
                if scheme_milestone.milestone == milestone and scheme_milestone.observation_type == observation_type
            ),
            None,
        )

    def update_milestones(self, *milestones: SchemeMilestone) -> None:
        for milestone in milestones:
            self.update_milestone(milestone)

    @property
    def current_milestone(self) -> Milestone | None:
        actual_milestones = [
            milestone.milestone for milestone in self.milestones if milestone.observation_type == ObservationType.ACTUAL
        ]
        return max(actual_milestones, key=lambda milestone: milestone.milestone_order) if actual_milestones else None

    def get_status_date(self, milestone: Milestone, observation_type: ObservationType) -> date | None:
        scheme_milestone = self._milestone(milestone, observation_type)
        return scheme_milestone.status_date if scheme_milestone else None
