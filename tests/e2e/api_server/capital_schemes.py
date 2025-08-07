from typing import Any

from flask import Blueprint, Response, abort, request

from schemes.infrastructure.api.base import BaseModel
from tests.e2e.api_server.auth import jwt_bearer_auth


class CapitalSchemeOverviewModel(BaseModel):
    name: str
    bid_submitting_authority: str
    funding_programme: str


class CapitalSchemeBidStatusDetailsModel(BaseModel):
    bid_status: str


class CapitalSchemeAuthorityReviewModel(BaseModel):
    review_date: str


class CapitalSchemeModel(BaseModel):
    reference: str
    overview: CapitalSchemeOverviewModel
    bid_status_details: CapitalSchemeBidStatusDetailsModel
    authority_review: CapitalSchemeAuthorityReviewModel


bp = Blueprint("capital_schemes", __name__)
capital_schemes: dict[str, CapitalSchemeModel] = {}


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
