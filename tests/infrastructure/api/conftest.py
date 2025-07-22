from typing import Any

import pytest
from authlib.integrations.base_client import BaseApp, FrameworkIntegration, OAuth2Mixin
from authlib.integrations.requests_client import OAuth2Session
from authlib.oauth2.rfc6749 import OAuth2Token

from schemes.infrastructure.api.oauth import RemoteApp


class _StubRemoteApp(OAuth2Mixin, BaseApp):  # type: ignore
    client_cls = OAuth2Session

    # Mimics FlaskAppMixin's behaviour of not requiring the current request
    # See closing note: https://docs.authlib.org/en/latest/client/frameworks.html#fetch-user-oauth-token
    def _get_requested_token(self, request: Any) -> OAuth2Token | None:
        return self._fetch_token() if self._fetch_token else None


@pytest.fixture(name="access_token")
def access_token_fixture() -> str:
    return "dummy_jwt"


@pytest.fixture(name="api_base_url")
def api_base_url_fixture() -> str:
    return "https://api.example"


@pytest.fixture(name="remote_app")
def remote_app_fixture(access_token: str, api_base_url: str) -> RemoteApp:
    return _StubRemoteApp(
        FrameworkIntegration("dummy"),
        fetch_token=lambda: OAuth2Token({"access_token": access_token}),
        api_base_url=api_base_url,
    )
