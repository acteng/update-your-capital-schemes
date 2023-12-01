from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date
from decimal import Decimal
from enum import Enum, unique

import inject
from flask import Blueprint, Response, render_template, session

from schemes.domain.authorities import Authority, AuthorityRepository
from schemes.domain.schemes import (
    DataSource,
    DateRange,
    FinancialRevision,
    FinancialType,
    FundingProgramme,
    Milestone,
    MilestoneRevision,
    ObservationType,
    Scheme,
    SchemeFunding,
    SchemeRepository,
    SchemeType,
)
from schemes.domain.users import UserRepository
from schemes.views.auth.api_key import api_key_auth
from schemes.views.auth.bearer import bearer_auth

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

    context = SchemesContext.for_domain(authority, authority_schemes)
    return render_template("schemes.html", **asdict(context))


@dataclass(frozen=True)
class SchemesContext:
    authority_name: str
    schemes: list[SchemeRowContext]

    @staticmethod
    def for_domain(authority: Authority, schemes: list[Scheme]) -> SchemesContext:
        return SchemesContext(
            authority_name=authority.name,
            schemes=[SchemeRowContext.for_domain(scheme) for scheme in schemes],
        )


@dataclass(frozen=True)
class SchemeRowContext:
    id: int
    reference: str
    funding_programme: FundingProgrammeContext
    name: str

    @staticmethod
    def for_domain(scheme: Scheme) -> SchemeRowContext:
        return SchemeRowContext(
            id=scheme.id,
            reference=scheme.reference,
            funding_programme=FundingProgrammeContext.for_domain(scheme.funding_programme),
            name=scheme.name,
        )


@bp.get("<int:scheme_id>")
@bearer_auth
@inject.autoparams("schemes")
def get(schemes: SchemeRepository, scheme_id: int) -> str:
    scheme = schemes.get(scheme_id)
    assert scheme

    context = SchemeContext.for_domain(scheme)
    return render_template("scheme.html", **asdict(context))


@dataclass(frozen=True)
class SchemeContext:
    name: str
    overview: SchemeOverviewContext
    funding: SchemeFundingContext
    milestones: SchemeMilestonesContext

    @staticmethod
    def for_domain(scheme: Scheme) -> SchemeContext:
        return SchemeContext(
            name=scheme.name,
            overview=SchemeOverviewContext.for_domain(scheme),
            funding=SchemeFundingContext.for_domain(scheme.funding),
            milestones=SchemeMilestonesContext.for_domain(scheme.milestones.current_milestone_revisions),
        )


@dataclass(frozen=True)
class SchemeOverviewContext:
    reference: str
    type: SchemeTypeContext
    funding_programme: FundingProgrammeContext
    current_milestone: MilestoneContext

    @staticmethod
    def for_domain(scheme: Scheme) -> SchemeOverviewContext:
        return SchemeOverviewContext(
            reference=scheme.reference,
            type=SchemeTypeContext.for_domain(scheme.type),
            funding_programme=FundingProgrammeContext.for_domain(scheme.funding_programme),
            current_milestone=MilestoneContext.for_domain(scheme.milestones.current_milestone),
        )


@dataclass(frozen=True)
class SchemeTypeContext:
    name: str | None

    @staticmethod
    def for_domain(type_: SchemeType | None) -> SchemeTypeContext:
        type_names = {
            SchemeType.DEVELOPMENT: "Development",
            SchemeType.CONSTRUCTION: "Construction",
        }
        return SchemeTypeContext(name=type_names[type_] if type_ else None)


@dataclass(frozen=True)
class FundingProgrammeContext:
    name: str | None

    @staticmethod
    def for_domain(funding_programme: FundingProgramme | None) -> FundingProgrammeContext:
        funding_programme_names = {
            FundingProgramme.ATF2: "ATF2",
            FundingProgramme.ATF3: "ATF3",
            FundingProgramme.ATF4: "ATF4",
            FundingProgramme.ATF4E: "ATF4e",
            FundingProgramme.ATF5: "ATF5",
            FundingProgramme.MRN: "MRN",
            FundingProgramme.LUF: "LUF",
            FundingProgramme.CRSTS: "CRSTS",
        }
        return FundingProgrammeContext(name=funding_programme_names[funding_programme] if funding_programme else None)


@dataclass(frozen=True)
class MilestoneContext:
    name: str | None

    @staticmethod
    def for_domain(milestone: Milestone | None) -> MilestoneContext:
        milestone_names = {
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
        return MilestoneContext(name=milestone_names[milestone] if milestone else None)


@dataclass(frozen=True)
class SchemeFundingContext:
    funding_allocation: Decimal | None
    spend_to_date: Decimal | None
    change_control_adjustment: Decimal | None
    allocation_still_to_spend: Decimal

    @staticmethod
    def for_domain(funding: SchemeFunding) -> SchemeFundingContext:
        return SchemeFundingContext(
            funding_allocation=funding.funding_allocation,
            spend_to_date=funding.spend_to_date,
            change_control_adjustment=funding.change_control_adjustment,
            allocation_still_to_spend=funding.allocation_still_to_spend,
        )


@dataclass(frozen=True)
class SchemeMilestonesContext:
    milestones: list[SchemeMilestoneRowContext]

    @staticmethod
    def for_domain(milestone_revisions: list[MilestoneRevision]) -> SchemeMilestonesContext:
        def get_status_date(milestone: Milestone, observation_type: ObservationType) -> date | None:
            revisions = (
                revision.status_date
                for revision in milestone_revisions
                if revision.milestone == milestone and revision.observation_type == observation_type
            )
            return next(revisions, None)

        return SchemeMilestonesContext(
            milestones=[
                SchemeMilestoneRowContext(
                    milestone=MilestoneContext.for_domain(milestone),
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

    def to_domain(self, authority_id: int) -> Scheme:
        scheme = Scheme(id_=self.id, name=self.name, authority_id=authority_id)
        scheme.type = self.type.to_domain() if self.type else None
        scheme.funding_programme = self.funding_programme.to_domain() if self.funding_programme else None

        for financial_revision_repr in self.financial_revisions:
            scheme.funding.update_financial(financial_revision_repr.to_domain())

        for milestone_revision_repr in self.milestone_revisions:
            scheme.milestones.update_milestone(milestone_revision_repr.to_domain())

        return scheme


@unique
class SchemeTypeRepr(Enum):
    DEVELOPMENT = "development"
    CONSTRUCTION = "construction"

    def to_domain(self) -> SchemeType:
        return {
            SchemeTypeRepr.DEVELOPMENT: SchemeType.DEVELOPMENT,
            SchemeTypeRepr.CONSTRUCTION: SchemeType.CONSTRUCTION,
        }[self]


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
        return {
            FundingProgrammeRepr.ATF2: FundingProgramme.ATF2,
            FundingProgrammeRepr.ATF3: FundingProgramme.ATF3,
            FundingProgrammeRepr.ATF4: FundingProgramme.ATF4,
            FundingProgrammeRepr.ATF4E: FundingProgramme.ATF4E,
            FundingProgrammeRepr.ATF5: FundingProgramme.ATF5,
            FundingProgrammeRepr.MRN: FundingProgramme.MRN,
            FundingProgrammeRepr.LUF: FundingProgramme.LUF,
            FundingProgrammeRepr.CRSTS: FundingProgramme.CRSTS,
        }[self]


@dataclass(frozen=True)
class FinancialRevisionRepr:
    effective_date_from: str
    effective_date_to: str | None
    type: FinancialTypeRepr
    amount: str
    source: DataSourceRepr

    def to_domain(self) -> FinancialRevision:
        return FinancialRevision(
            effective=DateRange(
                date_from=date.fromisoformat(self.effective_date_from),
                date_to=date.fromisoformat(self.effective_date_to) if self.effective_date_to else None,
            ),
            type=self.type.to_domain(),
            amount=Decimal(self.amount),
            source=self.source.to_domain(),
        )


@unique
class FinancialTypeRepr(Enum):
    EXPECTED_COST = "expected cost"
    ACTUAL_COST = "actual cost"
    FUNDING_ALLOCATION = "funding allocation"
    SPENT_TO_DATE = "spent to date"
    FUNDING_REQUEST = "funding request"

    def to_domain(self) -> FinancialType:
        return {
            FinancialTypeRepr.EXPECTED_COST: FinancialType.EXPECTED_COST,
            FinancialTypeRepr.ACTUAL_COST: FinancialType.ACTUAL_COST,
            FinancialTypeRepr.FUNDING_ALLOCATION: FinancialType.FUNDING_ALLOCATION,
            FinancialTypeRepr.SPENT_TO_DATE: FinancialType.SPENT_TO_DATE,
            FinancialTypeRepr.FUNDING_REQUEST: FinancialType.FUNDING_REQUEST,
        }[self]


@unique
class DataSourceRepr(Enum):
    PULSE_5 = "Pulse 5"
    PULSE_6 = "Pulse 6"
    ATF4_BID = "ATF4 Bid"
    ATF3_BID = "ATF3 Bid"
    INSPECTORATE_REVIEW = "Inspectorate review"
    REGIONAL_ENGAGEMENT_MANAGER_REVIEW = "Regional Engagement Manager review"
    ATE_PUBLISHED_DATA = "ATE published data"
    CHANGE_CONTROL = "change control"
    ATF4E_BID = "ATF4e Bid"
    PULSE_2023_24_Q2 = "Pulse 2023/24 Q2"
    INITIAL_SCHEME_LIST = "Initial Scheme List"

    def to_domain(self) -> DataSource:
        return {
            DataSourceRepr.PULSE_5: DataSource.PULSE_5,
            DataSourceRepr.PULSE_6: DataSource.PULSE_6,
            DataSourceRepr.ATF4_BID: DataSource.ATF4_BID,
            DataSourceRepr.ATF3_BID: DataSource.ATF3_BID,
            DataSourceRepr.INSPECTORATE_REVIEW: DataSource.INSPECTORATE_REVIEW,
            DataSourceRepr.REGIONAL_ENGAGEMENT_MANAGER_REVIEW: DataSource.REGIONAL_ENGAGEMENT_MANAGER_REVIEW,
            DataSourceRepr.ATE_PUBLISHED_DATA: DataSource.ATE_PUBLISHED_DATA,
            DataSourceRepr.CHANGE_CONTROL: DataSource.CHANGE_CONTROL,
            DataSourceRepr.ATF4E_BID: DataSource.ATF4E_BID,
            DataSourceRepr.PULSE_2023_24_Q2: DataSource.PULSE_2023_24_Q2,
            DataSourceRepr.INITIAL_SCHEME_LIST: DataSource.INITIAL_SCHEME_LIST,
        }[self]


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
        return {
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
        }[self]


@unique
class ObservationTypeRepr(Enum):
    PLANNED = "Planned"
    ACTUAL = "Actual"

    def to_domain(self) -> ObservationType:
        return {
            ObservationTypeRepr.PLANNED: ObservationType.PLANNED,
            ObservationTypeRepr.ACTUAL: ObservationType.ACTUAL,
        }[self]
