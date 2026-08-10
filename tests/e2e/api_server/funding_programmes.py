from typing import Annotated, Any

from flask import Blueprint, Response, abort, request, url_for
from pydantic import AnyUrl, Field
from werkzeug.datastructures import MultiDict

from tests.e2e.api_server.auth import require_oauth
from tests.e2e.api_server.base import BaseModel
from tests.e2e.api_server.collections import CollectionModel
from tests.e2e.api_server.requests import parse_bool


class FundingProgrammeModel(BaseModel):
    id: Annotated[AnyUrl | None, Field(alias="@id")] = None
    code: str
    eligible_for_authority_update: bool


class FundingProgrammeItemModel(BaseModel):
    id: Annotated[AnyUrl, Field(alias="@id")]
    code: str


bp = Blueprint("funding_programmes", __name__)
funding_programmes: dict[str, FundingProgrammeModel] = {}


@bp.post("")
@require_oauth("tests")
def add_funding_programmes() -> Response:
    for element in request.json:
        funding_programme = FundingProgrammeModel.model_validate(element)

        if not funding_programme.id:
            funding_programme.id = AnyUrl(
                url_for("funding_programmes.get_funding_programme", code=funding_programme.code, _external=True)
            )

        funding_programmes[funding_programme.code] = funding_programme

    return Response(status=201)


@bp.get("")
@require_oauth()
def get_funding_programmes() -> dict[str, Any]:
    args = MultiDict(request.args)
    eligible_for_authority_update = (
        parse_bool(args.pop("eligible-for-authority-update")) if "eligible-for-authority-update" in args else None
    )
    if args:
        abort(400, f"Unexpected query string parameters: {set(args.keys())}")

    funding_programme_items = [
        FundingProgrammeItemModel(
            id=AnyUrl(url_for("funding_programmes.get_funding_programme", code=funding_programme.code, _external=True)),
            code=funding_programme.code,
        )
        for funding_programme in funding_programmes.values()
        if (
            eligible_for_authority_update is None
            or funding_programme.eligible_for_authority_update == eligible_for_authority_update
        )
    ]
    return CollectionModel[FundingProgrammeItemModel](items=funding_programme_items).to_json()


@bp.get("<code>")
@require_oauth()
def get_funding_programme(code: str) -> dict[str, Any]:
    return funding_programmes[code].to_json()


@bp.delete("")
@require_oauth("tests")
def clear_funding_programmes() -> Response:
    funding_programmes.clear()
    return Response(status=204)
