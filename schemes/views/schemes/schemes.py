from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum, unique

import inject
from flask import Blueprint, Response, render_template, session

from schemes.domain.authorities import Authority, AuthorityRepository
from schemes.domain.schemes import (
    FundingProgramme,
    Scheme,
    SchemeRepository,
    SchemeType,
)
from schemes.domain.users import UserRepository
from schemes.views.auth.api_key import api_key_auth
from schemes.views.auth.bearer import bearer_auth
from schemes.views.schemes.funding import FinancialRevisionRepr, SchemeFundingContext
from schemes.views.schemes.milestones import (
    MilestoneContext,
    MilestoneRevisionRepr,
    SchemeMilestonesContext,
)
from schemes.views.schemes.outputs import OutputRevisionRepr, SchemeOutputsContext

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
    return render_template("scheme.html", **asdict(context))


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
