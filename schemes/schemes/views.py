from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date

import inject
from flask import Blueprint, Response, render_template, session

from schemes.auth.api_key import api_key_auth
from schemes.auth.bearer import bearer_auth
from schemes.authorities.domain import Authority
from schemes.authorities.services import AuthorityRepository
from schemes.schemes.domain import (
    FundingProgramme,
    Milestone,
    MilestoneRevision,
    ObservationType,
    Scheme,
    SchemeType,
)
from schemes.schemes.services import SchemeRepository
from schemes.users.services import UserRepository

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
    name: str

    @staticmethod
    def for_domain(scheme: Scheme) -> SchemeRowContext:
        return SchemeRowContext(
            id=scheme.id,
            reference=scheme.reference,
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
    reference: str
    overview: SchemeOverviewContext

    @staticmethod
    def for_domain(scheme: Scheme) -> SchemeContext:
        return SchemeContext(
            name=scheme.name, reference=scheme.reference, overview=SchemeOverviewContext.for_domain(scheme)
        )


@dataclass(frozen=True)
class SchemeOverviewContext:
    type: str | None = None
    funding_programme: str | None = None
    current_milestone: str | None = None

    @staticmethod
    def for_domain(scheme: Scheme) -> SchemeOverviewContext:
        return SchemeOverviewContext(
            type=SchemeOverviewContext._type_to_name(scheme.type) if scheme.type else None,
            funding_programme=SchemeOverviewContext._funding_programme_to_name(scheme.funding_programme)
            if scheme.funding_programme
            else None,
            current_milestone=SchemeOverviewContext._milestone_to_name(scheme.current_milestone)
            if scheme.current_milestone
            else None,
        )

    @staticmethod
    def _type_to_name(type_: SchemeType) -> str:
        return {
            SchemeType.DEVELOPMENT: "Development",
            SchemeType.CONSTRUCTION: "Construction",
        }[type_]

    @staticmethod
    def _funding_programme_to_name(funding_programme: FundingProgramme) -> str:
        return {
            FundingProgramme.ATF2: "ATF2",
            FundingProgramme.ATF3: "ATF3",
            FundingProgramme.ATF4: "ATF4",
            FundingProgramme.ATF4E: "ATF4e",
            FundingProgramme.ATF5: "ATF5",
            FundingProgramme.MRN: "MRN",
            FundingProgramme.LUF: "LUF",
            FundingProgramme.CRSTS: "CRSTS",
        }[funding_programme]

    @staticmethod
    def _milestone_to_name(milestone: Milestone) -> str:
        return {
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
        }[milestone]


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

    def to_domain(self, authority_id: int) -> Scheme:
        scheme = Scheme(id_=self.id, name=self.name, authority_id=authority_id)
        scheme.type = self._type_to_domain(self.type) if self.type else None
        scheme.funding_programme = (
            self._funding_programme_to_domain(self.funding_programme) if self.funding_programme else None
        )
        for milestone_revision_repr in self.milestone_revisions:
            scheme.update_milestone(milestone_revision_repr.to_domain())
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
            effective_date_from=date.fromisoformat(self.effective_date_from),
            effective_date_to=date.fromisoformat(self.effective_date_to) if self.effective_date_to else None,
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
