from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum, unique
from typing import Any

from flask_wtf import FlaskForm
from wtforms.form import BaseForm
from wtforms.utils import unset_value

from schemes.dicts import inverse_dict
from schemes.domain.dates import DateRange
from schemes.domain.schemes import (
    Milestone,
    MilestoneRevision,
    ObservationType,
    Scheme,
    SchemeMilestones,
)
from schemes.views.forms import (
    CustomMessageDateField,
    MultivalueInputRequired,
    MultivalueOptional,
    RemoveLeadingZerosGovDateInput,
)
from schemes.views.schemes.data_source import DataSourceRepr
from schemes.views.schemes.observations import ObservationTypeRepr


@dataclass(frozen=True)
class SchemeMilestonesContext:
    milestones: list[SchemeMilestoneRowContext]

    @classmethod
    def from_domain(cls, milestones: SchemeMilestones) -> SchemeMilestonesContext:
        return cls(
            milestones=[
                SchemeMilestoneRowContext(
                    milestone=MilestoneContext.from_domain(milestone),
                    planned=milestones.get_current_status_date(milestone, ObservationType.PLANNED),
                    actual=milestones.get_current_status_date(milestone, ObservationType.ACTUAL),
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
    def __init__(self, required_message: str, **kwargs: Any):
        super().__init__(widget=RemoveLeadingZerosGovDateInput(), format="%d %m %Y", **kwargs)
        self._required_message = required_message
        self._initial_value = unset_value

    def process_data(self, value: Any) -> None:
        super().process_data(value)
        if self._initial_value is unset_value:
            self._initial_value = value

    def pre_validate(self, form: BaseForm) -> None:
        if self._initial_value is unset_value or self._initial_value is None:
            MultivalueOptional()(form, self)
        else:
            MultivalueInputRequired(message=self._required_message)(form, self)


class ChangeMilestoneDatesForm(FlaskForm):  # type: ignore
    feasibility_design_completed_planned = MilestoneDateField(
        required_message="Enter a feasibility design completed planned date",
        invalid_message="Feasibility design completed planned date must be a real date",
    )
    feasibility_design_completed_actual = MilestoneDateField(
        required_message="Enter a feasibility design completed actual date",
        invalid_message="Feasibility design completed actual date must be a real date",
    )
    preliminary_design_completed_planned = MilestoneDateField(
        required_message="Enter a preliminary design completed planned date",
        invalid_message="Preliminary design completed planned date must be a real date",
    )
    preliminary_design_completed_actual = MilestoneDateField(
        required_message="Enter a preliminary design completed actual date",
        invalid_message="Preliminary design completed actual date must be a real date",
    )
    detailed_design_completed_planned = MilestoneDateField(
        required_message="Enter a detailed design completed planned date",
        invalid_message="Detailed design completed planned date must be a real date",
    )
    detailed_design_completed_actual = MilestoneDateField(
        required_message="Enter a detailed design completed actual date",
        invalid_message="Detailed design completed actual date must be a real date",
    )
    construction_started_planned = MilestoneDateField(
        required_message="Enter a construction started planned date",
        invalid_message="Construction started planned date must be a real date",
    )
    construction_started_actual = MilestoneDateField(
        required_message="Enter a construction started actual date",
        invalid_message="Construction started actual date must be a real date",
    )
    construction_completed_planned = MilestoneDateField(
        required_message="Enter a construction completed planned date",
        invalid_message="Construction completed planned date must be a real date",
    )

    @classmethod
    def from_domain(cls, milestones: SchemeMilestones) -> ChangeMilestoneDatesForm:
        return cls(
            feasibility_design_completed_planned=milestones.get_current_status_date(
                Milestone.FEASIBILITY_DESIGN_COMPLETED, ObservationType.PLANNED
            ),
            feasibility_design_completed_actual=milestones.get_current_status_date(
                Milestone.FEASIBILITY_DESIGN_COMPLETED, ObservationType.ACTUAL
            ),
            preliminary_design_completed_planned=milestones.get_current_status_date(
                Milestone.PRELIMINARY_DESIGN_COMPLETED, ObservationType.PLANNED
            ),
            preliminary_design_completed_actual=milestones.get_current_status_date(
                Milestone.PRELIMINARY_DESIGN_COMPLETED, ObservationType.ACTUAL
            ),
            detailed_design_completed_planned=milestones.get_current_status_date(
                Milestone.DETAILED_DESIGN_COMPLETED, ObservationType.PLANNED
            ),
            detailed_design_completed_actual=milestones.get_current_status_date(
                Milestone.DETAILED_DESIGN_COMPLETED, ObservationType.ACTUAL
            ),
            construction_started_planned=milestones.get_current_status_date(
                Milestone.CONSTRUCTION_STARTED, ObservationType.PLANNED
            ),
            construction_started_actual=milestones.get_current_status_date(
                Milestone.CONSTRUCTION_STARTED, ObservationType.ACTUAL
            ),
            construction_completed_planned=milestones.get_current_status_date(
                Milestone.CONSTRUCTION_COMPLETED, ObservationType.PLANNED
            ),
        )

    def update_domain(self, milestones: SchemeMilestones, now: datetime) -> None:
        def update_milestone(planned: date | None, actual: date | None, milestone: Milestone) -> None:
            if planned and milestones.get_current_status_date(milestone, ObservationType.PLANNED) != planned:
                milestones.update_milestone_date(now, milestone, ObservationType.PLANNED, planned)
            if actual and milestones.get_current_status_date(milestone, ObservationType.ACTUAL) != actual:
                milestones.update_milestone_date(now, milestone, ObservationType.ACTUAL, actual)

        update_milestone(
            self.feasibility_design_completed_planned.data,
            self.feasibility_design_completed_actual.data,
            Milestone.FEASIBILITY_DESIGN_COMPLETED,
        )
        update_milestone(
            self.preliminary_design_completed_planned.data,
            self.preliminary_design_completed_actual.data,
            Milestone.PRELIMINARY_DESIGN_COMPLETED,
        )
        update_milestone(
            self.detailed_design_completed_planned.data,
            self.detailed_design_completed_actual.data,
            Milestone.DETAILED_DESIGN_COMPLETED,
        )
        update_milestone(
            self.construction_started_planned.data,
            self.construction_started_actual.data,
            Milestone.CONSTRUCTION_STARTED,
        )
        update_milestone(self.construction_completed_planned.data, None, Milestone.CONSTRUCTION_COMPLETED)


@dataclass(frozen=True)
class MilestoneRevisionRepr:
    effective_date_from: str
    effective_date_to: str | None
    milestone: MilestoneRepr
    observation_type: ObservationTypeRepr
    status_date: str
    source: DataSourceRepr
    id: int | None = None

    @classmethod
    def from_domain(cls, milestone_revision: MilestoneRevision) -> MilestoneRevisionRepr:
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
