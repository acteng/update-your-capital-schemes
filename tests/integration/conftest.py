from typing import Any, Generator, Mapping

import inject
import pytest
from flask import Flask, session
from flask.testing import FlaskClient
from flask_wtf.csrf import generate_csrf
from inject import Binder

from schemes import _get_current_user, create_app, destroy_app
from schemes.domain.authorities import AuthorityRepository
from schemes.domain.schemes import SchemeRepository
from schemes.domain.users import User, UserRepository
from schemes.infrastructure.clock import Clock, FakeClock
from tests.integration.fakes import (
    MemoryAuthorityRepository,
    MemorySchemeRepository,
    MemoryUserRepository,
)


@pytest.fixture(name="config")
def config_fixture() -> Mapping[str, Any]:
    return {
        "TESTING": True,
        "SECRET_KEY": b"secret_key",
        "GOVUK_CLIENT_ID": "test",
        "GOVUK_CLIENT_SECRET": "test",
        "GOVUK_SERVER_METADATA_URL": "test",
        "GOVUK_TOKEN_ENDPOINT": "test",
        "GOVUK_PROFILE_URL": "test",
        "GOVUK_END_SESSION_ENDPOINT": "test",
    }


@pytest.fixture(name="app")
def app_fixture(config: Mapping[str, Any]) -> Generator[Flask, Any, Any]:
    app = create_app(config)
    inject.clear_and_configure(_bindings, bind_in_runtime=False)
    yield app
    destroy_app(app)


@pytest.fixture(name="client")
def client_fixture(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture(name="csrf_token")
def csrf_token_fixture(client: FlaskClient) -> str:
    with client.session_transaction() as client_session:
        csrf_token: str = generate_csrf()
        client_session["csrf_token"] = session["csrf_token"]
    return csrf_token


@pytest.fixture(name="clock")
def clock_fixture(app: Flask) -> Clock:
    return inject.instance(Clock)


@pytest.fixture(name="authorities")
def authorities_fixture(app: Flask) -> AuthorityRepository:
    return inject.instance(AuthorityRepository)


@pytest.fixture(name="users")
def users_fixture(app: Flask) -> UserRepository:
    return inject.instance(UserRepository)


@pytest.fixture(name="schemes")
def schemes_fixture(app: Flask) -> SchemeRepository:
    return inject.instance(SchemeRepository)


def _bindings(binder: Binder) -> None:
    binder.bind(Clock, FakeClock())
    binder.bind(AuthorityRepository, MemoryAuthorityRepository())
    binder.bind(UserRepository, MemoryUserRepository())
    binder.bind(SchemeRepository, MemorySchemeRepository())
    binder.bind_to_provider(User, _get_current_user)
