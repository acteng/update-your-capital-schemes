from datetime import date, datetime
from enum import Enum
from typing import Self

from schemes.domain.dates import DateRange
from schemes.domain.schemes.milestones import Milestone, MilestoneRevision
from schemes.infrastructure.api.base import BaseModel
from schemes.infrastructure.api.data_sources import DataSourceModel
from schemes.infrastructure.api.observation_types import ObservationTypeModel


class MilestoneModel(str, Enum):
    PUBLIC_CONSULTATION_COMPLETED = "public consultation completed"
    FEASIBILITY_DESIGN_STARTED = "feasibility design started"
    FEASIBILITY_DESIGN_COMPLETED = "feasibility design completed"
    PRELIMINARY_DESIGN_COMPLETED = "preliminary design completed"
    OUTLINE_DESIGN_COMPLETED = "outline design completed"
    DETAILED_DESIGN_COMPLETED = "detailed design completed"
    CONSTRUCTION_STARTED = "construction started"
    CONSTRUCTION_COMPLETED = "construction completed"
    FUNDING_COMPLETED = "funding completed"
    NOT_PROGRESSED = "not progressed"
    SUPERSEDED = "superseded"
    REMOVED = "removed"

    @classmethod
    def from_domain(cls, milestone: Milestone) -> Self:
        return cls[milestone.name]

    def to_domain(self) -> Milestone:
        return Milestone[self.name]


class CapitalSchemeMilestoneModel(BaseModel):
    milestone: MilestoneModel
    observation_type: ObservationTypeModel
    status_date: date
    source: DataSourceModel

    @classmethod
    def from_domain(cls, milestone_revision: MilestoneRevision) -> Self:
        return cls(
            milestone=MilestoneModel.from_domain(milestone_revision.milestone),
            observation_type=ObservationTypeModel.from_domain(milestone_revision.observation_type),
            status_date=milestone_revision.status_date,
            source=DataSourceModel.from_domain(milestone_revision.source),
        )

    def to_domain(self) -> MilestoneRevision:
        # TODO: id, effective
        return MilestoneRevision(
            id_=0,
            effective=DateRange(date_from=datetime.min, date_to=None),
            milestone=self.milestone.to_domain(),
            observation_type=self.observation_type.to_domain(),
            status_date=self.status_date,
            source=self.source.to_domain(),
        )
