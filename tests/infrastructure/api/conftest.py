from typing import Any

import pytest
from authlib.integrations.base_client import FrameworkIntegration
from authlib.integrations.httpx_client import AsyncOAuth2Client
from authlib.oauth2.rfc6749 import OAuth2Token

from schemes.oauth import ClientAsyncBaseApp, ClientAsyncOAuth2Mixin


class StubRemoteApp(ClientAsyncOAuth2Mixin, ClientAsyncBaseApp):
    client_cls = AsyncOAuth2Client
    client_count = 0

    def _get_oauth_client(self, **metadata: Any) -> AsyncOAuth2Client:
        self.client_count += 1
        return super()._get_oauth_client(**metadata)


@pytest.fixture(name="access_token")
def access_token_fixture() -> str:
    return "dummy_jwt"


@pytest.fixture(name="api_base_url")
def api_base_url_fixture() -> str:
    return "https://api.example"


@pytest.fixture(name="remote_app")
def remote_app_fixture(access_token: str, api_base_url: str) -> StubRemoteApp:
    async def fetch_token(request: Any) -> OAuth2Token:
        return OAuth2Token({"access_token": access_token})

    return StubRemoteApp(FrameworkIntegration("dummy"), fetch_token=fetch_token, api_base_url=api_base_url)
