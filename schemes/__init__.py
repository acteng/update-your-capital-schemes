import os
from datetime import timedelta
from logging import Logger
from typing import Any, Callable, Mapping

import alembic.config
import flask_session
import inject
from alembic import command
from authlib.integrations.flask_client import OAuth
from authlib.oauth2.rfc7523 import PrivateKeyJWT
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
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_wtf.csrf import CSRFError
from govuk_frontend_wtf.main import WTFormsHelpers
from inject import Binder
from jinja2 import ChoiceLoader, FileSystemLoader, PackageLoader, PrefixLoader
from sqlalchemy import Engine, create_engine, event
from sqlalchemy.dialects.sqlite.base import SQLiteDialect
from sqlalchemy.engine.interfaces import DBAPIConnection
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import ConnectionPoolEntry
from werkzeug import Response as BaseResponse

from schemes.annotations import Migrated
from schemes.config import LocalConfig
from schemes.domain.authorities import AuthorityRepository
from schemes.domain.reporting_window import (
    DefaultReportingWindowService,
    ReportingWindowService,
)
from schemes.domain.schemes import SchemeRepository
from schemes.domain.users import UserRepository
from schemes.infrastructure.api import ApiAuthorityRepository
from schemes.infrastructure.clock import Clock, FakeClock, SystemClock
from schemes.infrastructure.database import (
    AuthorityEntity,
    CapitalSchemeAuthorityReviewEntity,
    CapitalSchemeBidStatusEntity,
    CapitalSchemeEntity,
    CapitalSchemeFinancialEntity,
    CapitalSchemeInterventionEntity,
    CapitalSchemeMilestoneEntity,
    CapitalSchemeOverviewEntity,
    UserEntity,
)
from schemes.infrastructure.database.authorities import DatabaseAuthorityRepository
from schemes.infrastructure.database.schemes import DatabaseSchemeRepository
from schemes.infrastructure.database.users import DatabaseUserRepository
from schemes.sessions import RequestFilteringSessionInterface
from schemes.views import auth, authorities, clock, legal, schemes, start, users
from schemes.views.filters import date, pounds, remove_exponent


def create_app(test_config: Mapping[str, Any] | None = None) -> Flask:
    env = os.getenv("FLASK_ENV", LocalConfig.name)

    app = Flask(__name__, static_folder="views/static", template_folder="views/templates")
    app.config.from_object(f"schemes.config.{env.title()}Config")
    app.config.from_prefixed_env()
    app.config.from_mapping(test_config)

    _configure_logger(app)

    inject.configure(bindings(app), bind_in_runtime=False)

    logger = inject.instance(Logger)
    logger.info("Using environment '%s'", env)

    app.config["SESSION_SQLALCHEMY"] = SQLAlchemy(app)
    flask_session.Session(app)
    app.session_interface = RequestFilteringSessionInterface(app.session_interface, f"{app.static_url_path}/")
    _configure_jinja(app)
    _configure_http(app)
    _configure_error_pages(app)
    csrf = CSRFProtect(app)
    _configure_govuk_frontend(app)
    WTFormsHelpers(app)
    _configure_oidc(app)

    app.register_blueprint(clock.bp, url_prefix="/clock")
    csrf.exempt(clock.set_clock)
    app.register_blueprint(start.bp)
    app.register_blueprint(legal.bp)
    app.register_blueprint(auth.bp, url_prefix="/auth")
    app.register_blueprint(authorities.bp, url_prefix="/authorities")
    csrf.exempt(authorities.add)
    csrf.exempt(authorities.add_users)
    csrf.exempt(authorities.clear)
    app.register_blueprint(schemes.bp, url_prefix="/schemes")
    csrf.exempt(schemes.schemes.add_schemes)
    csrf.exempt(schemes.schemes.clear)
    app.register_blueprint(users.bp, url_prefix="/users")
    csrf.exempt(users.clear)

    _migrate_database()

    return app


def destroy_app(_app: Flask) -> None:
    inject.clear()


def bindings(app: Flask) -> Callable[[Binder], None]:
    def _bindings(binder: Binder) -> None:
        binder.bind(Flask, app)
        binder.bind(Config, app.config)
        binder.bind(Logger, app.logger)
        binder.bind(Clock, FakeClock() if app.testing else SystemClock())
        binder.bind_to_constructor(ReportingWindowService, DefaultReportingWindowService)
        binder.bind_to_constructor(Engine, _create_engine)
        binder.bind_to_constructor((Engine, CapitalSchemeEntity), _create_capital_schemes_engine)
        binder.bind_to_constructor(sessionmaker[Session], _create_session_maker)
        binder.bind_to_constructor(AuthorityRepository, DatabaseAuthorityRepository)
        binder.bind_to_constructor(
            (AuthorityRepository, Migrated),
            _create_api_authority_repository if "ATE_URL" in app.config else DatabaseAuthorityRepository,
        )
        binder.bind_to_constructor(UserRepository, DatabaseUserRepository)
        binder.bind_to_constructor(SchemeRepository, DatabaseSchemeRepository)

    return _bindings


def _configure_logger(app: Flask) -> None:
    app.logger.setLevel(app.config["LOGGER_LEVEL"])


@inject.autoparams()
def _create_engine(app: Flask) -> Engine:
    flask_sqlalchemy_extension: SQLAlchemy = app.extensions["sqlalchemy"]
    with app.app_context():
        engine = flask_sqlalchemy_extension.engine

    if engine.dialect.name == SQLiteDialect.name:
        event.listen(engine, "connect", _enforce_sqlite_foreign_keys)

    return engine


@inject.autoparams()
def _create_capital_schemes_engine(config: Config, engine: Engine) -> Engine:
    database_uri = config.get("CAPITAL_SCHEMES_DATABASE_URI")
    engine_options = config["SQLALCHEMY_ENGINE_OPTIONS"]
    return create_engine(database_uri, **engine_options) if database_uri else engine


@inject.params(engine=Engine, capital_schemes_engine=(Engine, CapitalSchemeEntity))
def _create_session_maker(engine: Engine, capital_schemes_engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(
        binds={
            AuthorityEntity: capital_schemes_engine,
            CapitalSchemeAuthorityReviewEntity: capital_schemes_engine,
            CapitalSchemeBidStatusEntity: capital_schemes_engine,
            CapitalSchemeEntity: capital_schemes_engine,
            CapitalSchemeFinancialEntity: capital_schemes_engine,
            CapitalSchemeInterventionEntity: capital_schemes_engine,
            CapitalSchemeMilestoneEntity: capital_schemes_engine,
            CapitalSchemeOverviewEntity: capital_schemes_engine,
            UserEntity: engine,
        }
    )


@inject.autoparams()
def _create_api_authority_repository(app: Flask) -> ApiAuthorityRepository:
    oauth = app.extensions["authlib.integrations.flask_client"]
    return ApiAuthorityRepository(oauth.ate)


def _enforce_sqlite_foreign_keys(dbapi_connection: DBAPIConnection, _connection_record: ConnectionPoolEntry) -> None:
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


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


def _configure_http(app: Flask) -> None:
    hsts_max_age = int(timedelta(days=365).total_seconds())
    csp_govuk_frontend = "'sha256-GUQ5ad8JK5KmEWmROf3LZd9ge94daqNvd8xy9YS1iDw='"
    csp_govuk_frontend_init = "'sha256-qlEoMJwhtzSzuQBNcUtKL5nwWlPXO6xVXHxEUboRWW4='"

    @app.after_request
    def set_headers(response: Response) -> Response:
        response.headers["Strict-Transport-Security"] = f"max-age={hsts_max_age}"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.content_security_policy.script_src = f"{csp_govuk_frontend} {csp_govuk_frontend_init} 'self';"
        response.content_security_policy.default_src = "'self';"
        if not response.direct_passthrough:
            response.cache_control.no_store = True
        return response


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
    def govuk_frontend_config() -> dict[str, Any]:
        rebrand = False
        return {
            "assetPath": url_for(
                "static", filename="govuk-frontend/assets/rebrand" if rebrand else "govuk-frontend/assets"
            ),
            "govukRebrand": rebrand,
            "themeColor": "#006853",
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

    if "ATE_URL" in app.config:
        oauth.register(
            name="ate",
            client_id=app.config["ATE_CLIENT_ID"],
            client_secret=app.config["ATE_CLIENT_SECRET"],
            server_metadata_url=app.config["ATE_SERVER_METADATA_URL"],
            access_token_params={"audience": app.config["ATE_AUDIENCE"]},
            api_base_url=app.config["ATE_URL"],
            client_kwargs={"token_endpoint_auth_method": "client_secret_post"},
        )


def _migrate_database() -> None:
    engine = inject.instance(Engine)

    alembic_config = alembic.config.Config()
    alembic_config.set_main_option("script_location", "schemes:infrastructure/database/migrations")

    with engine.connect() as connection:
        alembic_config.attributes["connection"] = connection
        command.upgrade(alembic_config, "head")
