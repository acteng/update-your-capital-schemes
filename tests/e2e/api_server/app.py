from typing import Any

from authlib.integrations.flask_client import OAuth
from flask import Flask

from tests.e2e.api_server import authorities, capital_schemes, clock, funding_programmes
from tests.e2e.api_server.auth import ApiJwtBearerTokenValidator, require_oauth


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(test_config)

    oauth = OAuth(app)
    oauth.register(name="auth", server_metadata_url=app.config["OIDC_SERVER_METADATA_URL"])

    server_metadata = oauth.auth.load_server_metadata()
    issuer = server_metadata.get("issuer")
    resource_server_identifier = app.config["RESOURCE_SERVER_IDENTIFIER"]
    require_oauth.register_token_validator(ApiJwtBearerTokenValidator(issuer, resource_server_identifier))

    app.register_blueprint(clock.bp, url_prefix="/clock")
    app.register_blueprint(funding_programmes.bp, url_prefix="/funding-programmes")
    app.register_blueprint(authorities.bp, url_prefix="/authorities")
    app.register_blueprint(capital_schemes.bp, url_prefix="/capital-schemes")

    return app
