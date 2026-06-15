from dataclasses import dataclass
from datetime import datetime
from typing import Self

import inject
from flask import Blueprint, Response, abort, flash, redirect, render_template, session, url_for
from werkzeug import Response as BaseResponse

from schemes.dicts import as_shallow_dict
from schemes.domain.authorities import Authority, AuthorityRepository
from schemes.domain.reporting_window import ReportingWindow, ReportingWindowService
from schemes.domain.schemes.overview import FundingProgramme, FundingProgrammes, SchemeType
from schemes.domain.schemes.schemes import Scheme, SchemeRepository
from schemes.domain.users import UserRepository
from schemes.infrastructure.clock import Clock
from schemes.views.auth.bearer import async_bearer_auth
from schemes.views.schemes.funding import (
    ChangeSpendToDateContext,
    ChangeSpendToDateForm,
    SchemeFundingContext,
)
from schemes.views.schemes.milestones import (
    ChangeMilestoneDatesContext,
    ChangeMilestoneDatesForm,
    MilestoneContext,
    SchemeMilestonesContext,
)
from schemes.views.schemes.outputs import SchemeOutputsContext
from schemes.views.schemes.reviews import SchemeReviewContext, SchemeReviewForm

bp = Blueprint("schemes", __name__)


@bp.get("")
@async_bearer_auth
@inject.autoparams()
async def index(
    clock: Clock,
    users: UserRepository,
    reporting_window_service: ReportingWindowService,
    authorities: AuthorityRepository,
    schemes: SchemeRepository,
) -> str:
    user_info = session["user"]
    user = users.get(user_info["email"])
    assert user
    now = clock.now
    reporting_window = reporting_window_service.get_by_date(now)
    authority = await authorities.get(user.authority_abbreviation)
    assert authority
    authority_schemes = [
        scheme for scheme in await schemes.get_by_authority(authority.abbreviation) if scheme.is_updateable
    ]

    context = SchemesContext.from_domain(now, reporting_window, authority, authority_schemes)
    return render_template("schemes.html", **as_shallow_dict(context))


@dataclass(frozen=True)
class FundingProgrammeContext:
    name: str
    _NAMES = {
        FundingProgrammes.ATF2: "ATF2",
        FundingProgrammes.ATF3: "ATF3",
        FundingProgrammes.ATF4: "ATF4",
        FundingProgrammes.ATF4E: "ATF4e",
        FundingProgrammes.ATF5: "ATF5",
        FundingProgrammes.CATF: "CATF",
        FundingProgrammes.CRSTS: "CRSTS",
        FundingProgrammes.IST: "IST",
        FundingProgrammes.LUF1: "LUF1",
        FundingProgrammes.LUF2: "LUF2",
        FundingProgrammes.LUF3: "LUF3",
        FundingProgrammes.MRN: "MRN",
        FundingProgrammes.OTH: "OTH",
        FundingProgrammes.CON: "CON",
    }

    @classmethod
    def from_domain(cls, funding_programme: FundingProgramme) -> Self:
        return cls(name=cls._NAMES[funding_programme])


@dataclass(frozen=True)
class SchemeRowContext:
    reference: str
    funding_programme: FundingProgrammeContext
    name: str
    needs_review: bool
    last_reviewed: datetime | None

    @classmethod
    def from_domain(cls, reporting_window: ReportingWindow, scheme: Scheme) -> Self:
        funding_programme = scheme.overview.funding_programme
        assert funding_programme
        name = scheme.overview.name
        assert name is not None

        return cls(
            reference=scheme.reference,
            funding_programme=FundingProgrammeContext.from_domain(funding_programme),
            name=name,
            needs_review=scheme.reviews.needs_review(reporting_window),
            last_reviewed=scheme.reviews.last_reviewed,
        )


@dataclass(frozen=True)
class SchemesContext:
    reporting_window_days_left: int | None
    authority_name: str
    schemes: list[SchemeRowContext]

    @classmethod
    def from_domain(
        cls, now: datetime, reporting_window: ReportingWindow, authority: Authority, schemes: list[Scheme]
    ) -> Self:
        needs_review = any(scheme.reviews.needs_review(reporting_window) for scheme in schemes)
        return cls(
            reporting_window_days_left=reporting_window.days_left(now) if needs_review else None,
            authority_name=authority.name,
            schemes=[SchemeRowContext.from_domain(reporting_window, scheme) for scheme in schemes],
        )


@bp.get("<reference>")
@async_bearer_auth
@inject.autoparams()
async def get(
    reference: str,
    clock: Clock,
    reporting_window_service: ReportingWindowService,
    users: UserRepository,
    authorities: AuthorityRepository,
    schemes: SchemeRepository,
) -> Response:
    user_info = session["user"]
    user = users.get(user_info["email"])
    assert user
    now = clock.now
    reporting_window = reporting_window_service.get_by_date(now)
    authority = await authorities.get(user.authority_abbreviation)
    assert authority
    scheme = await schemes.get(reference)

    if not (scheme and scheme.is_updateable):
        abort(404)

    if user.authority_abbreviation != scheme.overview.authority_abbreviation:
        abort(403)

    context = SchemeContext.from_domain(reporting_window, authority, scheme)
    context.review.form.validate_on_submit()
    return Response(render_template("scheme/index.html", **as_shallow_dict(context)))


@dataclass(frozen=True)
class SchemeTypeContext:
    name: str
    _NAMES = {
        SchemeType.DEVELOPMENT: "Development",
        SchemeType.CONSTRUCTION: "Construction",
    }

    @classmethod
    def from_domain(cls, type_: SchemeType) -> Self:
        return cls(name=cls._NAMES[type_])


@dataclass(frozen=True)
class SchemeOverviewContext:
    reference: str
    type: SchemeTypeContext
    funding_programme: FundingProgrammeContext
    current_milestone: MilestoneContext

    @classmethod
    def from_domain(cls, scheme: Scheme) -> Self:
        type_ = scheme.overview.type
        assert type_
        funding_programme = scheme.overview.funding_programme
        assert funding_programme

        return cls(
            reference=scheme.reference,
            type=SchemeTypeContext.from_domain(type_),
            funding_programme=FundingProgrammeContext.from_domain(funding_programme),
            current_milestone=MilestoneContext.from_domain(scheme.milestones.current_milestone),
        )


@dataclass(frozen=True)
class SchemeContext:
    reference: str
    authority_name: str
    name: str
    needs_review: bool
    overview: SchemeOverviewContext
    funding: SchemeFundingContext
    milestones: SchemeMilestonesContext
    outputs: SchemeOutputsContext
    review: SchemeReviewContext

    @classmethod
    def from_domain(cls, reporting_window: ReportingWindow, authority: Authority, scheme: Scheme) -> Self:
        name = scheme.overview.name
        assert name is not None

        return cls(
            reference=scheme.reference,
            authority_name=authority.name,
            name=name,
            needs_review=scheme.reviews.needs_review(reporting_window),
            overview=SchemeOverviewContext.from_domain(scheme),
            funding=SchemeFundingContext.from_domain(scheme.funding),
            milestones=SchemeMilestonesContext.from_domain(scheme),
            outputs=SchemeOutputsContext.from_domain(scheme.outputs.current_output_revisions),
            review=SchemeReviewContext.from_domain(scheme.reviews),
        )


@bp.get("<reference>/spend-to-date")
@async_bearer_auth
@inject.autoparams()
async def spend_to_date_form(reference: str, users: UserRepository, schemes: SchemeRepository) -> str:
    user_info = session["user"]
    user = users.get(user_info["email"])
    assert user
    scheme = await schemes.get(reference)

    if not (scheme and scheme.is_updateable):
        abort(404)

    if user.authority_abbreviation != scheme.overview.authority_abbreviation:
        abort(403)

    context = ChangeSpendToDateContext.from_domain(scheme)
    context.form.validate_on_submit()
    return render_template("scheme/spend_to_date.html", **as_shallow_dict(context))


@bp.post("<reference>/spend-to-date")
@async_bearer_auth
@inject.autoparams()
async def spend_to_date(
    clock: Clock, users: UserRepository, schemes: SchemeRepository, reference: str
) -> str | BaseResponse:
    user_info = session["user"]
    user = users.get(user_info["email"])
    assert user
    scheme = await schemes.get(reference)

    if not (scheme and scheme.is_updateable):
        abort(404)

    if user.authority_abbreviation != scheme.overview.authority_abbreviation:
        abort(403)

    form = ChangeSpendToDateForm.from_domain(scheme.funding)

    if not form.validate():
        return await spend_to_date_form(reference)

    form.update_domain(scheme.funding, clock.now)
    await schemes.update(scheme)

    return redirect(url_for("schemes.get", reference=reference))


@bp.get("<reference>/milestones")
@async_bearer_auth
@inject.autoparams()
async def milestones_form(reference: str, clock: Clock, users: UserRepository, schemes: SchemeRepository) -> str:
    user_info = session["user"]
    user = users.get(user_info["email"])
    assert user
    scheme = await schemes.get(reference)

    if not (scheme and scheme.is_updateable):
        abort(404)

    if user.authority_abbreviation != scheme.overview.authority_abbreviation:
        abort(403)

    context = ChangeMilestoneDatesContext.from_domain(scheme, clock.now)
    context.form.validate_on_submit()
    return render_template("scheme/milestones.html", **as_shallow_dict(context))


@bp.post("<reference>/milestones")
@async_bearer_auth
@inject.autoparams()
async def milestones(
    clock: Clock, users: UserRepository, schemes: SchemeRepository, reference: str
) -> str | BaseResponse:
    user_info = session["user"]
    user = users.get(user_info["email"])
    assert user
    scheme = await schemes.get(reference)

    if not (scheme and scheme.is_updateable):
        abort(404)

    if user.authority_abbreviation != scheme.overview.authority_abbreviation:
        abort(403)

    now = clock.now
    form = ChangeMilestoneDatesForm.from_domain(scheme, now)

    if not form.validate():
        return await milestones_form(reference)

    form.update_domain(scheme, now)
    await schemes.update(scheme)

    return redirect(url_for("schemes.get", reference=reference))


@bp.post("<reference>")
@async_bearer_auth
@inject.autoparams()
async def review(clock: Clock, users: UserRepository, schemes: SchemeRepository, reference: str) -> BaseResponse:
    user_info = session["user"]
    user = users.get(user_info["email"])
    assert user
    scheme = await schemes.get(reference)

    if not (scheme and scheme.is_updateable):
        abort(404)

    if user.authority_abbreviation != scheme.overview.authority_abbreviation:
        abort(403)

    form = SchemeReviewForm()

    if not form.validate():
        return await get(reference)

    form.update_domain(scheme.reviews, clock.now)
    await schemes.update(scheme)

    flash(f"{scheme.overview.name} has been reviewed")
    return redirect(url_for("schemes.index"))
