from typing import Any, Mapping

import pytest
from flask import Flask
from flask.testing import FlaskClient

from schemes import create_app


@pytest.fixture(name="config")
def config_fixture() -> Mapping[str, Any]:
    return {
        "TESTING": True,
        "GOVUK_CLIENT_ID": "test",
        "GOVUK_CLIENT_SECRET": "test",
        "GOVUK_SERVER_METADATA_URL": "test",
        "GOVUK_TOKEN_ENDPOINT": "test",
        "GOVUK_PROFILE_URL": "test",
        "GOVUK_END_SESSION_ENDPOINT": "test",
    }


@pytest.fixture(name="app")
def app_fixture(config: Mapping[str, Any]) -> Flask:
    return create_app(config)


@pytest.fixture(name="client")
def client_fixture(app: Flask) -> FlaskClient:
    return app.test_client()
