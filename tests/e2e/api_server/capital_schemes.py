from typing import Any

from flask import Blueprint, Response, abort, make_response, request

from tests.e2e.api_server.auth import require_oauth
from tests.e2e.api_server.base import BaseModel
from tests.e2e.api_server.collections import CollectionModel
from tests.e2e.api_server.requests import parse_bool


class CapitalSchemeOverviewModel(BaseModel):
    name: str
    bid_submitting_authority: str
    funding_programme: str
    type: str


class CapitalSchemeBidStatusDetailsModel(BaseModel):
    bid_status: str


class CapitalSchemeFinancialModel(BaseModel):
    type: str
    amount: int
    source: str


class CapitalSchemeMilestoneModel(BaseModel):
    milestone: str
    observation_type: str
    status_date: str
    source: str


class CapitalSchemeMilestonesModel(CollectionModel[CapitalSchemeMilestoneModel]):
    current_milestone: str | None


class CapitalSchemeOutputModel(BaseModel):
    type: str
    measure: str
    observation_type: str
    value: str


class CapitalSchemeAuthorityReviewModel(BaseModel):
    review_date: str


class CapitalSchemeModel(BaseModel):
    reference: str
    overview: CapitalSchemeOverviewModel
    bid_status_details: CapitalSchemeBidStatusDetailsModel
    financials: CollectionModel[CapitalSchemeFinancialModel]
    milestones: CapitalSchemeMilestonesModel
    outputs: CollectionModel[CapitalSchemeOutputModel]
    authority_review: CapitalSchemeAuthorityReviewModel | None


class MilestoneModel(BaseModel):
    name: str
    active: bool
    complete: bool


bp = Blueprint("capital_schemes", __name__)
capital_schemes: dict[str, CapitalSchemeModel] = {}
milestones: dict[str, MilestoneModel] = {}


@bp.post("")
@require_oauth("tests")
def add_capital_schemes() -> Response:
    for element in request.get_json():
        capital_scheme = CapitalSchemeModel.model_validate(element)
        capital_schemes[capital_scheme.reference] = capital_scheme

    return Response(status=201)


@bp.get("<reference>")
@require_oauth()
def get_capital_scheme(reference: str) -> dict[str, Any]:
    capital_scheme = capital_schemes.get(reference)

    if not capital_scheme:
        abort(404)

    return capital_scheme.to_json()


@bp.post("<reference>/financials")
@require_oauth()
def add_financial(reference: str) -> Response:
    capital_scheme = capital_schemes.get(reference)

    if not capital_scheme:
        abort(404)

    financial = CapitalSchemeFinancialModel.model_validate(request.get_json())
    # remove current financials of same type
    capital_scheme.financials.items = [f for f in capital_scheme.financials.items if f.type != financial.type]
    capital_scheme.financials.items.append(financial)

    return make_response(financial.to_json(), 201)


@bp.post("<reference>/milestones")
@require_oauth()
def add_capital_scheme_milestones(reference: str) -> Response:
    capital_scheme = capital_schemes.get(reference)

    if not capital_scheme:
        abort(404)

    milestones = CollectionModel[CapitalSchemeMilestoneModel].model_validate(request.get_json())
    milestone_observation_types = [(m.milestone, m.observation_type) for m in milestones.items]
    # remove current milestones of same type
    capital_scheme.milestones.items = [
        m
        for m in capital_scheme.milestones.items
        if (m.milestone, m.observation_type) not in milestone_observation_types
    ]
    capital_scheme.milestones.items.extend(milestones.items)

    return make_response(milestones.to_json(), 201)


@bp.delete("")
@require_oauth("tests")
def clear_capital_schemes() -> Response:
    capital_schemes.clear()
    return Response(status=204)


@bp.post("milestones")
@require_oauth("tests")
def add_milestones() -> Response:
    for element in request.get_json():
        milestone = MilestoneModel.model_validate(element)
        milestones[milestone.name] = milestone

    return Response(status=201)


@bp.get("milestones")
@require_oauth()
def get_milestones() -> dict[str, Any]:
    active = request.args.get("active", type=parse_bool)
    complete = request.args.get("complete", type=parse_bool)

    milestone_names = [
        milestone.name
        for milestone in milestones.values()
        if (active is None or milestone.active == active) and (complete is None or milestone.complete == complete)
    ]
    return CollectionModel[str](items=milestone_names).to_json()


@bp.delete("milestones")
@require_oauth("tests")
def clear_milestones() -> Response:
    milestones.clear()
    return Response(status=204)
