from typing import Any

from flask import Blueprint, Response, abort, request

from schemes.infrastructure.api.base import BaseModel
from tests.e2e.api_server.auth import jwt_bearer_auth
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


class CapitalSchemeMilestoneModel(BaseModel):
    milestone: str
    observation_type: str
    status_date: str


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
def add_capital_schemes() -> Response:
    for element in request.get_json():
        capital_scheme = CapitalSchemeModel.model_validate(element)
        capital_schemes[capital_scheme.reference] = capital_scheme

    return Response(status=201)


@bp.get("<reference>")
@jwt_bearer_auth
def get_capital_scheme(reference: str) -> dict[str, Any]:
    capital_scheme = capital_schemes.get(reference)

    if not capital_scheme:
        abort(404)

    return capital_scheme.model_dump(mode="json")


@bp.delete("")
def clear_authorities() -> Response:
    capital_schemes.clear()
    return Response(status=204)


@bp.post("milestones")
def add_milestones() -> Response:
    for element in request.get_json():
        milestone = MilestoneModel.model_validate(element)
        milestones[milestone.name] = milestone

    return Response(status=201)


@bp.get("milestones")
@jwt_bearer_auth
def get_milestones() -> dict[str, Any]:
    active = request.args.get("active", type=parse_bool)
    complete = request.args.get("complete", type=parse_bool)

    milestone_names = [
        milestone.name
        for milestone in milestones.values()
        if (active is None or milestone.active == active) and (complete is None or milestone.complete == complete)
    ]
    return CollectionModel[str](items=milestone_names).model_dump(mode="json")
