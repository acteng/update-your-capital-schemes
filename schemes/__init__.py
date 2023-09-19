import os
from flask import Flask, render_template, url_for
from jinja2 import BaseLoader, ChoiceLoader, FileSystemLoader, PackageLoader, PrefixLoader


def create_app() -> Flask:
    app = Flask(__name__)
    app.jinja_loader = create_jinja_loader(app)  # type: ignore

    @app.context_processor
    def govuk_frontend_config() -> dict[str, str]:
        return {"assetPath": url_for("static", filename="govuk-frontend/assets")}

    @app.route("/")
    def index() -> str:
        return render_template("index.html")

    return app


def create_jinja_loader(app: Flask) -> BaseLoader:
    default_loader = FileSystemLoader(os.path.join(app.root_path, str(app.template_folder)))
    govuk_loader = PrefixLoader({"govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja")})
    return ChoiceLoader([default_loader, govuk_loader])
