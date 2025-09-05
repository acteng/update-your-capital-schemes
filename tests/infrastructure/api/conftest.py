from typing import Any

import pytest
from authlib.integrations.base_client import FrameworkIntegration
from authlib.integrations.base_client.async_app import AsyncOAuth2Mixin
from authlib.integrations.httpx_client import AsyncOAuth2Client
from authlib.oauth2.rfc6749 import OAuth2Token

from schemes.oauth import AsyncBaseApp


class _StubRemoteApp(AsyncOAuth2Mixin, AsyncBaseApp):  # type: ignore
    client_cls = AsyncOAuth2Client


@pytest.fixture(name="access_token")
def access_token_fixture() -> str:
    return "dummy_jwt"


@pytest.fixture(name="api_base_url")
def api_base_url_fixture() -> str:
    return "https://api.example"


@pytest.fixture(name="remote_app")
def remote_app_fixture(access_token: str, api_base_url: str) -> AsyncBaseApp:
    async def fetch_token(request: Any) -> OAuth2Token:
        return OAuth2Token({"access_token": access_token})

    return _StubRemoteApp(FrameworkIntegration("dummy"), fetch_token=fetch_token, api_base_url=api_base_url)
