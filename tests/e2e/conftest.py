import multiprocessing
import sys

import pytest
from flask import Flask

from schemes import create_app


@pytest.fixture(name="app", scope="session")
def app_fixture() -> Flask:
    return create_app({"TESTING": True})


@pytest.fixture(name="configure_live_server", scope="session", autouse=True)
def configure_live_server_fixture() -> None:
    if sys.platform == "darwin":
        multiprocessing.set_start_method("fork")
