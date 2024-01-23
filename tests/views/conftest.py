import pytest
from flask import Flask


@pytest.fixture(name="app")
def app_fixture() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = b"test"
    return app
