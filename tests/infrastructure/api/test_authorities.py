from __future__ import annotations

from dataclasses import dataclass

import pytest
import responses
from authlib.integrations.base_client import BaseApp, FrameworkIntegration, OAuth2Mixin
from authlib.integrations.requests_client import OAuth2Session
from responses.matchers import header_matcher

from schemes.infrastructure.api.authorities import ApiAuthorityRepository
from tests.infrastructure.api.oauth import StubAuthorizationServer


class TestApiAuthorityRepository:
    @pytest.fixture(name="client")
    def client_fixture(self) -> _Client:
        return _Client(client_id="stub_client_id", client_secret="stub_client_secret")

    @pytest.fixture(name="authorization_server")
    def authorization_server_fixture(self, client: _Client) -> StubAuthorizationServer:
        return StubAuthorizationServer(
            client_id=client.client_id,
            client_secret=client.client_secret,
            resource_server_identifier="https://api.example",
        )

    @pytest.fixture(name="authorities")
    def authorities_fixture(
        self, authorization_server: StubAuthorizationServer, client: _Client
    ) -> ApiAuthorityRepository:
        remote_app = _StubRemoteApp(
            FrameworkIntegration("dummy"),
            client_id=client.client_id,
            client_secret=client.client_secret,
            access_token_url=authorization_server.token_endpoint,
            access_token_params={"audience": "https://api.example"},
            api_base_url="https://api.example",
            client_kwargs={"token_endpoint_auth_method": "client_secret_post"},
        )
        return ApiAuthorityRepository(remote_app)

    @responses.activate
    def test_get_authority(
        self, authorization_server: StubAuthorizationServer, authorities: ApiAuthorityRepository
    ) -> None:
        authorization_server.given_token_endpoint_returns_access_token("dummy_jwt")
        responses.get(
            "https://api.example/authorities/LIV",
            match=[header_matcher({"Authorization": "Bearer dummy_jwt"})],
            json={"abbreviation": "LIV", "fullName": "Liverpool City Region Combined Authority"},
        )

        authority = authorities.get("LIV")

        assert (
            authority
            and authority.abbreviation == "LIV"
            and authority.name == "Liverpool City Region Combined Authority"
        )


@dataclass
class _Client:
    client_id: str
    client_secret: str


class _StubRemoteApp(OAuth2Mixin, BaseApp):  # type: ignore
    client_cls = OAuth2Session
