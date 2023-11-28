from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date
from decimal import Decimal

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

    @staticmethod
    def for_domain(scheme: Scheme) -> SchemeContext:
        return SchemeContext(
            name=scheme.name,
            overview=SchemeOverviewContext.for_domain(scheme),
            funding=SchemeFundingContext.for_domain(scheme),
        )


@dataclass(frozen=True)
class SchemeOverviewContext:
    reference: str
    type: str | None
    funding_programme: FundingProgrammeContext
    current_milestone: MilestoneContext

    @staticmethod
    def for_domain(scheme: Scheme) -> SchemeOverviewContext:
        return SchemeOverviewContext(
            reference=scheme.reference,
            type=SchemeOverviewContext._type_to_name(scheme.type),
            funding_programme=FundingProgrammeContext.for_domain(scheme.funding_programme),
            current_milestone=MilestoneContext.for_domain(scheme.current_milestone),
        )

    @staticmethod
    def _type_to_name(type_: SchemeType | None) -> str | None:
        type_names = {
            SchemeType.DEVELOPMENT: "Development",
            SchemeType.CONSTRUCTION: "Construction",
        }
        return type_names[type_] if type_ else None


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
    def for_domain(scheme: Scheme) -> SchemeFundingContext:
        return SchemeFundingContext(
            funding_allocation=scheme.funding_allocation,
            spend_to_date=scheme.spend_to_date,
            change_control_adjustment=scheme.change_control_adjustment,
            allocation_still_to_spend=scheme.allocation_still_to_spend,
        )


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
    type: str | None = None
    funding_programme: str | None = None
    milestone_revisions: list[MilestoneRevisionRepr] = field(default_factory=list)
    financial_revisions: list[FinancialRevisionRepr] = field(default_factory=list)

    def to_domain(self, authority_id: int) -> Scheme:
        scheme = Scheme(id_=self.id, name=self.name, authority_id=authority_id)
        scheme.type = self._type_to_domain(self.type) if self.type else None
        scheme.funding_programme = (
            self._funding_programme_to_domain(self.funding_programme) if self.funding_programme else None
        )
        for milestone_revision_repr in self.milestone_revisions:
            scheme.update_milestone(milestone_revision_repr.to_domain())

        for financial_revision_repr in self.financial_revisions:
            scheme.update_financial(financial_revision_repr.to_domain())
        return scheme

    @staticmethod
    def _type_to_domain(type_: str) -> SchemeType:
        return {
            "development": SchemeType.DEVELOPMENT,
            "construction": SchemeType.CONSTRUCTION,
        }[type_]

    @staticmethod
    def _funding_programme_to_domain(funding_programme: str) -> FundingProgramme:
        return {
            "ATF2": FundingProgramme.ATF2,
            "ATF3": FundingProgramme.ATF3,
            "ATF4": FundingProgramme.ATF4,
            "ATF4e": FundingProgramme.ATF4E,
            "ATF5": FundingProgramme.ATF5,
            "MRN": FundingProgramme.MRN,
            "LUF": FundingProgramme.LUF,
            "CRSTS": FundingProgramme.CRSTS,
        }[funding_programme]


@dataclass(frozen=True)
class MilestoneRevisionRepr:
    effective_date_from: str
    effective_date_to: str | None
    milestone: str
    observation_type: str
    status_date: str

    def to_domain(self) -> MilestoneRevision:
        return MilestoneRevision(
            effective=DateRange(
                date_from=date.fromisoformat(self.effective_date_from),
                date_to=date.fromisoformat(self.effective_date_to) if self.effective_date_to else None,
            ),
            milestone=self._milestone_to_domain(self.milestone),
            observation_type=self._observation_type_to_domain(self.observation_type),
            status_date=date.fromisoformat(self.status_date),
        )

    @staticmethod
    def _milestone_to_domain(milestone: str) -> Milestone:
        return {
            "public consultation completed": Milestone.PUBLIC_CONSULTATION_COMPLETED,
            "feasibility design completed": Milestone.FEASIBILITY_DESIGN_COMPLETED,
            "preliminary design completed": Milestone.PRELIMINARY_DESIGN_COMPLETED,
            "outline design completed": Milestone.OUTLINE_DESIGN_COMPLETED,
            "detailed design completed": Milestone.DETAILED_DESIGN_COMPLETED,
            "construction started": Milestone.CONSTRUCTION_STARTED,
            "construction completed": Milestone.CONSTRUCTION_COMPLETED,
            "inspection": Milestone.INSPECTION,
            "not progressed": Milestone.NOT_PROGRESSED,
            "superseded": Milestone.SUPERSEDED,
            "removed": Milestone.REMOVED,
        }[milestone]

    @staticmethod
    def _observation_type_to_domain(observation_type: str) -> ObservationType:
        return {
            "Planned": ObservationType.PLANNED,
            "Actual": ObservationType.ACTUAL,
        }[observation_type]


@dataclass(frozen=True)
class FinancialRevisionRepr:
    effective_date_from: str
    effective_date_to: str | None
    type: str
    amount: str
    source: str

    def to_domain(self) -> FinancialRevision:
        return FinancialRevision(
            effective=DateRange(
                date_from=date.fromisoformat(self.effective_date_from),
                date_to=date.fromisoformat(self.effective_date_to) if self.effective_date_to else None,
            ),
            type=self._financial_type_to_domain(self.type),
            amount=Decimal(self.amount),
            source=self._data_source_to_domain(self.source),
        )

    @staticmethod
    def _financial_type_to_domain(financial_type: str) -> FinancialType:
        return {
            "expected cost": FinancialType.EXPECTED_COST,
            "actual cost": FinancialType.ACTUAL_COST,
            "funding allocation": FinancialType.FUNDING_ALLOCATION,
            "spent to date": FinancialType.SPENT_TO_DATE,
            "funding request": FinancialType.FUNDING_REQUEST,
        }[financial_type]

    @staticmethod
    def _data_source_to_domain(data_source: str) -> DataSource:
        return {
            "Pulse 5": DataSource.PULSE_5,
            "Pulse 6": DataSource.PULSE_6,
            "ATF4 Bid": DataSource.ATF4_BID,
            "ATF3 Bid": DataSource.ATF3_BID,
            "Inspectorate review": DataSource.INSPECTORATE_REVIEW,
            "Regional Engagement Manager review": DataSource.REGIONAL_ENGAGEMENT_MANAGER_REVIEW,
            "ATE published data": DataSource.ATE_PUBLISHED_DATA,
            "change control": DataSource.CHANGE_CONTROL,
            "ATF4e Bid": DataSource.ATF4E_BID,
            "Pulse 2023/24 Q2": DataSource.PULSE_2023_24_Q2,
            "Initial Scheme List": DataSource.INITIAL_SCHEME_LIST,
        }[data_source]
