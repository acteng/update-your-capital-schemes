from typing import Any, Generator, Mapping

import inject
import pytest
from flask import Flask
from flask.testing import FlaskClient
from inject import Binder

from schemes import create_app
from schemes.authorities import AuthorityRepository
from schemes.users.services import UserRepository
from tests.integration.fakes import MemoryAuthorityRepository, MemoryUserRepository


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
    inject.clear()


@pytest.fixture(name="client")
def client_fixture(app: Flask) -> FlaskClient:
    return app.test_client()


def _bindings(binder: Binder) -> None:
    binder.bind(AuthorityRepository, MemoryAuthorityRepository())
    binder.bind(UserRepository, MemoryUserRepository())
