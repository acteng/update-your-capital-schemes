import os
from typing import Mapping, Any

from flask import Flask, render_template, url_for, Response, request
from jinja2 import ChoiceLoader, FileSystemLoader, PackageLoader, PrefixLoader


def create_app(test_config: Mapping[str, Any] | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_prefixed_env()
    app.config.from_mapping(test_config)

    _configure_basic_auth(app)
    _configure_govuk_frontend(app)

    @app.route("/")
    def index() -> str:
        return render_template("index.html")

    return app


def _configure_basic_auth(app: Flask) -> None:
    username = app.config.get("BASIC_AUTH_USERNAME")
    password = app.config.get("BASIC_AUTH_PASSWORD")

    if username:

        @app.before_request
        def before_request() -> Response | None:
            auth = request.authorization
            if auth and auth.type == "basic" and auth.username == username and auth.password == password:
                return None
            return Response(status=401, headers={"WWW-Authenticate": "Basic realm='Schemes'"}, response="Unauthorized")


def _configure_govuk_frontend(app: Flask) -> None:
    default_loader = FileSystemLoader(os.path.join(app.root_path, str(app.template_folder)))
    govuk_loader = PrefixLoader({"govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja")})
    app.jinja_loader = ChoiceLoader([default_loader, govuk_loader])  # type: ignore

    @app.context_processor
    def govuk_frontend_config() -> dict[str, str]:
        return {"assetPath": url_for("static", filename="govuk-frontend/assets")}
