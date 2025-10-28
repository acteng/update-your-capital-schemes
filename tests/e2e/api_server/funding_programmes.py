from typing import Annotated, Any

from flask import Blueprint, Response, request, url_for
from pydantic import AnyUrl, Field

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
    for element in request.get_json():
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
    eligible_for_authority_update = request.args.get("eligible-for-authority-update", type=parse_bool)

    funding_programme_item_models = [
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
    return CollectionModel[FundingProgrammeItemModel](items=funding_programme_item_models).to_json()


@bp.get("<code>")
@require_oauth()
def get_funding_programme(code: str) -> dict[str, Any]:
    return funding_programmes[code].to_json()


@bp.delete("")
@require_oauth("tests")
def clear_funding_programmes() -> Response:
    funding_programmes.clear()
    return Response(status=204)
