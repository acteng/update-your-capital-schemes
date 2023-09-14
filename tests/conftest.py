from flask import Flask
from flask.testing import FlaskClient
import pytest
from schemes import create_app


@pytest.fixture
def app() -> Flask:
    return create_app()


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()
