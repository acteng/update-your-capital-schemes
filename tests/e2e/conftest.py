from flask import Flask
import pytest
from schemes import create_app


@pytest.fixture(scope="session")
def app() -> Flask:
    return create_app()
