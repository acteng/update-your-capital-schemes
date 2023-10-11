from typing import Any

from authlib.integrations.flask_oauth2 import AuthorizationServer, current_token
from authlib.jose.rfc7517.base_key import Key
from authlib.jose.rfc7517.key_set import KeySet
from authlib.jose.rfc7518.rsa_key import RSAKey
from authlib.oauth2.rfc6749.requests import OAuth2Request
from flask import Flask, Response, jsonify, redirect, request, url_for
from werkzeug import Response as BaseResponse

from tests.e2e.oidc_server.clients import ClientRepository, StubClient
from tests.e2e.oidc_server.grants import (
    AuthorizationCodeRepository,
    StubAuthorizationCodeGrant,
    StubOpenIDCode,
    StubUserInfo,
)
from tests.e2e.oidc_server.jwts import PrivateKeyJwtClientAssertion
from tests.e2e.oidc_server.resources import TypedResourceProtector
from tests.e2e.oidc_server.tokens import (
    StubBearerTokenValidator,
    StubToken,
    TokenRepository,
)
from tests.e2e.oidc_server.users import StubUser, UserRepository


class OidcServerApp(Flask):
    def __init__(self, import_name: str):
        super().__init__(import_name)
        self._users = UserRepository()
        self._authorized_user_id: str | None = None
        self._clients = ClientRepository()
        self._authorization_codes = AuthorizationCodeRepository()
        self._tokens = TokenRepository()

    def create_authorization_server(self, key: Key) -> AuthorizationServer:
        authorization_server = AuthorizationServer(self, self._clients.get, self._save_token)

        issuer = self._get_base_url()
        open_id_code = StubOpenIDCode(issuer, key, self._authorization_codes, require_nonce=True)
        authorization_server.register_grant(StubAuthorizationCodeGrant, [self._init_grant, open_id_code])

        return authorization_server

    def create_resource_protector(self) -> TypedResourceProtector:
        resource_protector = TypedResourceProtector()
        resource_protector.register_token_validator(StubBearerTokenValidator(self._tokens))
        return resource_protector

    def add_user(self, user: StubUser) -> None:
        self._users.add(user)
        # automatically authorize first user
        if self._authorized_user_id is None:
            self.authorize_user(user.id)

    def clear_users(self) -> None:
        self._users.clear()

    def authorize_user(self, user_id: str) -> None:
        self._authorized_user_id = user_id

    def authorized_user(self) -> StubUser | None:
        return None if self._authorized_user_id is None else self._users.get(self._authorized_user_id)

    def current_user(self) -> StubUser:
        user_id = current_token.user_id
        return self._users.get(user_id)

    def add_client(self, client: StubClient) -> None:
        self._clients.add(client)

    def _get_base_url(self) -> str:
        scheme = self.config["PREFERRED_URL_SCHEME"]
        server_name = self.config["SERVER_NAME"]
        root = self.config["APPLICATION_ROOT"]
        return f"{scheme}://{server_name}{root}"

    def _init_grant(self, grant: StubAuthorizationCodeGrant) -> None:
        # attributes set by grant extension as initializer arguments are fixed
        grant.authorization_codes = self._authorization_codes
        grant.users = self._users

    def _save_token(self, token: dict[str, str], oauth2_request: OAuth2Request) -> None:
        self._tokens.add(
            token["access_token"],
            StubToken(client_id=oauth2_request.client.client_id, user_id=oauth2_request.user.id, scope=token["scope"]),
        )


def create_app(test_config: dict[str, Any] | None = None) -> OidcServerApp:
    app = OidcServerApp(__name__)
    app.config.from_prefixed_env()
    app.config.from_mapping(test_config)

    key = RSAKey.generate_key(is_private=True)
    authorization_server = app.create_authorization_server(key)
    require_oauth = app.create_resource_protector()

    @app.route("/users", methods=["POST"])
    def add_user() -> Response:
        user = StubUser(**request.get_json())
        app.add_user(user)
        return Response(status=201)

    @app.route("/users", methods=["DELETE"])
    def clear_users() -> Response:
        app.clear_users()
        return Response(status=204)

    @app.route("/clients", methods=["POST"])
    def add_client() -> Response:
        client = StubClient(**request.get_json())
        app.add_client(client)
        return Response(status=201)

    @app.route("/.well-known/openid-configuration")
    def openid_configuration() -> Response:
        return jsonify(
            {
                "authorization_endpoint": url_for("authorize", _external=True),
                "token_endpoint": url_for("token", _external=True),
                "userinfo_endpoint": url_for("userinfo", _external=True),
                "jwks_uri": url_for("jwks", _external=True),
            }
        )

    @app.route("/authorize")
    def authorize() -> Response:
        authorized_user = app.authorized_user()

        if authorized_user is None:
            return Response("<h1>Login</h1>")

        response: Response = authorization_server.create_authorization_response(grant_user=authorized_user)
        return response

    @app.route("/token", methods=["POST"])
    def token() -> Response:
        response: Response = authorization_server.create_token_response()
        return response

    @app.route("/userinfo")
    @require_oauth("openid email")
    def userinfo() -> Response:
        user = app.current_user()
        return jsonify(StubUserInfo(user))

    @app.route("/jwks_uri")
    def jwks() -> Response:
        return jsonify(KeySet([key]).as_dict())

    @app.route("/logout")
    def logout() -> BaseResponse:
        id_token_hint = request.args.get("id_token_hint")
        post_logout_redirect_uri = request.args.get("post_logout_redirect_uri")
        assert id_token_hint is not None and post_logout_redirect_uri is not None
        # TODO: revoke token for id_token_hint

        return redirect(post_logout_redirect_uri)

    # register after token endpoint has been defined
    authorization_server.register_client_auth_method(
        PrivateKeyJwtClientAssertion.CLIENT_AUTH_METHOD,
        PrivateKeyJwtClientAssertion(app.url_for("token", _external=True)),
    )

    return app
