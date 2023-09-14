from flask.testing import FlaskClient
import pytest
from app import app


@pytest.fixture
def client() -> FlaskClient:
    return app.test_client()
