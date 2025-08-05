from typing import Any

from flask import Blueprint, Response, abort, request
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from tests.e2e.api_server.auth import jwt_bearer_auth


class AuthorityModel(BaseModel):
    abbreviation: str
    full_name: str

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)


bp = Blueprint("authorities", __name__)
authorities: dict[str, AuthorityModel] = {}


@bp.post("/authorities")
def add_authorities() -> Response:
    for element in request.get_json():
        authority = AuthorityModel(**element)
        authorities[authority.abbreviation] = authority

    return Response(status=201)


@bp.get("/authorities/<abbreviation>")
@jwt_bearer_auth
def get_authority(abbreviation: str) -> dict[str, Any]:
    authority = authorities.get(abbreviation)

    if not authority:
        abort(404)

    return authority.model_dump()


@bp.delete("/authorities")
def clear_authorities() -> Response:
    authorities.clear()
    return Response(status=204)
