import os
from typing import Any, Callable, Mapping

import alembic.config
import inject
from alembic import command
from authlib.integrations.flask_client import OAuth
from authlib.oauth2.rfc7523 import PrivateKeyJWT
from dataclass_wizard import JSONWizard
from dataclass_wizard.enums import LetterCase
from flask import (
    Config,
    Flask,
    Response,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_wtf import CSRFProtect
from flask_wtf.csrf import CSRFError
from govuk_frontend_wtf.main import WTFormsHelpers
from inject import Binder
from jinja2 import ChoiceLoader, FileSystemLoader, PackageLoader, PrefixLoader
from sqlalchemy import Engine, create_engine, event
from sqlalchemy.dialects.sqlite.base import SQLiteDialect
from sqlalchemy.engine.interfaces import DBAPIConnection
from sqlalchemy.pool import ConnectionPoolEntry
from werkzeug import Response as BaseResponse

from schemes.config import DevConfig
from schemes.domain.authorities import AuthorityRepository
from schemes.domain.reporting_window import (
    DefaultReportingWindowService,
    ReportingWindowService,
)
from schemes.domain.schemes import SchemeRepository
from schemes.domain.users import UserRepository
from schemes.infrastructure.clock import Clock, FakeClock, SystemClock
from schemes.infrastructure.database.authorities import DatabaseAuthorityRepository
from schemes.infrastructure.database.schemes import DatabaseSchemeRepository
from schemes.infrastructure.database.users import DatabaseUserRepository
from schemes.views import auth, authorities, clock, schemes, start, users
from schemes.views.filters import date, pounds, remove_exponent


def create_app(test_config: Mapping[str, Any] | None = None) -> Flask:
    env = os.environ.get("FLASK_ENV", DevConfig.name)

    app = Flask(__name__, static_folder="views/static", template_folder="views/templates")
    app.config.from_object(f"schemes.config.{env.title()}Config")
    app.config.from_prefixed_env()
    app.config.from_mapping(test_config)

    inject.configure(bindings(app), bind_in_runtime=False)

    _configure_dataclass_wizard()
    _configure_jinja(app)
    _configure_error_pages(app)
    csrf = CSRFProtect(app)
    _configure_govuk_frontend(app)
    WTFormsHelpers(app)
    _configure_oidc(app)

    app.register_blueprint(clock.bp, url_prefix="/clock")
    csrf.exempt(clock.set_clock)
    app.register_blueprint(start.bp)
    app.register_blueprint(auth.bp, url_prefix="/auth")
    app.register_blueprint(authorities.bp, url_prefix="/authorities")
    csrf.exempt(authorities.add)
    csrf.exempt(authorities.add_users)
    csrf.exempt(authorities.add_schemes)
    csrf.exempt(authorities.clear)
    app.register_blueprint(schemes.bp, url_prefix="/schemes")
    csrf.exempt(schemes.schemes.clear)
    app.register_blueprint(users.bp, url_prefix="/users")
    csrf.exempt(users.clear)

    _migrate_database()

    return app


def destroy_app(app: Flask) -> None:
    engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])

    if engine.dialect.name == SQLiteDialect.name:
        event.remove(Engine, "connect", _enforce_sqlite_foreign_keys)

    inject.clear()


def bindings(app: Flask) -> Callable[[Binder], None]:
    def _bindings(binder: Binder) -> None:
        binder.bind(Config, app.config)
        binder.bind(Clock, FakeClock() if app.testing else SystemClock())
        binder.bind_to_constructor(ReportingWindowService, DefaultReportingWindowService)
        binder.bind_to_constructor(Engine, _create_engine)
        binder.bind_to_constructor(AuthorityRepository, DatabaseAuthorityRepository)
        binder.bind_to_constructor(UserRepository, DatabaseUserRepository)
        binder.bind_to_constructor(SchemeRepository, DatabaseSchemeRepository)

    return _bindings


@inject.autoparams()
def _create_engine(config: Config) -> Engine:
    engine = create_engine(config["SQLALCHEMY_DATABASE_URI"])

    if engine.dialect.name == SQLiteDialect.name:
        event.listen(Engine, "connect", _enforce_sqlite_foreign_keys)

    return engine


def _enforce_sqlite_foreign_keys(dbapi_connection: DBAPIConnection, _connection_record: ConnectionPoolEntry) -> None:
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def _configure_dataclass_wizard() -> None:
    class GlobalJSONMeta(JSONWizard.Meta):  # type: ignore
        key_transform_with_dump = LetterCase.SNAKE
        raise_on_unknown_json_key = True


def _configure_jinja(app: Flask) -> None:
    app.jinja_options["extensions"] = ["jinja2.ext.do"]

    app.jinja_env.filters[date.__name__] = date
    app.jinja_env.filters[pounds.__name__] = pounds
    app.jinja_env.filters[remove_exponent.__name__] = remove_exponent

    default_loader = FileSystemLoader(os.path.join(app.root_path, str(app.template_folder)))
    package_loaders = PrefixLoader(
        {
            "govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja"),
            "govuk_frontend_wtf": PackageLoader("govuk_frontend_wtf"),
        }
    )
    app.jinja_loader = ChoiceLoader([default_loader, package_loaders])


def _configure_error_pages(app: Flask) -> None:
    @app.errorhandler(403)
    def forbidden(_error: Exception) -> Response:
        return Response(render_template("403.html"), status=403)

    @app.errorhandler(404)
    def not_found(_error: Exception) -> Response:
        return Response(render_template("404.html"), status=404)

    @app.errorhandler(500)
    def internal_server_error(_error: Exception) -> Response:
        return Response(render_template("500.html"), status=500)

    @app.errorhandler(CSRFError)
    def csrf_error(_error: CSRFError) -> BaseResponse:
        flash("The form you were submitting has expired. Please try again.")
        return redirect(request.full_path)


def _configure_govuk_frontend(app: Flask) -> None:
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


def _migrate_database() -> None:
    engine: Engine = inject.instance(Engine)

    alembic_config = alembic.config.Config()
    alembic_config.set_main_option("script_location", "schemes:infrastructure/database/migrations")

    with engine.connect() as connection:
        alembic_config.attributes["connection"] = connection
        command.upgrade(alembic_config, "head")
