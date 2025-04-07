import multiprocessing
import socket
import sys
from dataclasses import dataclass
from typing import Any, Generator

import pytest
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)
from flask import Flask
from playwright.sync_api import BrowserContext
from pytest import FixtureRequest
from pytest_flask.live_server import LiveServer

from schemes import create_app, destroy_app
from tests.e2e.api_client import ApiClient
from tests.e2e.api_server.app import create_app as api_server_create_app
from tests.e2e.app_client import AppClient
from tests.e2e.oauth_server.app import create_app as authorization_server_create_app
from tests.e2e.oidc_server.app import OidcServerApp
from tests.e2e.oidc_server.app import create_app as oidc_server_create_app
from tests.e2e.oidc_server.clients import StubClient
from tests.e2e.oidc_server.web_client import OidcClient


@dataclass
class _Client:
    client_id: str
    client_secret: str


@pytest.fixture(name="configure_live_server", scope="package", autouse=True)
def configure_live_server_fixture() -> None:
    if sys.platform == "darwin":
        multiprocessing.set_start_method("fork")


@pytest.fixture(name="api_key", scope="package")
def api_key_fixture() -> str:
    return "api-key"


@pytest.fixture(name="app", scope="package", params=[False, True], ids=["database", "api"])
def app_fixture(
    request: FixtureRequest,
    api_key: str,
    oidc_server: LiveServer,
    api_server: LiveServer,
    authorization_server: LiveServer,
    resource_server_identifier: str,
    app_oauth_client: _Client,
) -> Generator[Flask, Any, Any]:
    port = _get_random_port()
    client_id = "app"
    private_key, public_key = _generate_key_pair()

    config = {
        "TESTING": True,
        "SECRET_KEY": b"secret_key",
        "SERVER_NAME": f"localhost:{port}",
        "LIVESERVER_PORT": port,
        "API_KEY": api_key,
        "GOVUK_CLIENT_ID": client_id,
        "GOVUK_CLIENT_SECRET": private_key.decode(),
        "GOVUK_SERVER_METADATA_URL": oidc_server.app.url_for("openid_configuration", _external=True),
        "GOVUK_TOKEN_ENDPOINT": oidc_server.app.url_for("token", _external=True),
        "GOVUK_END_SESSION_ENDPOINT": oidc_server.app.url_for("logout", _external=True),
    }

    if request.param:
        config |= {
            "ATE_URL": _get_url(api_server),
            "ATE_CLIENT_ID": app_oauth_client.client_id,
            "ATE_CLIENT_SECRET": app_oauth_client.client_secret,
            "ATE_SERVER_METADATA_URL": authorization_server.app.url_for("openid_configuration", _external=True),
            "ATE_AUDIENCE": resource_server_identifier,
        }

    app = create_app(config)

    app_oidc_client = StubClient(
        client_id=client_id,
        redirect_uri=app.url_for("auth.callback", _external=True),
        public_key=public_key.decode(),
        scope="openid email",
    )

    oidc_client = OidcClient(_get_url(oidc_server))
    oidc_client.add_client(app_oidc_client)
    yield app
    destroy_app(app)
    oidc_client.clear_clients()


@pytest.fixture(name="app_client")
def app_client_fixture(live_server: LiveServer, api_key: str) -> Generator[AppClient, Any, Any]:
    client = AppClient(_get_url(live_server), api_key)
    yield client
    client.clear_schemes()
    client.clear_users()
    client.clear_authorities()


@pytest.fixture(name="oidc_server_app", scope="package")
def oidc_server_app_fixture() -> OidcServerApp:
    port = _get_random_port()
    return oidc_server_create_app({"TESTING": True, "SERVER_NAME": f"localhost:{port}"})


@pytest.fixture(name="oidc_server", scope="package")
def oidc_server_fixture(oidc_server_app: OidcServerApp, request: FixtureRequest) -> Generator[LiveServer, Any, Any]:
    server = LiveServer(oidc_server_app, "localhost", _get_port(oidc_server_app), 5, True)
    server.start()
    request.addfinalizer(server.stop)
    yield server


@pytest.fixture(name="oidc_client")
def oidc_client_fixture(oidc_server: LiveServer) -> Generator[OidcClient, Any, Any]:
    client = OidcClient(_get_url(oidc_server))
    yield client
    client.clear_users()


@pytest.fixture(name="api_server_app", scope="package")
def api_server_app_fixture(authorization_server: LiveServer, resource_server_identifier: str) -> Flask:
    port = _get_random_port()
    return api_server_create_app(
        {
            "TESTING": True,
            "SERVER_NAME": f"localhost:{port}",
            "OIDC_SERVER_METADATA_URL": authorization_server.app.url_for("openid_configuration", _external=True),
            "RESOURCE_SERVER_IDENTIFIER": resource_server_identifier,
        }
    )


@pytest.fixture(name="api_server", scope="package")
def api_server_fixture(api_server_app: Flask, request: FixtureRequest) -> LiveServer:
    server = LiveServer(api_server_app, "localhost", _get_port(api_server_app), 5, True)
    server.start()
    request.addfinalizer(server.stop)
    return server


@pytest.fixture(name="api_client")
def api_client_fixture(api_server: LiveServer) -> Generator[ApiClient]:
    client = ApiClient(_get_url(api_server))
    yield client
    client.clear_authorities()


@pytest.fixture(name="resource_server_identifier", scope="package")
def resource_server_identifier_fixture() -> str:
    return "https://api.example"


@pytest.fixture(name="app_oauth_client", scope="package")
def app_oauth_client_fixture() -> _Client:
    return _Client(client_id="stub_client_id", client_secret="stub_client_secret")


@pytest.fixture(name="authorization_server_app", scope="package")
def authorization_server_app_fixture(app_oauth_client: _Client, resource_server_identifier: str) -> Flask:
    port = _get_random_port()
    return authorization_server_create_app(
        {
            "TESTING": True,
            "SERVER_NAME": f"localhost:{port}",
            "CLIENT_ID": app_oauth_client.client_id,
            "CLIENT_SECRET": app_oauth_client.client_secret,
            "RESOURCE_SERVER_IDENTIFIER": resource_server_identifier,
        }
    )


@pytest.fixture(name="authorization_server", scope="package")
def authorization_server_fixture(authorization_server_app: Flask, request: FixtureRequest) -> LiveServer:
    server = LiveServer(authorization_server_app, "localhost", _get_port(authorization_server_app), 5, True)
    server.start()
    request.addfinalizer(server.stop)
    return server


@pytest.fixture(name="browser_context_args", scope="package")
def browser_context_args_fixture(browser_context_args: dict[str, str], live_server: LiveServer) -> dict[str, str]:
    browser_context_args["base_url"] = _get_url(live_server)
    return browser_context_args


@pytest.fixture(name="context")
def browser_context_fixture(context: BrowserContext) -> Generator[BrowserContext, None, None]:
    context.set_default_timeout(5_000)
    yield context


def _get_url(live_server: LiveServer) -> str:
    return f"http://{live_server.host}:{live_server.port}"


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
