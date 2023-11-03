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

from schemes import auth, authorities, schemes, start, users
from schemes.authorities.services import (
    AuthorityRepository,
    DatabaseAuthorityRepository,
)
from schemes.config import DevConfig
from schemes.users.domain import User
from schemes.users.services import DatabaseUserRepository, UserRepository


def create_app(test_config: Mapping[str, Any] | None = None) -> Flask:
    env = os.environ.get("FLASK_ENV", DevConfig.name)

    app = Flask(__name__)
    app.config.from_object(f"schemes.config.{env.title()}Config")
    app.config.from_prefixed_env()
    app.config.from_mapping(test_config)

    def bindings(binder: Binder) -> None:
        binder.bind(Config, app.config)
        _bindings(binder)

    inject.configure(bindings, bind_in_runtime=False)

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
    inject.clear()


def _bindings(binder: Binder) -> None:
    binder.bind_to_constructor(Engine, _create_engine)
    binder.bind_to_constructor(AuthorityRepository, DatabaseAuthorityRepository)
    binder.bind_to_constructor(UserRepository, DatabaseUserRepository)


@inject.autoparams()
def _create_engine(config: Config) -> Engine:
    engine = create_engine(config["SQLALCHEMY_DATABASE_URI"])

    def enforce_sqlite_foreign_keys(dbapi_connection: DBAPIConnection, _connection_record: ConnectionPoolEntry) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    if engine.dialect.name == SQLiteDialect.name:
        event.listen(Engine, "connect", enforce_sqlite_foreign_keys)

    return engine


def _configure_error_pages(app: Flask) -> None:
    @app.errorhandler(404)
    def not_found(error: Exception) -> Response:  # pylint: disable=unused-argument
        return Response(render_template("404.html"), status=404)

    @app.errorhandler(500)
    def internal_server_error(error: Exception) -> Response:  # pylint: disable=unused-argument
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
    alembic_config.set_main_option("script_location", "schemes:migrations")

    with engine.connect() as connection:
        alembic_config.attributes["connection"] = connection
        command.upgrade(alembic_config, "head")
