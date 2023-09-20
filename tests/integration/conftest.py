from flask import Flask
from flask.testing import FlaskClient
import pytest
from schemes import create_app


@pytest.fixture(name="app")
def app_fixture() -> Flask:
    return create_app()


@pytest.fixture(name="client")
def client_fixture(app: Flask) -> FlaskClient:
    return app.test_client()
