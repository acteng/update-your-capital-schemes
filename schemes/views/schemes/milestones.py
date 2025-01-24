from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum, unique
from typing import Any

from flask_wtf import FlaskForm
from wtforms import FormField
from wtforms.form import BaseForm, Form
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
from schemes.views import forms
from schemes.views.forms import (
    CustomMessageDateField,
    MultivalueInputRequired,
    MultivalueOptional,
    RemoveLeadingZerosGovDateInput,
)
from schemes.views.schemes.data_sources import DataSourceRepr
from schemes.views.schemes.observations import ObservationTypeRepr


@dataclass(frozen=True)
class SchemeMilestonesContext:
    milestones: list[SchemeMilestoneRowContext]

    @classmethod
    def from_domain(cls, scheme: Scheme) -> SchemeMilestonesContext:
        return cls(
            milestones=[
                SchemeMilestoneRowContext(
                    milestone=MilestoneContext.from_domain(milestone),
                    planned=scheme.milestones.get_current_status_date(milestone, ObservationType.PLANNED),
                    actual=scheme.milestones.get_current_status_date(milestone, ObservationType.ACTUAL),
                )
                for milestone in sorted(
                    scheme.milestones_eligible_for_authority_update, key=lambda milestone: milestone.stage_order
                )
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
        Milestone.FEASIBILITY_DESIGN_STARTED: "Feasibility design started",
        Milestone.FEASIBILITY_DESIGN_COMPLETED: "Feasibility design completed",
        Milestone.PRELIMINARY_DESIGN_COMPLETED: "Preliminary design completed",
        Milestone.OUTLINE_DESIGN_COMPLETED: "Outline design completed",
        Milestone.DETAILED_DESIGN_COMPLETED: "Detailed design completed",
        Milestone.CONSTRUCTION_STARTED: "Construction started",
        Milestone.CONSTRUCTION_COMPLETED: "Construction completed",
        Milestone.FUNDING_COMPLETED: "Funding completed",
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
    name: str
    form: ChangeMilestoneDatesForm

    @classmethod
    def from_domain(cls, scheme: Scheme, now: datetime) -> ChangeMilestoneDatesContext:
        name = scheme.overview.name
        assert name is not None

        return ChangeMilestoneDatesContext(
            id=scheme.id, name=name, form=ChangeMilestoneDatesForm.from_domain(scheme, now)
        )


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


class MilestoneDatesForm(Form):
    planned: MilestoneDateField
    actual: MilestoneDateField

    @staticmethod
    def create_class(milestone: Milestone, now: datetime) -> type[MilestoneDatesForm]:
        milestone_name = MilestoneContext.from_domain(milestone).name or ""

        class DynamicMilestoneDatesForm(MilestoneDatesForm):
            planned = MilestoneDateField(
                invalid_message=f"{milestone_name} planned date must be a real date",
                required_message=f"Enter a {milestone_name.lower()} planned date",
            )
            actual = MilestoneDateField(
                validators=[
                    forms.DateRange(max=now.date(), message=f"{milestone_name} actual date must not be in the future")
                ],
                invalid_message=f"{milestone_name} actual date must be a real date",
                required_message=f"Enter a {milestone_name.lower()} actual date",
            )

        return DynamicMilestoneDatesForm

    @classmethod
    def from_domain(cls, milestones: SchemeMilestones, milestone: Milestone, now: datetime) -> MilestoneDatesForm:
        form_class = MilestoneDatesForm.create_class(milestone, now)

        return form_class(
            planned=milestones.get_current_status_date(milestone, ObservationType.PLANNED),
            actual=milestones.get_current_status_date(milestone, ObservationType.ACTUAL),
        )

    def update_domain(self, milestones: SchemeMilestones, now: datetime, milestone: Milestone) -> None:
        current_planned_date = milestones.get_current_status_date(milestone, ObservationType.PLANNED)
        if self.planned.data and current_planned_date != self.planned.data:
            milestones.update_milestone_date(now, milestone, ObservationType.PLANNED, self.planned.data)

        current_actual_date = milestones.get_current_status_date(milestone, ObservationType.ACTUAL)
        if self.actual.data and current_actual_date != self.actual.data:
            milestones.update_milestone_date(now, milestone, ObservationType.ACTUAL, self.actual.data)


class ChangeMilestoneDatesForm(FlaskForm):  # type: ignore
    feasibility_design_completed: FormField[MilestoneDatesForm]
    preliminary_design_completed: FormField[MilestoneDatesForm]
    detailed_design_completed: FormField[MilestoneDatesForm]
    construction_started: FormField[MilestoneDatesForm]
    construction_completed: FormField[MilestoneDatesForm]

    @staticmethod
    def create_class(scheme: Scheme, now: datetime) -> type[ChangeMilestoneDatesForm]:
        class DynamicChangeMilestoneDatesForm(ChangeMilestoneDatesForm):
            pass

        for milestone in sorted(
            scheme.milestones_eligible_for_authority_update, key=lambda milestone: milestone.stage_order
        ):
            field = FormField(
                form_class=MilestoneDatesForm.create_class(milestone, now),
                label=MilestoneContext.from_domain(milestone).name,
                name=ChangeMilestoneDatesForm._to_field_name(milestone),
            )
            setattr(DynamicChangeMilestoneDatesForm, field.name, field)

        return DynamicChangeMilestoneDatesForm

    @classmethod
    def from_domain(cls, scheme: Scheme, now: datetime) -> ChangeMilestoneDatesForm:
        form_class = cls.create_class(scheme, now)

        return form_class(
            data={
                cls._to_field_name(milestone): MilestoneDatesForm.from_domain(scheme.milestones, milestone, now).data
                for milestone in scheme.milestones_eligible_for_authority_update
            }
        )

    def update_domain(self, scheme: Scheme, now: datetime) -> None:
        for milestone in sorted(
            scheme.milestones_eligible_for_authority_update, key=lambda milestone: milestone.stage_order
        ):
            field_name = self._to_field_name(milestone)
            self[field_name].form.update_domain(scheme.milestones, now, milestone)

    @staticmethod
    def _to_field_name(milestone: Milestone) -> str:
        return milestone.name.lower()


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
    FUNDING_COMPLETED = "funding completed"
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
            Milestone.FUNDING_COMPLETED: MilestoneRepr.FUNDING_COMPLETED,
            Milestone.NOT_PROGRESSED: MilestoneRepr.NOT_PROGRESSED,
            Milestone.SUPERSEDED: MilestoneRepr.SUPERSEDED,
            Milestone.REMOVED: MilestoneRepr.REMOVED,
        }
