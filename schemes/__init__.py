import os
from typing import Any, Mapping

from authlib.integrations.flask_client import OAuth
from authlib.oauth2.rfc7523 import PrivateKeyJWT
from flask import Flask, Response, request, url_for
from jinja2 import ChoiceLoader, FileSystemLoader, PackageLoader, PrefixLoader

from schemes import api, auth, home, start
from schemes.config import DevConfig


def create_app(test_config: Mapping[str, Any] | None = None) -> Flask:
    env = os.environ.get("FLASK_ENV", DevConfig.name)

    app = Flask(__name__)
    app.config.from_object(f"schemes.config.{env.title()}Config")
    app.config.from_prefixed_env()
    app.config.from_mapping(test_config)

    _configure_basic_auth(app)
    _configure_govuk_frontend(app)
    _configure_oidc(app)
    _configure_users(app)

    app.register_blueprint(start.bp)
    app.register_blueprint(auth.bp, url_prefix="/auth")
    app.register_blueprint(home.bp, url_prefix="/home")
    if app.testing:
        app.register_blueprint(api.bp, url_prefix="/api")

    return app


def _configure_basic_auth(app: Flask) -> None:
    username = app.config.get("BASIC_AUTH_USERNAME")
    password = app.config.get("BASIC_AUTH_PASSWORD")

    if username:

        @app.before_request
        def before_request() -> Response | None:
            authz = request.authorization
            if authz and authz.type == "basic" and authz.username == username and authz.password == password:
                return None
            return Response(status=401, headers={"WWW-Authenticate": "Basic realm='Schemes'"}, response="Unauthorized")


def _configure_govuk_frontend(app: Flask) -> None:
    default_loader = FileSystemLoader(os.path.join(app.root_path, str(app.template_folder)))
    govuk_loader = PrefixLoader({"govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja")})
    app.jinja_loader = ChoiceLoader([default_loader, govuk_loader])  # type: ignore

    @app.context_processor
    def govuk_frontend_config() -> dict[str, str]:
        return {
            "assetPath": url_for("static", filename="govuk-frontend/assets"),
            "oneLoginLink": app.config["GOVUK_PROFILE_URL"],
        }


def _configure_oidc(app: Flask) -> None:
    oauth = OAuth(app)
    oauth.register(
        name="govuk",
        client_id=app.config["GOVUK_CLIENT_ID"],
        client_secret=app.config["GOVUK_CLIENT_SECRET"].encode(),
        server_metadata_url=app.config["GOVUK_SERVER_METADATA_URL"],
        client_kwargs={
            "scope": "openid email",
            "token_endpoint_auth_method": PrivateKeyJWT(app.config["GOVUK_TOKEN_ENDPOINT"]),
        },
    )


def _configure_users(app: Flask) -> None:
    app.extensions["users"] = []

    if not app.testing:
        app.extensions["users"].extend(
            ["alex.coleman@activetravelengland.gov.uk", "mark.hobson@activetravelengland.gov.uk"]
        )
