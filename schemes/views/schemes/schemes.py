from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, unique

import dataclass_wizard
import inject
from dataclass_wizard import fromlist
from dataclass_wizard.errors import UnknownJSONKey
from flask import (
    Blueprint,
    Response,
    abort,
    current_app,
    flash,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug import Response as BaseResponse

from schemes.dicts import as_shallow_dict, inverse_dict
from schemes.domain.authorities import Authority, AuthorityRepository
from schemes.domain.reporting_window import ReportingWindow, ReportingWindowService
from schemes.domain.schemes import (
    FundingProgramme,
    FundingProgrammes,
    Scheme,
    SchemeRepository,
    SchemeType,
)
from schemes.domain.users import UserRepository
from schemes.infrastructure.clock import Clock
from schemes.views.auth.api_key import api_key_auth
from schemes.views.auth.bearer import bearer_auth
from schemes.views.schemes.funding import (
    BidStatusRevisionRepr,
    ChangeSpendToDateContext,
    ChangeSpendToDateForm,
    FinancialRevisionRepr,
    SchemeFundingContext,
)
from schemes.views.schemes.milestones import (
    ChangeMilestoneDatesContext,
    ChangeMilestoneDatesForm,
    MilestoneContext,
    MilestoneRevisionRepr,
    SchemeMilestonesContext,
)
from schemes.views.schemes.outputs import OutputRevisionRepr, SchemeOutputsContext
from schemes.views.schemes.overview import OverviewRevisionRepr
from schemes.views.schemes.reviews import (
    AuthorityReviewRepr,
    SchemeReviewContext,
    SchemeReviewForm,
)

bp = Blueprint("schemes", __name__)


@bp.post("")
@api_key_auth
@inject.autoparams("schemes")
def add_schemes(schemes: SchemeRepository) -> Response:
    try:
        schemes_repr = fromlist(SchemeRepr, request.get_json())
    except UnknownJSONKey as error:
        current_app.logger.error(error)
        return Response(status=400)

    schemes.add(*[scheme_repr.to_domain() for scheme_repr in schemes_repr])
    return Response(status=201)


@bp.get("")
@bearer_auth
@inject.autoparams()
def index(
    clock: Clock,
    users: UserRepository,
    reporting_window_service: ReportingWindowService,
    authorities: AuthorityRepository,
    schemes: SchemeRepository,
) -> str:
    user_info = session["user"]
    user = users.get_by_email(user_info["email"])
    assert user
    now = clock.now
    reporting_window = reporting_window_service.get_by_date(now)
    authority = authorities.get(user.authority_id)
    assert authority
    authority_schemes = [scheme for scheme in schemes.get_by_authority(authority.id) if scheme.is_updateable]

    context = SchemesContext.from_domain(now, reporting_window, authority, authority_schemes)
    return render_template("schemes.html", **as_shallow_dict(context))


@dataclass(frozen=True)
class SchemesContext:
    reporting_window_days_left: int | None
    authority_name: str
    schemes: list[SchemeRowContext]

    @classmethod
    def from_domain(
        cls, now: datetime, reporting_window: ReportingWindow, authority: Authority, schemes: list[Scheme]
    ) -> SchemesContext:
        needs_review = any(scheme.reviews.needs_review(reporting_window) for scheme in schemes)
        return cls(
            reporting_window_days_left=reporting_window.days_left(now) if needs_review else None,
            authority_name=authority.name,
            schemes=[SchemeRowContext.from_domain(reporting_window, scheme) for scheme in schemes],
        )


@dataclass(frozen=True)
class SchemeRowContext:
    id: int
    reference: str
    funding_programme: FundingProgrammeContext
    name: str
    needs_review: bool
    last_reviewed: datetime | None

    @classmethod
    def from_domain(cls, reporting_window: ReportingWindow, scheme: Scheme) -> SchemeRowContext:
        name = scheme.overview.name
        assert name is not None

        return cls(
            id=scheme.id,
            reference=scheme.reference,
            funding_programme=FundingProgrammeContext.from_domain(scheme.funding_programme),
            name=name,
            needs_review=scheme.reviews.needs_review(reporting_window),
            last_reviewed=scheme.reviews.last_reviewed,
        )


@bp.get("<int:scheme_id>")
def get(scheme_id: int) -> Response:
    json = request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html
    return get_json(scheme_id) if json else get_html(scheme_id)


@bearer_auth
@inject.autoparams("clock", "reporting_window_service", "users", "authorities", "schemes")
def get_html(
    scheme_id: int,
    clock: Clock,
    reporting_window_service: ReportingWindowService,
    users: UserRepository,
    authorities: AuthorityRepository,
    schemes: SchemeRepository,
) -> Response:
    user_info = session["user"]
    user = users.get_by_email(user_info["email"])
    assert user
    now = clock.now
    reporting_window = reporting_window_service.get_by_date(now)
    authority = authorities.get(user.authority_id)
    assert authority
    scheme = schemes.get(scheme_id)

    if not (scheme and scheme.is_updateable):
        abort(404)

    if user.authority_id != scheme.overview.authority_id:
        abort(403)

    context = SchemeContext.from_domain(reporting_window, authority, scheme)
    context.review.form.validate_on_submit()
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
    needs_review: bool
    overview: SchemeOverviewContext
    funding: SchemeFundingContext
    milestones: SchemeMilestonesContext
    outputs: SchemeOutputsContext
    review: SchemeReviewContext

    @classmethod
    def from_domain(cls, reporting_window: ReportingWindow, authority: Authority, scheme: Scheme) -> SchemeContext:
        name = scheme.overview.name
        assert name is not None

        return cls(
            id=scheme.id,
            authority_name=authority.name,
            name=name,
            needs_review=scheme.reviews.needs_review(reporting_window),
            overview=SchemeOverviewContext.from_domain(scheme),
            funding=SchemeFundingContext.from_domain(scheme.funding),
            milestones=SchemeMilestonesContext.from_domain(scheme.milestones),
            outputs=SchemeOutputsContext.from_domain(scheme.outputs.current_output_revisions),
            review=SchemeReviewContext.from_domain(scheme.reviews),
        )


@dataclass(frozen=True)
class SchemeOverviewContext:
    reference: str
    type: SchemeTypeContext
    funding_programme: FundingProgrammeContext
    current_milestone: MilestoneContext

    @classmethod
    def from_domain(cls, scheme: Scheme) -> SchemeOverviewContext:
        type_ = scheme.overview.type
        assert type_

        return cls(
            reference=scheme.reference,
            type=SchemeTypeContext.from_domain(type_),
            funding_programme=FundingProgrammeContext.from_domain(scheme.funding_programme),
            current_milestone=MilestoneContext.from_domain(scheme.milestones.current_milestone),
        )


@dataclass(frozen=True)
class SchemeTypeContext:
    name: str
    _NAMES = {
        SchemeType.DEVELOPMENT: "Development",
        SchemeType.CONSTRUCTION: "Construction",
    }

    @classmethod
    def from_domain(cls, type_: SchemeType) -> SchemeTypeContext:
        return cls(name=cls._NAMES[type_])


@dataclass(frozen=True)
class FundingProgrammeContext:
    name: str
    _NAMES = {
        FundingProgrammes.ATF2: "ATF2",
        FundingProgrammes.ATF3: "ATF3",
        FundingProgrammes.ATF4: "ATF4",
        FundingProgrammes.ATF4E: "ATF4e",
    }

    @classmethod
    def from_domain(cls, funding_programme: FundingProgramme) -> FundingProgrammeContext:
        return cls(name=cls._NAMES[funding_programme])


@bp.get("<int:scheme_id>/spend-to-date")
@bearer_auth
@inject.autoparams("users", "schemes")
def spend_to_date_form(scheme_id: int, users: UserRepository, schemes: SchemeRepository) -> str:
    user_info = session["user"]
    user = users.get_by_email(user_info["email"])
    assert user
    scheme = schemes.get(scheme_id)

    if not (scheme and scheme.is_updateable):
        abort(404)

    if user.authority_id != scheme.overview.authority_id:
        abort(403)

    context = ChangeSpendToDateContext.from_domain(scheme)
    context.form.validate_on_submit()
    return render_template("scheme/spend_to_date.html", **as_shallow_dict(context))


@bp.post("<int:scheme_id>/spend-to-date")
@bearer_auth
@inject.autoparams("clock", "users", "schemes")
def spend_to_date(clock: Clock, users: UserRepository, schemes: SchemeRepository, scheme_id: int) -> BaseResponse:
    user_info = session["user"]
    user = users.get_by_email(user_info["email"])
    assert user
    scheme = schemes.get(scheme_id)

    if not (scheme and scheme.is_updateable):
        abort(404)

    if user.authority_id != scheme.overview.authority_id:
        abort(403)

    form = ChangeSpendToDateForm.from_domain(scheme.funding)

    if not form.validate():
        return spend_to_date_form(scheme_id)

    form.update_domain(scheme.funding, clock.now)
    schemes.update(scheme)

    return redirect(url_for("schemes.get", scheme_id=scheme_id))


@bp.get("<int:scheme_id>/milestones")
@bearer_auth
@inject.autoparams("users", "schemes")
def milestones_form(scheme_id: int, users: UserRepository, schemes: SchemeRepository) -> str:
    user_info = session["user"]
    user = users.get_by_email(user_info["email"])
    assert user
    scheme = schemes.get(scheme_id)

    if not (scheme and scheme.is_updateable):
        abort(404)

    if user.authority_id != scheme.overview.authority_id:
        abort(403)

    context = ChangeMilestoneDatesContext.from_domain(scheme)
    context.form.validate_on_submit()
    return render_template("scheme/milestones.html", **as_shallow_dict(context))


@bp.post("<int:scheme_id>/milestones")
@bearer_auth
@inject.autoparams("clock", "users", "schemes")
def milestones(clock: Clock, users: UserRepository, schemes: SchemeRepository, scheme_id: int) -> BaseResponse:
    user_info = session["user"]
    user = users.get_by_email(user_info["email"])
    assert user
    scheme = schemes.get(scheme_id)

    if not (scheme and scheme.is_updateable):
        abort(404)

    if user.authority_id != scheme.overview.authority_id:
        abort(403)

    form = ChangeMilestoneDatesForm.from_domain(scheme.milestones)

    if not form.validate():
        return milestones_form(scheme_id)

    form.update_domain(scheme.milestones, clock.now)
    schemes.update(scheme)

    return redirect(url_for("schemes.get", scheme_id=scheme_id))


@bp.post("<int:scheme_id>")
@bearer_auth
@inject.autoparams("clock", "users", "schemes")
def review(clock: Clock, users: UserRepository, schemes: SchemeRepository, scheme_id: int) -> BaseResponse:
    user_info = session["user"]
    user = users.get_by_email(user_info["email"])
    assert user
    scheme = schemes.get(scheme_id)

    if not (scheme and scheme.is_updateable):
        abort(404)

    if user.authority_id != scheme.overview.authority_id:
        abort(403)

    form = SchemeReviewForm()

    if not form.validate():
        return get(scheme_id)

    form.update_domain(scheme.reviews, clock.now)
    schemes.update(scheme)

    flash(f"{scheme.overview.name} has been reviewed")
    return redirect(url_for("schemes.index"))


@bp.delete("")
@api_key_auth
@inject.autoparams()
def clear(schemes: SchemeRepository) -> Response:
    schemes.clear()
    return Response(status=204)


@dataclass(frozen=True)
class SchemeRepr:
    id: int
    funding_programme: FundingProgrammeRepr
    overview_revisions: list[OverviewRevisionRepr] = field(default_factory=list)
    bid_status_revisions: list[BidStatusRevisionRepr] = field(default_factory=list)
    financial_revisions: list[FinancialRevisionRepr] = field(default_factory=list)
    milestone_revisions: list[MilestoneRevisionRepr] = field(default_factory=list)
    output_revisions: list[OutputRevisionRepr] = field(default_factory=list)
    authority_reviews: list[AuthorityReviewRepr] = field(default_factory=list)

    @classmethod
    def from_domain(cls, scheme: Scheme) -> SchemeRepr:
        return cls(
            id=scheme.id,
            funding_programme=FundingProgrammeRepr.from_domain(scheme.funding_programme),
            overview_revisions=[
                OverviewRevisionRepr.from_domain(overview_revision)
                for overview_revision in scheme.overview.overview_revisions
            ],
            bid_status_revisions=[
                BidStatusRevisionRepr.from_domain(bid_status_revision)
                for bid_status_revision in scheme.funding.bid_status_revisions
            ],
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
            authority_reviews=[
                AuthorityReviewRepr.from_domain(authority_review)
                for authority_review in scheme.reviews.authority_reviews
            ],
        )

    def to_domain(self) -> Scheme:
        scheme = Scheme(id_=self.id, funding_programme=self.funding_programme.to_domain())

        for overview_revision_repr in self.overview_revisions:
            scheme.overview.update_overviews(overview_revision_repr.to_domain())

        for bid_status_revision_repr in self.bid_status_revisions:
            scheme.funding.update_bid_status(bid_status_revision_repr.to_domain())

        for financial_revision_repr in self.financial_revisions:
            scheme.funding.update_financial(financial_revision_repr.to_domain())

        for milestone_revision_repr in self.milestone_revisions:
            scheme.milestones.update_milestone(milestone_revision_repr.to_domain())

        for output_revision_repr in self.output_revisions:
            scheme.outputs.update_output(output_revision_repr.to_domain())

        for authority_review_repr in self.authority_reviews:
            scheme.reviews.update_authority_review(authority_review_repr.to_domain())

        return scheme


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
            FundingProgrammes.ATF2: FundingProgrammeRepr.ATF2,
            FundingProgrammes.ATF3: FundingProgrammeRepr.ATF3,
            FundingProgrammes.ATF4: FundingProgrammeRepr.ATF4,
            FundingProgrammes.ATF4E: FundingProgrammeRepr.ATF4E,
        }
