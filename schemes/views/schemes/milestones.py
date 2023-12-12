from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum, unique

from schemes.domain.schemes import (
    DateRange,
    Milestone,
    MilestoneRevision,
    ObservationType,
)
from schemes.views.schemes.observations import ObservationTypeRepr


@dataclass(frozen=True)
class SchemeMilestonesContext:
    milestones: list[SchemeMilestoneRowContext]

    @classmethod
    def from_domain(cls, milestone_revisions: list[MilestoneRevision]) -> SchemeMilestonesContext:
        def get_status_date(milestone: Milestone, observation_type: ObservationType) -> date | None:
            revisions = (
                revision.status_date
                for revision in milestone_revisions
                if revision.milestone == milestone and revision.observation_type == observation_type
            )
            return next(revisions, None)

        return cls(
            milestones=[
                SchemeMilestoneRowContext(
                    milestone=MilestoneContext.from_domain(milestone),
                    planned=get_status_date(milestone, ObservationType.PLANNED),
                    actual=get_status_date(milestone, ObservationType.ACTUAL),
                )
                for milestone in [
                    Milestone.FEASIBILITY_DESIGN_COMPLETED,
                    Milestone.PRELIMINARY_DESIGN_COMPLETED,
                    Milestone.DETAILED_DESIGN_COMPLETED,
                    Milestone.CONSTRUCTION_STARTED,
                    Milestone.CONSTRUCTION_COMPLETED,
                ]
            ]
        )


@dataclass(frozen=True)
class SchemeMilestoneRowContext:
    milestone: MilestoneContext
    planned: date | None
    actual: date | None


@dataclass(frozen=True)
class MilestoneContext:
    name: str | None
    _NAMES = {
        Milestone.PUBLIC_CONSULTATION_COMPLETED: "Public consultation completed",
        Milestone.FEASIBILITY_DESIGN_COMPLETED: "Feasibility design completed",
        Milestone.PRELIMINARY_DESIGN_COMPLETED: "Preliminary design completed",
        Milestone.OUTLINE_DESIGN_COMPLETED: "Outline design completed",
        Milestone.DETAILED_DESIGN_COMPLETED: "Detailed design completed",
        Milestone.CONSTRUCTION_STARTED: "Construction started",
        Milestone.CONSTRUCTION_COMPLETED: "Construction completed",
        Milestone.INSPECTION: "Inspection",
        Milestone.NOT_PROGRESSED: "Not progressed",
        Milestone.SUPERSEDED: "Superseded",
        Milestone.REMOVED: "Removed",
    }

    @classmethod
    def from_domain(cls, milestone: Milestone | None) -> MilestoneContext:
        return cls(name=cls._NAMES[milestone] if milestone else None)


@dataclass(frozen=True)
class MilestoneRevisionRepr:
    effective_date_from: str
    effective_date_to: str | None
    milestone: MilestoneRepr
    observation_type: ObservationTypeRepr
    status_date: str

    def to_domain(self) -> MilestoneRevision:
        return MilestoneRevision(
            effective=DateRange(
                date_from=date.fromisoformat(self.effective_date_from),
                date_to=date.fromisoformat(self.effective_date_to) if self.effective_date_to else None,
            ),
            milestone=self.milestone.to_domain(),
            observation_type=self.observation_type.to_domain(),
            status_date=date.fromisoformat(self.status_date),
        )


@unique
class MilestoneRepr(Enum):
    PUBLIC_CONSULTATION_COMPLETED = "public consultation completed"
    FEASIBILITY_DESIGN_STARTED = "feasibility design started"
    FEASIBILITY_DESIGN_COMPLETED = "feasibility design completed"
    PRELIMINARY_DESIGN_COMPLETED = "preliminary design completed"
    OUTLINE_DESIGN_COMPLETED = "outline design completed"
    DETAILED_DESIGN_COMPLETED = "detailed design completed"
    CONSTRUCTION_STARTED = "construction started"
    CONSTRUCTION_COMPLETED = "construction completed"
    INSPECTION = "inspection"
    NOT_PROGRESSED = "not progressed"
    SUPERSEDED = "superseded"
    REMOVED = "removed"

    def to_domain(self) -> Milestone:
        members = {
            MilestoneRepr.PUBLIC_CONSULTATION_COMPLETED: Milestone.PUBLIC_CONSULTATION_COMPLETED,
            MilestoneRepr.FEASIBILITY_DESIGN_STARTED: Milestone.FEASIBILITY_DESIGN_STARTED,
            MilestoneRepr.FEASIBILITY_DESIGN_COMPLETED: Milestone.FEASIBILITY_DESIGN_COMPLETED,
            MilestoneRepr.PRELIMINARY_DESIGN_COMPLETED: Milestone.PRELIMINARY_DESIGN_COMPLETED,
            MilestoneRepr.OUTLINE_DESIGN_COMPLETED: Milestone.OUTLINE_DESIGN_COMPLETED,
            MilestoneRepr.DETAILED_DESIGN_COMPLETED: Milestone.DETAILED_DESIGN_COMPLETED,
            MilestoneRepr.CONSTRUCTION_STARTED: Milestone.CONSTRUCTION_STARTED,
            MilestoneRepr.CONSTRUCTION_COMPLETED: Milestone.CONSTRUCTION_COMPLETED,
            MilestoneRepr.INSPECTION: Milestone.INSPECTION,
            MilestoneRepr.NOT_PROGRESSED: Milestone.NOT_PROGRESSED,
            MilestoneRepr.SUPERSEDED: Milestone.SUPERSEDED,
            MilestoneRepr.REMOVED: Milestone.REMOVED,
        }
        return members[self]
