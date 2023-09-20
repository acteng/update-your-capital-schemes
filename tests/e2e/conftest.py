import multiprocessing
import sys
from flask import Flask
import pytest
from schemes import create_app


@pytest.fixture(name="app", scope="session")
def app_fixture() -> Flask:
    return create_app()


@pytest.fixture(name="set_mac_multiprocessing", scope="session", autouse=True)
def set_mac_multiprocessing_fixture() -> None:
    if sys.platform == 'darwin':
        multiprocessing.set_start_method("fork")
