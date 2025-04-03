from dataclasses import dataclass

import pytest
from authlib.integrations.base_client import BaseApp, FrameworkIntegration, OAuth2Mixin
from authlib.integrations.requests_client import OAuth2Session

from schemes.infrastructure.api.oauth import RemoteApp
from tests.infrastructure.api.oauth import StubAuthorizationServer


@dataclass
class _Client:
    client_id: str
    client_secret: str


class _StubRemoteApp(OAuth2Mixin, BaseApp):  # type: ignore
    client_cls = OAuth2Session


@pytest.fixture(name="client")
def client_fixture() -> _Client:
    return _Client(client_id="stub_client_id", client_secret="stub_client_secret")


@pytest.fixture(name="resource_server_identifier")
def resource_server_identifier_fixture() -> str:
    return "https://api.example"


@pytest.fixture(name="authorization_server")
def authorization_server_fixture(client: _Client, resource_server_identifier: str) -> StubAuthorizationServer:
    return StubAuthorizationServer(
        client_id=client.client_id,
        client_secret=client.client_secret,
        resource_server_identifier=resource_server_identifier,
    )


@pytest.fixture(name="api_base_url")
def api_base_url_fixture() -> str:
    return "https://api.example"


@pytest.fixture(name="remote_app")
def remote_app_fixture(
    authorization_server: StubAuthorizationServer, client: _Client, resource_server_identifier: str, api_base_url: str
) -> RemoteApp:
    return _StubRemoteApp(
        FrameworkIntegration("dummy"),
        client_id=client.client_id,
        client_secret=client.client_secret,
        access_token_url=authorization_server.token_endpoint,
        access_token_params={"audience": resource_server_identifier},
        api_base_url=api_base_url,
        client_kwargs={"token_endpoint_auth_method": "client_secret_post"},
    )
