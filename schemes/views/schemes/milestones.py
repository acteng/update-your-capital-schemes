from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum, unique
from typing import Any

from flask_wtf import FlaskForm
from govuk_frontend_wtf.wtforms_widgets import GovDateInput
from wtforms.fields.datetime import DateField

from schemes.dicts import inverse_dict
from schemes.domain.schemes import (
    DateRange,
    Milestone,
    MilestoneRevision,
    ObservationType,
    Scheme,
    SchemeMilestones,
)
from schemes.views.forms import CustomMessageDateField, MultivalueOptional
from schemes.views.schemes.funding import DataSourceRepr
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
class ChangeMilestoneDatesContext:
    id: int
    form: ChangeMilestoneDatesForm

    @classmethod
    def from_domain(cls, scheme: Scheme) -> ChangeMilestoneDatesContext:
        return ChangeMilestoneDatesContext(id=scheme.id, form=ChangeMilestoneDatesForm.from_domain(scheme.milestones))


class MilestoneDateField(CustomMessageDateField):
    def __init__(self, **kwargs: Any):
        super().__init__(widget=GovDateInput(), format="%d %m %Y", validators=[MultivalueOptional()], **kwargs)


class ChangeMilestoneDatesForm(FlaskForm):  # type: ignore
    construction_started_planned = MilestoneDateField(message="Construction started planned date must be a real date")
    construction_started_actual = MilestoneDateField(message="Construction started actual date must be a real date")
    construction_completed_planned = MilestoneDateField(
        message="Construction completed planned date must be a real date"
    )
    construction_completed_actual = MilestoneDateField(message="Construction completed actual date must be a real date")

    @classmethod
    def from_domain(cls, milestones: SchemeMilestones) -> ChangeMilestoneDatesForm:
        def get_status_date(milestone: Milestone, observation_type: ObservationType) -> date | None:
            revisions = (
                revision.status_date
                for revision in milestones.current_milestone_revisions
                if revision.milestone == milestone and revision.observation_type == observation_type
            )
            return next(revisions, None)

        # TODO: support all milestones
        return cls(
            construction_started_planned=get_status_date(Milestone.CONSTRUCTION_STARTED, ObservationType.PLANNED),
            construction_started_actual=get_status_date(Milestone.CONSTRUCTION_STARTED, ObservationType.ACTUAL),
            construction_completed_planned=get_status_date(Milestone.CONSTRUCTION_COMPLETED, ObservationType.PLANNED),
            construction_completed_actual=get_status_date(Milestone.CONSTRUCTION_COMPLETED, ObservationType.ACTUAL),
        )

    def update_domain(self, milestones: SchemeMilestones, now: datetime) -> None:
        def update_milestone(field: DateField, milestone: Milestone, observation_type: ObservationType) -> None:
            if field.data:
                milestones.update_milestone_date(now, milestone, observation_type, field.data)

        # TODO: support all milestones
        update_milestone(self.construction_started_planned, Milestone.CONSTRUCTION_STARTED, ObservationType.PLANNED)
        update_milestone(self.construction_started_actual, Milestone.CONSTRUCTION_STARTED, ObservationType.ACTUAL)
        update_milestone(self.construction_completed_planned, Milestone.CONSTRUCTION_COMPLETED, ObservationType.PLANNED)
        update_milestone(self.construction_completed_actual, Milestone.CONSTRUCTION_COMPLETED, ObservationType.ACTUAL)


@dataclass(frozen=True)
class MilestoneRevisionRepr:
    id: int
    effective_date_from: str
    effective_date_to: str | None
    milestone: MilestoneRepr
    observation_type: ObservationTypeRepr
    status_date: str
    source: DataSourceRepr

    @classmethod
    def from_domain(cls, milestone_revision: MilestoneRevision) -> MilestoneRevisionRepr:
        if not milestone_revision.id:
            raise ValueError("Milestone revision must be persistent")

        return cls(
            id=milestone_revision.id,
            effective_date_from=milestone_revision.effective.date_from.isoformat(),
            effective_date_to=(
                milestone_revision.effective.date_to.isoformat() if milestone_revision.effective.date_to else None
            ),
            milestone=MilestoneRepr.from_domain(milestone_revision.milestone),
            observation_type=ObservationTypeRepr.from_domain(milestone_revision.observation_type),
            status_date=milestone_revision.status_date.isoformat(),
            source=DataSourceRepr.from_domain(milestone_revision.source),
        )

    def to_domain(self) -> MilestoneRevision:
        return MilestoneRevision(
            id_=self.id,
            effective=DateRange(
                date_from=datetime.fromisoformat(self.effective_date_from),
                date_to=datetime.fromisoformat(self.effective_date_to) if self.effective_date_to else None,
            ),
            milestone=self.milestone.to_domain(),
            observation_type=self.observation_type.to_domain(),
            status_date=date.fromisoformat(self.status_date),
            source=self.source.to_domain(),
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

    @classmethod
    def from_domain(cls, milestone: Milestone) -> MilestoneRepr:
        return cls._members()[milestone]

    def to_domain(self) -> Milestone:
        return inverse_dict(self._members())[self]

    @staticmethod
    def _members() -> dict[Milestone, MilestoneRepr]:
        return {
            Milestone.PUBLIC_CONSULTATION_COMPLETED: MilestoneRepr.PUBLIC_CONSULTATION_COMPLETED,
            Milestone.FEASIBILITY_DESIGN_STARTED: MilestoneRepr.FEASIBILITY_DESIGN_STARTED,
            Milestone.FEASIBILITY_DESIGN_COMPLETED: MilestoneRepr.FEASIBILITY_DESIGN_COMPLETED,
            Milestone.PRELIMINARY_DESIGN_COMPLETED: MilestoneRepr.PRELIMINARY_DESIGN_COMPLETED,
            Milestone.OUTLINE_DESIGN_COMPLETED: MilestoneRepr.OUTLINE_DESIGN_COMPLETED,
            Milestone.DETAILED_DESIGN_COMPLETED: MilestoneRepr.DETAILED_DESIGN_COMPLETED,
            Milestone.CONSTRUCTION_STARTED: MilestoneRepr.CONSTRUCTION_STARTED,
            Milestone.CONSTRUCTION_COMPLETED: MilestoneRepr.CONSTRUCTION_COMPLETED,
            Milestone.INSPECTION: MilestoneRepr.INSPECTION,
            Milestone.NOT_PROGRESSED: MilestoneRepr.NOT_PROGRESSED,
            Milestone.SUPERSEDED: MilestoneRepr.SUPERSEDED,
            Milestone.REMOVED: MilestoneRepr.REMOVED,
        }
