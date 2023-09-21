import os
import functools
from typing import Callable, TypeVar, ParamSpec, Union, Mapping, Any

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
    def check_auth(username: Union[str, None], password: Union[str, None]) -> bool:
        return str(app.config["AUTH_USER"]) == username \
            and str(app.config["AUTH_PASSWORD"]) == password

    T = TypeVar('T')
    P = ParamSpec('P')  # pylint: disable=invalid-name

    def basic_auth(f: Callable[P, T]) -> Callable[P, Union[T, Response]]:  # pylint: disable=invalid-name
        @functools.wraps(f)
        def decorated_function(*args: P.args, **kwargs: P.kwargs) -> Union[T, Response]:
            auth = request.authorization
            if not auth or not check_auth(auth.username, auth.password):
                return Response(
                    response="Unauthorized",
                    status=401,
                    headers={"WWW-Authenticate": "Basic realm='Login Required'"}
                )
            return f(*args, **kwargs)

        return decorated_function

    if "AUTH_USER" in app.config:
        @app.before_request
        @basic_auth
        def before_request() -> None:
            pass


def _configure_govuk_frontend(app: Flask) -> None:
    default_loader = FileSystemLoader(os.path.join(app.root_path, str(app.template_folder)))
    govuk_loader = PrefixLoader({"govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja")})
    app.jinja_loader = ChoiceLoader([default_loader, govuk_loader])  # type: ignore

    @app.context_processor
    def govuk_frontend_config() -> dict[str, str]:
        return {"assetPath": url_for("static", filename="govuk-frontend/assets")}
