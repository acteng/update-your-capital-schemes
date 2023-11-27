import os
from typing import Any, Mapping

import alembic.config
import inject
from alembic import command
from authlib.integrations.flask_client import OAuth
from authlib.oauth2.rfc7523 import PrivateKeyJWT
from flask import Config, Flask, Response, render_template, url_for
from inject import Binder
from jinja2 import ChoiceLoader, FileSystemLoader, PackageLoader, PrefixLoader
from sqlalchemy import Engine, create_engine, event
from sqlalchemy.dialects.sqlite.base import SQLiteDialect
from sqlalchemy.engine.interfaces import DBAPIConnection
from sqlalchemy.pool import ConnectionPoolEntry

from schemes.config import DevConfig
from schemes.domain.authorities import AuthorityRepository
from schemes.domain.schemes import SchemeRepository
from schemes.domain.users import UserRepository
from schemes.infrastructure.authorities import DatabaseAuthorityRepository
from schemes.infrastructure.schemes import DatabaseSchemeRepository
from schemes.infrastructure.users import DatabaseUserRepository
from schemes.views import auth, authorities, schemes, start, users


def create_app(test_config: Mapping[str, Any] | None = None) -> Flask:
    env = os.environ.get("FLASK_ENV", DevConfig.name)

    app = Flask(__name__, static_folder="views/static", template_folder="views/templates")
    app.config.from_object(f"schemes.config.{env.title()}Config")
    app.config.from_prefixed_env()
    app.config.from_mapping(test_config)

    def bindings(binder: Binder) -> None:
        binder.bind(Config, app.config)
        _bindings(binder)

    inject.configure(bindings, bind_in_runtime=False)

    _configure_jinja(app)
    _configure_error_pages(app)
    _configure_govuk_frontend(app)
    _configure_oidc(app)

    app.register_blueprint(start.bp)
    app.register_blueprint(auth.bp, url_prefix="/auth")
    app.register_blueprint(authorities.bp, url_prefix="/authorities")
    app.register_blueprint(schemes.bp, url_prefix="/schemes")
    app.register_blueprint(users.bp, url_prefix="/users")

    _migrate_database()

    return app


def destroy_app(_app: Flask) -> None:
    event.remove(Engine, "connect", _enforce_sqlite_foreign_keys)
    inject.clear()


def _bindings(binder: Binder) -> None:
    binder.bind_to_constructor(Engine, _create_engine)
    binder.bind_to_constructor(AuthorityRepository, DatabaseAuthorityRepository)
    binder.bind_to_constructor(UserRepository, DatabaseUserRepository)
    binder.bind_to_constructor(SchemeRepository, DatabaseSchemeRepository)


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


def _configure_jinja(app: Flask) -> None:
    app.jinja_options["extensions"] = ["jinja2.ext.do"]


def _configure_error_pages(app: Flask) -> None:
    @app.errorhandler(404)
    def not_found(_error: Exception) -> Response:
        return Response(render_template("404.html"), status=404)

    @app.errorhandler(500)
    def internal_server_error(_error: Exception) -> Response:
        return Response(render_template("500.html"), status=500)


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


def _migrate_database() -> None:
    engine = inject.instance(Engine)

    alembic_config = alembic.config.Config()
    alembic_config.set_main_option("script_location", "schemes:infrastructure/migrations")

    with engine.connect() as connection:
        alembic_config.attributes["connection"] = connection
        command.upgrade(alembic_config, "head")
