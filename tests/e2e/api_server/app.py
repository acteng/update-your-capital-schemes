from typing import Any

from authlib.integrations.flask_client import OAuth
from flask import Flask

from tests.e2e.api_server import authorities, capital_schemes


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(test_config)

    oauth = OAuth(app)
    oauth.register(name="auth", server_metadata_url=app.config["OIDC_SERVER_METADATA_URL"])

    app.register_blueprint(authorities.bp, url_prefix="/authorities")
    app.register_blueprint(capital_schemes.bp, url_prefix="/capital-schemes")

    return app
