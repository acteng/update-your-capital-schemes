import os
from flask import Flask, render_template
from jinja2 import ChoiceLoader, FileSystemLoader, PackageLoader, PrefixLoader


def create_app() -> Flask:
    app = Flask(__name__, static_url_path="/")

    app.jinja_loader = ChoiceLoader(  # type: ignore
        [
            FileSystemLoader(os.path.join(app.root_path, str(app.template_folder))),
            PrefixLoader({"govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja")})
        ]
    )

    @app.route("/")
    def index() -> str:
        return render_template("index.html")

    return app
