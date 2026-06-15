from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Self

from flask_wtf import FlaskForm
from wtforms import FormField
from wtforms.form import BaseForm, Form

from schemes.domain.schemes.milestones import Milestone, SchemeMilestones
from schemes.domain.schemes.observations import ObservationType
from schemes.domain.schemes.schemes import Scheme
from schemes.views import forms
from schemes.views.forms import (
    CustomMessageDateField,
    MultivalueInputRequired,
    MultivalueOptional,
    RemoveLeadingZerosGovDateInput,
)


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
    def from_domain(cls, milestone: Milestone | None) -> Self:
        return cls(name=cls._NAMES[milestone] if milestone else None)


@dataclass(frozen=True)
class SchemeMilestoneRowContext:
    milestone: MilestoneContext
    planned: date | None
    actual: date | None


@dataclass(frozen=True)
class SchemeMilestonesContext:
    milestones: list[SchemeMilestoneRowContext]

    @classmethod
    def from_domain(cls, scheme: Scheme) -> Self:
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


class MilestoneDateField(CustomMessageDateField):
    def __init__(self, required_message: str, **kwargs: Any):
        super().__init__(widget=RemoveLeadingZerosGovDateInput(), format="%d %m %Y", **kwargs)
        self._required_message = required_message

    def pre_validate(self, form: BaseForm) -> None:
        if self.object_data is None:
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
                required_message=f"{milestone_name} planned date cannot be removed",
            )
            actual = MilestoneDateField(
                validators=[
                    forms.DateRange(max=now.date(), message=f"{milestone_name} actual date must not be in the future")
                ],
                invalid_message=f"{milestone_name} actual date must be a real date",
                required_message=f"{milestone_name} actual date cannot be removed",
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
class ChangeMilestoneDatesContext:
    reference: str
    name: str
    form: ChangeMilestoneDatesForm

    @classmethod
    def from_domain(cls, scheme: Scheme, now: datetime) -> Self:
        name = scheme.overview.name
        assert name is not None

        return cls(reference=scheme.reference, name=name, form=ChangeMilestoneDatesForm.from_domain(scheme, now))
