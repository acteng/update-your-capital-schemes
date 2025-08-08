from typing import Any

from flask import Blueprint, Response, abort, request, url_for
from pydantic import AnyUrl

from schemes.infrastructure.api.base import BaseModel
from tests.e2e.api_server.auth import jwt_bearer_auth
from tests.e2e.api_server.capital_schemes import capital_schemes
from tests.e2e.api_server.collections import CollectionModel


class AuthorityModel(BaseModel):
    abbreviation: str
    full_name: str


bp = Blueprint("authorities", __name__)
authorities: dict[str, AuthorityModel] = {}


@bp.post("")
def add_authorities() -> Response:
    for element in request.get_json():
        authority = AuthorityModel.model_validate(element)
        authorities[authority.abbreviation] = authority

    return Response(status=201)


@bp.get("<abbreviation>")
@jwt_bearer_auth
def get_authority(abbreviation: str) -> dict[str, Any]:
    authority = authorities.get(abbreviation)

    if not authority:
        abort(404)

    return authority.model_dump(mode="json")


@bp.get("<abbreviation>/capital-schemes/bid-submitting")
@jwt_bearer_auth
def get_authority_bid_submitting_capital_schemes(abbreviation: str) -> dict[str, Any]:
    funding_programme_codes = request.args.getlist("funding-programme-code")
    bid_status = request.args.get("bid-status")
    current_milestones = request.args.getlist("current-milestone")

    authority_url = url_for("authorities.get_authority", abbreviation=abbreviation, _external=True)
    funding_programme_urls = [
        url_for("funding_programmes.get_funding_programme", code=funding_programme_code, _external=True)
        for funding_programme_code in funding_programme_codes
    ]
    references = [
        capital_scheme.reference
        for capital_scheme in capital_schemes.values()
        if capital_scheme.overview.bid_submitting_authority == authority_url
        and (not funding_programme_urls or capital_scheme.overview.funding_programme in funding_programme_urls)
        and (not bid_status or capital_scheme.bid_status_details.bid_status == bid_status)
        and (not current_milestones or capital_scheme.milestones.current_milestone in current_milestones)
    ]

    capital_scheme_urls = [
        AnyUrl(url_for("capital_schemes.get_capital_scheme", reference=reference, _external=True))
        for reference in references
    ]
    return CollectionModel[AnyUrl](items=capital_scheme_urls).model_dump(mode="json")


@bp.delete("")
def clear_authorities() -> Response:
    authorities.clear()
    return Response(status=204)
