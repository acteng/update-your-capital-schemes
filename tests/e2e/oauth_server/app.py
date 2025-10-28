from typing import Any

from authlib.integrations.flask_oauth2 import AuthorizationServer
from authlib.jose import KeySet, RSAKey
from authlib.oauth2 import OAuth2Request
from flask import Flask, Response, jsonify, url_for

from tests.e2e.oauth_server.clients import ClientRepository, StubClient
from tests.e2e.oauth_server.grants import ClientSecretPostClientCredentialsGrant
from tests.e2e.oauth_server.tokens import StubJWTBearerTokenGenerator


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(test_config)

    clients = ClientRepository()
    for client in app.config["CLIENTS"]:
        clients.add(StubClient(client["clientId"], client["clientSecret"], client["scope"]))

    def _save_token(token: dict[str, str], oauth2_request: OAuth2Request) -> None:
        # JWT Bearer tokens do not require saving
        pass

    def _init_grant(grant: ClientSecretPostClientCredentialsGrant) -> None:
        # attributes set by grant extension as initializer arguments are fixed
        grant.audience = app.config["RESOURCE_SERVER_IDENTIFIER"]

    authorization_server = AuthorizationServer(app, clients.get, _save_token)
    authorization_server.register_grant(ClientSecretPostClientCredentialsGrant, [_init_grant])
    issuer = "http://auth.example"
    key = RSAKey.generate_key(is_private=True)
    authorization_server.register_token_generator(
        "default", StubJWTBearerTokenGenerator(issuer, app.config["RESOURCE_SERVER_IDENTIFIER"], KeySet([key]))
    )

    @app.get("/.well-known/openid-configuration")
    def openid_configuration() -> Response:
        return jsonify(
            {
                "issuer": issuer,
                "token_endpoint": url_for("token", _external=True),
                "jwks_uri": url_for("key_set", _external=True),
            }
        )

    @app.post("/token")
    def token() -> Response:
        response: Response = authorization_server.create_token_response()
        return response

    @app.get("/.well-known/jwks.json")
    def key_set() -> Any:
        return KeySet([key]).as_dict()

    return app
