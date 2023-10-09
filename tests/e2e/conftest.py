import multiprocessing
import os
import socket
import sys
from typing import Any, Generator

import pytest
from _pytest.mark import Mark
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)
from flask import Flask
from pytest_flask.live_server import LiveServer

from schemes import create_app
from tests.e2e.oidc_server.app import OidcServerFlask
from tests.e2e.oidc_server.app import create_app as oidc_server_create_app
from tests.e2e.oidc_server.clients import StubClient
from tests.e2e.oidc_server.users import StubUser


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "oidc_user(**kwargs): Add an OIDC Stub user to the OIDC Server instance by passing an id and email",
    )


@pytest.fixture(name="app", scope="class")
def app_fixture(oidc_server_app: OidcServerFlask) -> Flask:
    port = _get_random_port()
    client_id = "app"
    private_key, public_key = _generate_key_pair()

    app = create_app(
        {
            "TESTING": True,
            "SERVER_NAME": f"localhost:{port}",
            "LIVESERVER_PORT": port,
            "GOVUK_CLIENT_ID": client_id,
            "GOVUK_CLIENT_SECRET": private_key.decode(),
            "GOVUK_SERVER_METADATA_URL": oidc_server_app.url_for("openid_configuration", _external=True),
            "GOVUK_TOKEN_ENDPOINT": oidc_server_app.url_for("token", _external=True),
            "GOVUK_END_SESSION_ENDPOINT": oidc_server_app.url_for("logout", _external=True),
        }
    )

    oidc_server_app.add_client(
        StubClient(
            client_id=client_id,
            redirect_uri=app.url_for("auth.callback", _external=True),
            public_key=public_key.decode(),
            scope="openid email",
        )
    )

    return app


@pytest.fixture(name="configure_live_server", scope="session", autouse=True)
def configure_live_server_fixture() -> None:
    if sys.platform == "darwin":
        multiprocessing.set_start_method("fork")


@pytest.fixture(name="oidc_server_app", scope="class")
def oidc_server_app_fixture(request: pytest.FixtureRequest) -> OidcServerFlask:
    os.environ["AUTHLIB_INSECURE_TRANSPORT"] = "true"
    port = _get_random_port()

    oidc_server_app = oidc_server_create_app({"TESTING": True, "SERVER_NAME": f"localhost:{port}"})

    user_marker: Mark | None = next(request.node.iter_markers(name="oidc_user"), None)
    if user_marker is not None:
        oidc_server_app.add_user(StubUser(**user_marker.kwargs))

    return oidc_server_app


@pytest.fixture(name="oidc_server", scope="class")
def oidc_server_fixture(
    oidc_server_app: OidcServerFlask, request: pytest.FixtureRequest
) -> Generator[LiveServer, Any, Any]:
    server = LiveServer(oidc_server_app, "localhost", _get_port(oidc_server_app), 5, True)
    server.start()
    request.addfinalizer(server.stop)
    yield server


def _get_port(app: Flask) -> int:
    return int(app.config["SERVER_NAME"].split(":")[1])


def _get_random_port() -> int:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("", 0))
    port: int = sock.getsockname()[1]
    sock.close()
    return port


def _generate_key_pair() -> tuple[bytes, bytes]:
    key_pair = rsa.generate_private_key(backend=default_backend(), public_exponent=65537, key_size=2048)
    private_key = key_pair.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())
    public_key = key_pair.public_key().public_bytes(Encoding.OpenSSH, PublicFormat.OpenSSH)
    return private_key, public_key
