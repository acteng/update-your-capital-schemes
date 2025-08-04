from typing import Any

from authlib.integrations.flask_client import OAuth
from authlib.jose import jwt
from flask import Flask, Response, abort, request
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(test_config)

    oauth = OAuth(app)
    oauth.register(name="auth", server_metadata_url=app.config["OIDC_SERVER_METADATA_URL"])

    authorities: dict[str, AuthorityModel] = {}

    @app.post("/authorities")
    def add_authorities() -> Response:
        for element in request.get_json():
            authority = AuthorityModel(**element)
            authorities[authority.abbreviation] = authority

        return Response(status=201)

    @app.get("/authorities/<abbreviation>")
    def get_authority(abbreviation: str) -> dict[str, Any]:
        _validate_jwt()

        authority = authorities.get(abbreviation)

        if not authority:
            abort(404)

        return authority.model_dump()

    @app.delete("/authorities")
    def clear_authorities() -> Response:
        authorities.clear()
        return Response(status=204)

    def _validate_jwt() -> None:
        assert request.authorization
        server_metadata = oauth.auth.load_server_metadata()
        jwks = oauth.auth.fetch_jwk_set()
        claims = jwt.decode(
            request.authorization.token,
            key=jwks,
            claims_options={
                "iss": {"value": server_metadata.get("issuer")},
                "aud": {"value": app.config["RESOURCE_SERVER_IDENTIFIER"]},
            },
        )
        claims.validate()

    return app


class AuthorityModel(BaseModel):
    abbreviation: str
    full_name: str

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)
