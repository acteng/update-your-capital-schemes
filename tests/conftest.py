from flask.testing import FlaskClient
import pytest
from schemes import app


@pytest.fixture
def client() -> FlaskClient:
    return app.test_client()
