from typing import Annotated, Any

from flask import Blueprint, Response, abort, request, url_for
from pydantic import AnyUrl, Field

from tests.e2e.api_server.auth import require_oauth
from tests.e2e.api_server.base import BaseModel
from tests.e2e.api_server.capital_schemes import capital_schemes
from tests.e2e.api_server.collections import CollectionModel


class AuthorityModel(BaseModel):
    id: Annotated[AnyUrl | None, Field(alias="@id")] = None
    abbreviation: str
    full_name: str
    bid_submitting_capital_schemes: AnyUrl | None = None


class CapitalSchemeItemModel(BaseModel):
    id: Annotated[AnyUrl, Field(alias="@id")]


bp = Blueprint("authorities", __name__)
authorities: dict[str, AuthorityModel] = {}


@bp.post("")
@require_oauth("tests")
def add_authorities() -> Response:
    for element in request.json:
        authority = AuthorityModel.model_validate(element)

        if not authority.id:
            authority.id = AnyUrl(
                url_for("authorities.get_authority", abbreviation=authority.abbreviation, _external=True)
            )

        if not authority.bid_submitting_capital_schemes:
            authority.bid_submitting_capital_schemes = AnyUrl(
                url_for(
                    "authorities.get_authority_bid_submitting_capital_schemes",
                    abbreviation=authority.abbreviation,
                    _external=True,
                )
            )

        authorities[authority.abbreviation] = authority

    return Response(status=201)


@bp.get("<abbreviation>")
@require_oauth()
def get_authority(abbreviation: str) -> dict[str, Any]:
    authority = authorities.get(abbreviation)

    if not authority:
        abort(404)

    return authority.to_json()


@bp.get("<abbreviation>/capital-schemes/bid-submitting")
@require_oauth()
def get_authority_bid_submitting_capital_schemes(abbreviation: str) -> dict[str, Any]:
    funding_programme_codes = request.args.getlist("funding-programme-code")
    bid_status = request.args.get("bid-status")
    current_milestones = request.args.getlist("current-milestone", lambda value: value or None)

    authority_url = AnyUrl(url_for("authorities.get_authority", abbreviation=abbreviation, _external=True))
    funding_programme_urls = [
        AnyUrl(url_for("funding_programmes.get_funding_programme", code=funding_programme_code, _external=True))
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

    capital_scheme_items = [
        CapitalSchemeItemModel(
            id=AnyUrl(url_for("capital_schemes.get_capital_scheme", reference=reference, _external=True))
        )
        for reference in references
    ]
    return CollectionModel[CapitalSchemeItemModel](items=capital_scheme_items).to_json()


@bp.delete("")
@require_oauth("tests")
def clear_authorities() -> Response:
    authorities.clear()
    return Response(status=204)
