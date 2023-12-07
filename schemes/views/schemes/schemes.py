from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields
from datetime import date
from decimal import Decimal
from enum import Enum, unique
from itertools import groupby
from typing import Any, Iterator

import inject
from flask import Blueprint, Response, render_template, session

from schemes.domain.authorities import Authority, AuthorityRepository
from schemes.domain.schemes import (
    DateRange,
    FundingProgramme,
    Milestone,
    MilestoneRevision,
    ObservationType,
    OutputMeasure,
    OutputRevision,
    OutputType,
    OutputTypeMeasure,
    Scheme,
    SchemeRepository,
    SchemeType,
)
from schemes.domain.users import UserRepository
from schemes.views.auth.api_key import api_key_auth
from schemes.views.auth.bearer import bearer_auth
from schemes.views.schemes.funding import FinancialRevisionRepr, SchemeFundingContext
from schemes.views.schemes.observations import ObservationTypeRepr

bp = Blueprint("schemes", __name__)


@bp.get("")
@bearer_auth
@inject.autoparams()
def index(users: UserRepository, authorities: AuthorityRepository, schemes: SchemeRepository) -> str:
    user_info = session["user"]
    user = users.get_by_email(user_info["email"])
    assert user
    authority = authorities.get(user.authority_id)
    assert authority
    authority_schemes = schemes.get_by_authority(authority.id)

    context = SchemesContext.from_domain(authority, authority_schemes)
    return render_template("schemes.html", **asdict(context))


@dataclass(frozen=True)
class SchemesContext:
    authority_name: str
    schemes: list[SchemeRowContext]

    @classmethod
    def from_domain(cls, authority: Authority, schemes: list[Scheme]) -> SchemesContext:
        return cls(
            authority_name=authority.name,
            schemes=[SchemeRowContext.from_domain(scheme) for scheme in schemes],
        )


@dataclass(frozen=True)
class SchemeRowContext:
    id: int
    reference: str
    funding_programme: FundingProgrammeContext
    name: str

    @classmethod
    def from_domain(cls, scheme: Scheme) -> SchemeRowContext:
        return cls(
            id=scheme.id,
            reference=scheme.reference,
            funding_programme=FundingProgrammeContext.from_domain(scheme.funding_programme),
            name=scheme.name,
        )


@bp.get("<int:scheme_id>")
@bearer_auth
@inject.autoparams("schemes")
def get(schemes: SchemeRepository, scheme_id: int) -> str:
    scheme = schemes.get(scheme_id)
    assert scheme

    context = SchemeContext.from_domain(scheme)
    return render_template("scheme.html", **_as_shallow_dict(context))


def _as_shallow_dict(obj: Any) -> dict[str, Any]:
    return dict((field_.name, getattr(obj, field_.name)) for field_ in fields(obj))


@dataclass(frozen=True)
class SchemeContext:
    name: str
    overview: SchemeOverviewContext
    funding: SchemeFundingContext
    milestones: SchemeMilestonesContext
    outputs: SchemeOutputsContext

    @classmethod
    def from_domain(cls, scheme: Scheme) -> SchemeContext:
        return cls(
            name=scheme.name,
            overview=SchemeOverviewContext.from_domain(scheme),
            funding=SchemeFundingContext.from_domain(scheme.funding),
            milestones=SchemeMilestonesContext.from_domain(scheme.milestones.current_milestone_revisions),
            outputs=SchemeOutputsContext.from_domain(scheme.outputs.current_output_revisions),
        )


@dataclass(frozen=True)
class SchemeOverviewContext:
    reference: str
    type: SchemeTypeContext
    funding_programme: FundingProgrammeContext
    current_milestone: MilestoneContext

    @classmethod
    def from_domain(cls, scheme: Scheme) -> SchemeOverviewContext:
        return cls(
            reference=scheme.reference,
            type=SchemeTypeContext.from_domain(scheme.type),
            funding_programme=FundingProgrammeContext.from_domain(scheme.funding_programme),
            current_milestone=MilestoneContext.from_domain(scheme.milestones.current_milestone),
        )


@dataclass(frozen=True)
class SchemeTypeContext:
    name: str | None
    _NAMES = {
        SchemeType.DEVELOPMENT: "Development",
        SchemeType.CONSTRUCTION: "Construction",
    }

    @classmethod
    def from_domain(cls, type_: SchemeType | None) -> SchemeTypeContext:
        return cls(name=cls._NAMES[type_] if type_ else None)


@dataclass(frozen=True)
class FundingProgrammeContext:
    name: str | None
    _NAMES = {
        FundingProgramme.ATF2: "ATF2",
        FundingProgramme.ATF3: "ATF3",
        FundingProgramme.ATF4: "ATF4",
        FundingProgramme.ATF4E: "ATF4e",
        FundingProgramme.ATF5: "ATF5",
        FundingProgramme.MRN: "MRN",
        FundingProgramme.LUF: "LUF",
        FundingProgramme.CRSTS: "CRSTS",
    }

    @classmethod
    def from_domain(cls, funding_programme: FundingProgramme | None) -> FundingProgrammeContext:
        return cls(name=cls._NAMES[funding_programme] if funding_programme else None)


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
                    Milestone.PUBLIC_CONSULTATION_COMPLETED,
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
class SchemeOutputsContext:
    outputs: list[SchemeOutputRowContext]

    @classmethod
    def from_domain(cls, output_revisions: list[OutputRevision]) -> SchemeOutputsContext:
        return cls(
            outputs=[
                SchemeOutputRowContext(
                    type=OutputTypeContext.from_domain(type_),
                    measure=OutputMeasureContext.from_domain(measure),
                    planned=cls._get_value(group, ObservationType.PLANNED),
                    actual=cls._get_value(group, ObservationType.ACTUAL),
                )
                for (type_, measure), group in groupby(
                    sorted(output_revisions, key=SchemeOutputsContext._by_type_and_measure),
                    cls._by_type_and_measure,
                )
            ]
        )

    @staticmethod
    def _by_type_and_measure(output_revision: OutputRevision) -> tuple[OutputType, OutputMeasure]:
        return output_revision.type_measure.type, output_revision.type_measure.measure

    @staticmethod
    def _get_value(output_revisions: Iterator[OutputRevision], observation_type: ObservationType) -> Decimal | None:
        revisions = (revision.value for revision in output_revisions if revision.observation_type == observation_type)
        return next(revisions, None)


@dataclass(frozen=True)
class SchemeOutputRowContext:
    type: OutputTypeContext
    measure: OutputMeasureContext
    planned: Decimal | None
    actual: Decimal | None

    @property
    def planned_not_yet_delivered(self) -> Decimal:
        planned = self.planned or Decimal(0)
        actual = self.actual or Decimal(0)
        return planned - actual

    @property
    def delivery_status(self) -> str:
        planned = self.planned or Decimal(0)
        actual = self.actual or Decimal(0)
        match (planned, actual):
            case (0, _):
                return "No outputs recorded"
            case (_, 0):
                return "Not started"
            case (planned, actual) if planned > actual:
                return "In progress"
            case (planned, actual) if planned == actual:
                return "Complete"
        return "More outputs than planned"


@dataclass(frozen=True)
class OutputTypeContext:
    name: str
    _NAMES = {
        OutputType.NEW_SEGREGATED_CYCLING_FACILITY: "New segregated cycling facility",
        OutputType.NEW_TEMPORARY_SEGREGATED_CYCLING_FACILITY: "New temporary segregated cycling facility",
        OutputType.NEW_JUNCTION_TREATMENT: "New junction treatment",
        OutputType.NEW_PERMANENT_FOOTWAY: "New permanent footway",
        OutputType.NEW_TEMPORARY_FOOTWAY: "New temporary footway",
        OutputType.NEW_SHARED_USE_FACILITIES: "New shared use (walking and cycling) facilities",
        OutputType.NEW_SHARED_USE_FACILITIES_WHEELING: "New shared use (walking, wheeling & cycling) facilities",
        OutputType.IMPROVEMENTS_TO_EXISTING_ROUTE: "Improvements to make an existing walking/cycle route safer",
        OutputType.AREA_WIDE_TRAFFIC_MANAGEMENT: "Area-wide traffic management (including by TROs (both permanent and experimental))",
        OutputType.BUS_PRIORITY_MEASURES: "Bus priority measures that also enable active travel (for example, bus gates)",
        OutputType.SECURE_CYCLE_PARKING: "Provision of secure cycle parking facilities",
        OutputType.NEW_ROAD_CROSSINGS: "New road crossings",
        OutputType.RESTRICTION_OR_REDUCTION_OF_CAR_PARKING_AVAILABILITY: "Restriction or reduction of car parking availability",
        OutputType.SCHOOL_STREETS: "School streets",
        OutputType.UPGRADES_TO_EXISTING_FACILITIES: "Upgrades to existing facilities (e.g. surfacing, signage, signals)",
        OutputType.E_SCOOTER_TRIALS: "E-scooter trials",
        OutputType.PARK_AND_CYCLE_STRIDE_FACILITIES: "Park and cycle/stride facilities",
        OutputType.TRAFFIC_CALMING: "Traffic calming (e.g. lane closures, reducing speed limits)",
        OutputType.WIDENING_EXISTING_FOOTWAY: "Widening existing footway",
        OutputType.OTHER_INTERVENTIONS: "Other interventions",
    }

    @classmethod
    def from_domain(cls, type_: OutputType) -> OutputTypeContext:
        return cls(name=cls._NAMES[type_])


@dataclass(frozen=True)
class OutputMeasureContext:
    name: str
    _NAMES = {
        OutputMeasure.MILES: "Miles",
        OutputMeasure.NUMBER_OF_JUNCTIONS: "Number of junctions",
        OutputMeasure.SIZE_OF_AREA: "Size of area",
        OutputMeasure.NUMBER_OF_PARKING_SPACES: "Number of parking spaces",
        OutputMeasure.NUMBER_OF_CROSSINGS: "Number of crossings",
        OutputMeasure.NUMBER_OF_SCHOOL_STREETS: "Number of school streets",
        OutputMeasure.NUMBER_OF_TRIALS: "Number of trials",
        OutputMeasure.NUMBER_OF_BUS_GATES: "Number of bus gates",
        OutputMeasure.NUMBER_OF_UPGRADES: "Number of upgrades",
        OutputMeasure.NUMBER_OF_CHILDREN_AFFECTED: "Number of children affected",
        OutputMeasure.NUMBER_OF_MEASURES_PLANNED: "Number of measures planned",
    }

    @classmethod
    def from_domain(cls, measure: OutputMeasure) -> OutputMeasureContext:
        return cls(name=cls._NAMES[measure])


@bp.delete("")
@api_key_auth
@inject.autoparams()
def clear(schemes: SchemeRepository) -> Response:
    schemes.clear()
    return Response(status=204)


@dataclass(frozen=True)
class SchemeRepr:
    id: int
    name: str
    type: SchemeTypeRepr | None = None
    funding_programme: FundingProgrammeRepr | None = None
    financial_revisions: list[FinancialRevisionRepr] = field(default_factory=list)
    milestone_revisions: list[MilestoneRevisionRepr] = field(default_factory=list)
    output_revisions: list[OutputRevisionRepr] = field(default_factory=list)

    def to_domain(self, authority_id: int) -> Scheme:
        scheme = Scheme(id_=self.id, name=self.name, authority_id=authority_id)
        scheme.type = self.type.to_domain() if self.type else None
        scheme.funding_programme = self.funding_programme.to_domain() if self.funding_programme else None

        for financial_revision_repr in self.financial_revisions:
            scheme.funding.update_financial(financial_revision_repr.to_domain())

        for milestone_revision_repr in self.milestone_revisions:
            scheme.milestones.update_milestone(milestone_revision_repr.to_domain())

        for output_revision_repr in self.output_revisions:
            scheme.outputs.update_output(output_revision_repr.to_domain())

        return scheme


@unique
class SchemeTypeRepr(Enum):
    DEVELOPMENT = "development"
    CONSTRUCTION = "construction"

    def to_domain(self) -> SchemeType:
        members = {
            SchemeTypeRepr.DEVELOPMENT: SchemeType.DEVELOPMENT,
            SchemeTypeRepr.CONSTRUCTION: SchemeType.CONSTRUCTION,
        }
        return members[self]


@unique
class FundingProgrammeRepr(Enum):
    ATF2 = "ATF2"
    ATF3 = "ATF3"
    ATF4 = "ATF4"
    ATF4E = "ATF4e"
    ATF5 = "ATF5"
    MRN = "MRN"
    LUF = "LUF"
    CRSTS = "CRSTS"

    def to_domain(self) -> FundingProgramme:
        members = {
            FundingProgrammeRepr.ATF2: FundingProgramme.ATF2,
            FundingProgrammeRepr.ATF3: FundingProgramme.ATF3,
            FundingProgrammeRepr.ATF4: FundingProgramme.ATF4,
            FundingProgrammeRepr.ATF4E: FundingProgramme.ATF4E,
            FundingProgrammeRepr.ATF5: FundingProgramme.ATF5,
            FundingProgrammeRepr.MRN: FundingProgramme.MRN,
            FundingProgrammeRepr.LUF: FundingProgramme.LUF,
            FundingProgrammeRepr.CRSTS: FundingProgramme.CRSTS,
        }
        return members[self]


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


@dataclass(frozen=True)
class OutputRevisionRepr:
    effective_date_from: str
    effective_date_to: str | None
    type: OutputTypeRepr
    measure: OutputMeasureRepr
    value: str
    observation_type: ObservationTypeRepr

    def to_domain(self) -> OutputRevision:
        return OutputRevision(
            effective=DateRange(
                date_from=date.fromisoformat(self.effective_date_from),
                date_to=date.fromisoformat(self.effective_date_to) if self.effective_date_to else None,
            ),
            type_measure=OutputTypeMeasure.from_type_and_measure(self.type.to_domain(), self.measure.to_domain()),
            value=Decimal(self.value),
            observation_type=self.observation_type.to_domain(),
        )


@unique
class OutputTypeRepr(Enum):
    NEW_SEGREGATED_CYCLING_FACILITY = "New segregated cycling facility"
    NEW_TEMPORARY_SEGREGATED_CYCLING_FACILITY = "New temporary segregated cycling facility"
    NEW_JUNCTION_TREATMENT = "New junction treatment"
    NEW_PERMANENT_FOOTWAY = "New permanent footway"
    NEW_TEMPORARY_FOOTWAY = "New temporary footway"
    NEW_SHARED_USE_FACILITIES = "New shared use (walking and cycling) facilities"
    NEW_SHARED_USE_FACILITIES_WHEELING = "New shared use (walking, wheeling & cycling) facilities"
    IMPROVEMENTS_TO_EXISTING_ROUTE = "Improvements to make an existing walking/cycle route safer"
    AREA_WIDE_TRAFFIC_MANAGEMENT = "Area-wide traffic management (including by TROs (both permanent and experimental))"
    BUS_PRIORITY_MEASURES = "Bus priority measures that also enable active travel (for example, bus gates)"
    SECURE_CYCLE_PARKING = "Provision of secure cycle parking facilities"
    NEW_ROAD_CROSSINGS = "New road crossings"
    RESTRICTION_OR_REDUCTION_OF_CAR_PARKING_AVAILABILITY = "Restriction or reduction of car parking availability"
    SCHOOL_STREETS = "School streets"
    UPGRADES_TO_EXISTING_FACILITIES = "Upgrades to existing facilities (e.g. surfacing, signage, signals)"
    E_SCOOTER_TRIALS = "E-scooter trials"
    PARK_AND_CYCLE_STRIDE_FACILITIES = "Park and cycle/stride facilities"
    TRAFFIC_CALMING = "Traffic calming (e.g. lane closures, reducing speed limits)"
    WIDENING_EXISTING_FOOTWAY = "Widening existing footway"
    OTHER_INTERVENTIONS = "Other interventions"

    def to_domain(self) -> OutputType:
        members = {
            OutputTypeRepr.NEW_SEGREGATED_CYCLING_FACILITY: OutputType.NEW_SEGREGATED_CYCLING_FACILITY,
            OutputTypeRepr.NEW_TEMPORARY_SEGREGATED_CYCLING_FACILITY: OutputType.NEW_TEMPORARY_SEGREGATED_CYCLING_FACILITY,
            OutputTypeRepr.NEW_JUNCTION_TREATMENT: OutputType.NEW_JUNCTION_TREATMENT,
            OutputTypeRepr.NEW_PERMANENT_FOOTWAY: OutputType.NEW_PERMANENT_FOOTWAY,
            OutputTypeRepr.NEW_TEMPORARY_FOOTWAY: OutputType.NEW_TEMPORARY_FOOTWAY,
            OutputTypeRepr.NEW_SHARED_USE_FACILITIES: OutputType.NEW_SHARED_USE_FACILITIES,
            OutputTypeRepr.NEW_SHARED_USE_FACILITIES_WHEELING: OutputType.NEW_SHARED_USE_FACILITIES_WHEELING,
            OutputTypeRepr.IMPROVEMENTS_TO_EXISTING_ROUTE: OutputType.IMPROVEMENTS_TO_EXISTING_ROUTE,
            OutputTypeRepr.AREA_WIDE_TRAFFIC_MANAGEMENT: OutputType.AREA_WIDE_TRAFFIC_MANAGEMENT,
            OutputTypeRepr.BUS_PRIORITY_MEASURES: OutputType.BUS_PRIORITY_MEASURES,
            OutputTypeRepr.SECURE_CYCLE_PARKING: OutputType.SECURE_CYCLE_PARKING,
            OutputTypeRepr.NEW_ROAD_CROSSINGS: OutputType.NEW_ROAD_CROSSINGS,
            OutputTypeRepr.RESTRICTION_OR_REDUCTION_OF_CAR_PARKING_AVAILABILITY: OutputType.RESTRICTION_OR_REDUCTION_OF_CAR_PARKING_AVAILABILITY,
            OutputTypeRepr.SCHOOL_STREETS: OutputType.SCHOOL_STREETS,
            OutputTypeRepr.UPGRADES_TO_EXISTING_FACILITIES: OutputType.UPGRADES_TO_EXISTING_FACILITIES,
            OutputTypeRepr.E_SCOOTER_TRIALS: OutputType.E_SCOOTER_TRIALS,
            OutputTypeRepr.PARK_AND_CYCLE_STRIDE_FACILITIES: OutputType.PARK_AND_CYCLE_STRIDE_FACILITIES,
            OutputTypeRepr.TRAFFIC_CALMING: OutputType.TRAFFIC_CALMING,
            OutputTypeRepr.WIDENING_EXISTING_FOOTWAY: OutputType.WIDENING_EXISTING_FOOTWAY,
            OutputTypeRepr.OTHER_INTERVENTIONS: OutputType.OTHER_INTERVENTIONS,
        }
        return members[self]


@unique
class OutputMeasureRepr(Enum):
    MILES = "miles"
    NUMBER_OF_JUNCTIONS = "number of junctions"
    SIZE_OF_AREA = "size of area"
    NUMBER_OF_PARKING_SPACES = "number of parking spaces"
    NUMBER_OF_CROSSINGS = "number of crossings"
    NUMBER_OF_SCHOOL_STREETS = "number of school streets"
    NUMBER_OF_TRIALS = "number of trials"
    NUMBER_OF_BUS_GATES = "number of bus gates"
    NUMBER_OF_UPGRADES = "number of upgrades"
    NUMBER_OF_CHILDREN_AFFECTED = "number of children affected"
    NUMBER_OF_MEASURES_PLANNED = "number of measures planned"

    def to_domain(self) -> OutputMeasure:
        members = {
            OutputMeasureRepr.MILES: OutputMeasure.MILES,
            OutputMeasureRepr.NUMBER_OF_JUNCTIONS: OutputMeasure.NUMBER_OF_JUNCTIONS,
            OutputMeasureRepr.SIZE_OF_AREA: OutputMeasure.SIZE_OF_AREA,
            OutputMeasureRepr.NUMBER_OF_PARKING_SPACES: OutputMeasure.NUMBER_OF_PARKING_SPACES,
            OutputMeasureRepr.NUMBER_OF_CROSSINGS: OutputMeasure.NUMBER_OF_CROSSINGS,
            OutputMeasureRepr.NUMBER_OF_SCHOOL_STREETS: OutputMeasure.NUMBER_OF_SCHOOL_STREETS,
            OutputMeasureRepr.NUMBER_OF_TRIALS: OutputMeasure.NUMBER_OF_TRIALS,
            OutputMeasureRepr.NUMBER_OF_BUS_GATES: OutputMeasure.NUMBER_OF_BUS_GATES,
            OutputMeasureRepr.NUMBER_OF_UPGRADES: OutputMeasure.NUMBER_OF_UPGRADES,
            OutputMeasureRepr.NUMBER_OF_CHILDREN_AFFECTED: OutputMeasure.NUMBER_OF_CHILDREN_AFFECTED,
            OutputMeasureRepr.NUMBER_OF_MEASURES_PLANNED: OutputMeasure.NUMBER_OF_MEASURES_PLANNED,
        }
        return members[self]
