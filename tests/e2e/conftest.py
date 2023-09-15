from flask import Flask
import pytest
from schemes import create_app
import sys


@pytest.fixture(scope="session")
def app() -> Flask:
    return create_app()


@pytest.fixture(scope="session", autouse=True)
def set_mac_multiprocessing() -> None:
    if sys.platform == 'darwin':
        import multiprocessing
        multiprocessing.set_start_method("fork")
