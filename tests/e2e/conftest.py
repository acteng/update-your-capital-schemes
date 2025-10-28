import json
import multiprocessing
import socket
import sys
from dataclasses import dataclass
from tempfile import TemporaryDirectory
from typing import Any, Callable, Generator

import pytest
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat, PublicFormat
from flask import Flask
from playwright.sync_api import Browser, BrowserContext, BrowserType, Playwright, sync_playwright
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


@dataclass(frozen=True)
class _Client:
    client_id: str
    client_secret: str
    scope: str


@dataclass(frozen=True)
class _ResourceServer:
    identifier: str


@pytest.fixture(name="debug", scope="package")
def debug_fixture() -> bool:
    return False


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
    debug: bool,
    api_key: str,
    oidc_server: LiveServer,
    api_server: LiveServer,
    authorization_server: LiveServer,
    resource_server: _ResourceServer,
    app_oauth_client: _Client,
) -> Generator[Flask]:
    port = _get_random_port()
    client_id = "app"
    private_key, public_key = _generate_key_pair()

    config = {
        "DEBUG": debug,
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
            "ATE_AUDIENCE": resource_server.identifier,
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
def app_client_fixture(live_server: LiveServer, api_key: str) -> Generator[AppClient]:
    client = AppClient(_get_url(live_server), api_key)
    yield client
    client.clear_schemes()
    client.clear_users()
    client.clear_authorities()


@pytest.fixture(name="oidc_server_app", scope="package")
def oidc_server_app_fixture(debug: bool) -> OidcServerApp:
    port = _get_random_port()
    return oidc_server_create_app({"DEBUG": debug, "TESTING": True, "SERVER_NAME": f"localhost:{port}"})


@pytest.fixture(name="oidc_server", scope="package")
def oidc_server_fixture(oidc_server_app: OidcServerApp, request: FixtureRequest) -> Generator[LiveServer]:
    server = LiveServer(oidc_server_app, "localhost", _get_port(oidc_server_app), 5, True)
    server.start()
    request.addfinalizer(server.stop)
    yield server


@pytest.fixture(name="oidc_client")
def oidc_client_fixture(oidc_server: LiveServer) -> Generator[OidcClient]:
    client = OidcClient(_get_url(oidc_server))
    yield client
    client.clear_users()


@pytest.fixture(name="api_server_app", scope="package")
def api_server_app_fixture(debug: bool, authorization_server: LiveServer, resource_server: _ResourceServer) -> Flask:
    port = _get_random_port()
    return api_server_create_app(
        {
            "DEBUG": debug,
            "TESTING": True,
            "SERVER_NAME": f"localhost:{port}",
            "OIDC_SERVER_METADATA_URL": authorization_server.app.url_for("openid_configuration", _external=True),
            "RESOURCE_SERVER_IDENTIFIER": resource_server.identifier,
        }
    )


@pytest.fixture(name="api_server", scope="package")
def api_server_fixture(api_server_app: Flask, request: FixtureRequest) -> LiveServer:
    server = LiveServer(api_server_app, "localhost", _get_port(api_server_app), 5, True)
    server.start()
    request.addfinalizer(server.stop)
    return server


@pytest.fixture(name="api_client", scope="package")
def api_client_fixture(
    api_server: LiveServer,
    authorization_server: LiveServer,
    resource_server: _ResourceServer,
    tests_oauth_client: _Client,
) -> Generator[ApiClient]:
    client = ApiClient(
        url=_get_url(api_server),
        client_id=tests_oauth_client.client_id,
        client_secret=tests_oauth_client.client_secret,
        token_endpoint=authorization_server.app.url_for("token", _external=True),
        scope="tests",
        audience=resource_server.identifier,
    )
    yield client
    client.clear_schemes()
    client.clear_milestones()
    client.clear_authorities()
    client.clear_funding_programmes()


@pytest.fixture(name="resource_server", scope="package")
def resource_server_fixture() -> _ResourceServer:
    return _ResourceServer(identifier="https://api.example")


@pytest.fixture(name="app_oauth_client", scope="package")
def app_oauth_client_fixture() -> _Client:
    return _Client(client_id="app", client_secret="secret", scope="")


@pytest.fixture(name="tests_oauth_client", scope="package")
def tests_oauth_client_fixture() -> _Client:
    return _Client(client_id="tests", client_secret="secret", scope="tests")


@pytest.fixture(name="authorization_server_app", scope="package")
def authorization_server_app_fixture(
    debug: bool, app_oauth_client: _Client, tests_oauth_client: _Client, resource_server: _ResourceServer
) -> Flask:
    port = _get_random_port()
    return authorization_server_create_app(
        {
            "DEBUG": debug,
            "TESTING": True,
            "SERVER_NAME": f"localhost:{port}",
            "CLIENTS": [
                {
                    "clientId": app_oauth_client.client_id,
                    "clientSecret": app_oauth_client.client_secret,
                    "scope": app_oauth_client.scope,
                },
                {
                    "clientId": tests_oauth_client.client_id,
                    "clientSecret": tests_oauth_client.client_secret,
                    "scope": tests_oauth_client.scope,
                },
            ],
            "RESOURCE_SERVER_IDENTIFIER": resource_server.identifier,
        }
    )


@pytest.fixture(name="authorization_server", scope="package")
def authorization_server_fixture(authorization_server_app: Flask, request: FixtureRequest) -> LiveServer:
    server = LiveServer(authorization_server_app, "localhost", _get_port(authorization_server_app), 5, True)
    server.start()
    request.addfinalizer(server.stop)
    return server


# Copy of pytest_playwright.pytest_playwright.browser_context_args to narrow scope for pytest-asyncio compatibility
# See: https://github.com/microsoft/playwright-pytest/issues/167
# See: https://github.com/microsoft/playwright-pytest/issues/289
@pytest.fixture(name="browser_context_args", scope="package")
def browser_context_args_fixture(
    pytestconfig: Any,
    playwright: Playwright,
    device: str | None,
    base_url: str | None,
    _pw_artifacts_folder: TemporaryDirectory[str],
) -> dict[str, str]:
    context_args = {}
    if device:
        context_args.update(playwright.devices[device])
    if base_url:
        context_args["base_url"] = base_url

    video_option = pytestconfig.getoption("--video")
    capture_video = video_option in ["on", "retain-on-failure"]
    if capture_video:
        context_args["record_video_dir"] = _pw_artifacts_folder.name

    return context_args


@pytest.fixture(name="browser_context_args", scope="package")
def custom_browser_context_args_fixture(
    browser_context_args: dict[str, Any], live_server: LiveServer
) -> dict[str, Any]:
    browser_context_args["base_url"] = _get_url(live_server)
    return browser_context_args


@pytest.fixture(name="context")
def browser_context_fixture(context: BrowserContext) -> Generator[BrowserContext]:
    context.set_default_timeout(5_000)
    yield context


# Copy of pytest_playwright.pytest_playwright.playwright to narrow scope for pytest-asyncio compatibility
# See: https://github.com/microsoft/playwright-pytest/issues/167
# See: https://github.com/microsoft/playwright-pytest/issues/289
@pytest.fixture(name="playwright", scope="package")
def playwright_fixture() -> Generator[Playwright]:
    pw = sync_playwright().start()
    yield pw
    pw.stop()


# Copy of pytest_playwright.pytest_playwright.browser_type to narrow scope for pytest-asyncio compatibility
# See: https://github.com/microsoft/playwright-pytest/issues/167
# See: https://github.com/microsoft/playwright-pytest/issues/289
@pytest.fixture(name="browser_type", scope="package")
def browser_type_fixture(playwright: Playwright, browser_name: str) -> BrowserType:
    browser_type: BrowserType = getattr(playwright, browser_name)
    return browser_type


# Copy of pytest_playwright.pytest_playwright.launch_browser to narrow scope for pytest-asyncio compatibility
# See: https://github.com/microsoft/playwright-pytest/issues/167
# See: https://github.com/microsoft/playwright-pytest/issues/289
@pytest.fixture(name="launch_browser", scope="package")
def launch_browser_fixture(
    browser_type_launch_args: dict[str, Any], browser_type: BrowserType, connect_options: dict[str, Any] | None
) -> Callable[..., Browser]:
    def launch(**kwargs: dict[str, Any]) -> Browser:
        launch_options = {**browser_type_launch_args, **kwargs}
        if connect_options:
            browser = browser_type.connect(
                **(
                    {
                        **connect_options,
                        "headers": {
                            "x-playwright-launch-options": json.dumps(launch_options),
                            **(connect_options.get("headers") or {}),
                        },
                    }
                )
            )
        else:
            browser = browser_type.launch(**launch_options)
        return browser

    return launch


# Copy of pytest_playwright.pytest_playwright.browser to narrow scope for pytest-asyncio compatibility
# See: https://github.com/microsoft/playwright-pytest/issues/167
# See: https://github.com/microsoft/playwright-pytest/issues/289
@pytest.fixture(name="browser", scope="package")
def browser_fixture(launch_browser: Callable[[], Browser]) -> Generator[Browser]:
    browser = launch_browser()
    yield browser
    browser.close()


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
