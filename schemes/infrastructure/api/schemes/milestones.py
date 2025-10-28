from datetime import date, datetime
from enum import Enum

from schemes.domain.dates import DateRange
from schemes.domain.schemes.data_sources import DataSource
from schemes.domain.schemes.milestones import Milestone, MilestoneRevision
from schemes.infrastructure.api.base import BaseModel
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

    def to_domain(self) -> Milestone:
        return Milestone[self.name]


class CapitalSchemeMilestoneModel(BaseModel):
    milestone: MilestoneModel
    observation_type: ObservationTypeModel
    status_date: date

    def to_domain(self) -> MilestoneRevision:
        # TODO: id, effective, source
        return MilestoneRevision(
            id_=0,
            effective=DateRange(date_from=datetime.min, date_to=None),
            milestone=self.milestone.to_domain(),
            observation_type=self.observation_type.to_domain(),
            status_date=self.status_date,
            source=DataSource.PULSE_5,
        )
