from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, unique

import dataclass_wizard
import inject
from flask import (
    Blueprint,
    Response,
    abort,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
)
from werkzeug import Response as BaseResponse

from schemes.dicts import as_shallow_dict, inverse_dict
from schemes.domain.authorities import Authority, AuthorityRepository
from schemes.domain.schemes import (
    FundingProgramme,
    Scheme,
    SchemeRepository,
    SchemeType,
)
from schemes.domain.users import User
from schemes.infrastructure.clock import Clock
from schemes.views.auth.api_key import api_key_auth
from schemes.views.auth.bearer import bearer_auth
from schemes.views.schemes.funding import (
    FinancialRevisionRepr,
    SchemeChangeSpendToDateContext,
    SchemeFundingContext,
)
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
def index(user: User, authorities: AuthorityRepository, schemes: SchemeRepository) -> str:
    authority = authorities.get(user.authority_id)
    assert authority
    authority_schemes = schemes.get_by_authority(authority.id)

    context = SchemesContext.from_domain(authority, authority_schemes)
    return render_template("schemes.html", **as_shallow_dict(context))


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
def get(scheme_id: int) -> Response:
    json = request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html
    return get_json(scheme_id) if json else get_html(scheme_id)


@bearer_auth
@inject.autoparams("user", "authorities", "schemes")
def get_html(scheme_id: int, user: User, authorities: AuthorityRepository, schemes: SchemeRepository) -> Response:
    authority = authorities.get(user.authority_id)
    assert authority
    scheme = schemes.get(scheme_id)
    assert scheme

    if user.authority_id != scheme.authority_id:
        abort(403)

    context = SchemeContext.from_domain(authority, scheme)
    return Response(render_template("scheme/index.html", **as_shallow_dict(context)))


@api_key_auth
@inject.autoparams("schemes")
def get_json(scheme_id: int, schemes: SchemeRepository) -> Response:
    scheme = schemes.get(scheme_id)
    assert scheme

    response = make_response(dataclass_wizard.asdict(SchemeRepr.from_domain(scheme)))
    response.content_type = "application/json"
    return response


@dataclass(frozen=True)
class SchemeContext:
    id: int
    authority_name: str
    name: str
    overview: SchemeOverviewContext
    funding: SchemeFundingContext
    milestones: SchemeMilestonesContext
    outputs: SchemeOutputsContext

    @classmethod
    def from_domain(cls, authority: Authority, scheme: Scheme) -> SchemeContext:
        return cls(
            id=scheme.id,
            authority_name=authority.name,
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


@bp.get("<int:scheme_id>/spend-to-date")
@bearer_auth
@inject.autoparams("user", "schemes")
def spend_to_date_form(user: User, schemes: SchemeRepository, scheme_id: int) -> str:
    scheme = schemes.get(scheme_id)
    assert scheme

    if user.authority_id != scheme.authority_id:
        abort(403)

    context = SchemeChangeSpendToDateContext.from_domain(scheme)
    return render_template("scheme/spend_to_date.html", **as_shallow_dict(context))


@bp.post("<int:scheme_id>/spend-to-date")
@bearer_auth
@inject.autoparams("clock", "user", "schemes")
def spend_to_date(clock: Clock, user: User, schemes: SchemeRepository, scheme_id: int) -> BaseResponse:
    scheme = schemes.get(scheme_id)
    assert scheme

    if user.authority_id != scheme.authority_id:
        abort(403)

    context = SchemeChangeSpendToDateContext.from_domain(scheme)
    context.form.process(formdata=request.form)

    if not context.form.validate():
        return Response(render_template("scheme/spend_to_date.html", **as_shallow_dict(context)))

    context.form.update_domain(scheme.funding, clock.now)
    schemes.update(scheme)

    return redirect(url_for("schemes.get", scheme_id=scheme_id))


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

    @classmethod
    def from_domain(cls, scheme: Scheme) -> SchemeRepr:
        return cls(
            id=scheme.id,
            name=scheme.name,
            type=SchemeTypeRepr.from_domain(scheme.type) if scheme.type else None,
            funding_programme=(
                FundingProgrammeRepr.from_domain(scheme.funding_programme) if scheme.funding_programme else None
            ),
            financial_revisions=[
                FinancialRevisionRepr.from_domain(financial_revision)
                for financial_revision in scheme.funding.financial_revisions
            ],
            milestone_revisions=[
                MilestoneRevisionRepr.from_domain(milestone_revision)
                for milestone_revision in scheme.milestones.milestone_revisions
            ],
            output_revisions=[
                OutputRevisionRepr.from_domain(output_revision) for output_revision in scheme.outputs.output_revisions
            ],
        )

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

    @classmethod
    def from_domain(cls, type_: SchemeType) -> SchemeTypeRepr:
        return cls._members()[type_]

    def to_domain(self) -> SchemeType:
        return inverse_dict(self._members())[self]

    @staticmethod
    def _members() -> dict[SchemeType, SchemeTypeRepr]:
        return {
            SchemeType.DEVELOPMENT: SchemeTypeRepr.DEVELOPMENT,
            SchemeType.CONSTRUCTION: SchemeTypeRepr.CONSTRUCTION,
        }


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

    @classmethod
    def from_domain(cls, funding_programme: FundingProgramme) -> FundingProgrammeRepr:
        return cls._members()[funding_programme]

    def to_domain(self) -> FundingProgramme:
        return inverse_dict(self._members())[self]

    @staticmethod
    def _members() -> dict[FundingProgramme, FundingProgrammeRepr]:
        return {
            FundingProgramme.ATF2: FundingProgrammeRepr.ATF2,
            FundingProgramme.ATF3: FundingProgrammeRepr.ATF3,
            FundingProgramme.ATF4: FundingProgrammeRepr.ATF4,
            FundingProgramme.ATF4E: FundingProgrammeRepr.ATF4E,
            FundingProgramme.ATF5: FundingProgrammeRepr.ATF5,
            FundingProgramme.MRN: FundingProgrammeRepr.MRN,
            FundingProgramme.LUF: FundingProgrammeRepr.LUF,
            FundingProgramme.CRSTS: FundingProgrammeRepr.CRSTS,
        }
