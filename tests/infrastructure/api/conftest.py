from itertools import groupby
from typing import Any, Generator
from urllib.parse import parse_qsl, urlsplit

import pytest
from authlib.integrations.base_client import BaseApp, FrameworkIntegration, OAuth2Mixin
from authlib.integrations.requests_client import OAuth2Session
from authlib.oauth2.rfc6749 import OAuth2Token
from responses import RequestsMock

from schemes.infrastructure.api.oauth import RemoteApp


class _AllowEmptyQueryParamRequestsMock(RequestsMock):
    """
    A custom Responses that allows empty query parameters to be matched.

    See: https://github.com/getsentry/responses/issues/778
    """

    def _parse_request_params(self, url: str) -> dict[str, str | int | float | list[str | int | float | None]]:
        # Copy of RequestsMock._parse_request_params:
        params: dict[str, str | int | float | list[Any]] = {}
        # Allow empty query parameters
        for key, val in groupby(parse_qsl(urlsplit(url).query, keep_blank_values=True), lambda kv: kv[0]):
            values = list(map(lambda x: x[1], val))
            if len(values) == 1:
                values = values[0]  # type: ignore[assignment]
            params[key] = values
        return params


class _StubRemoteApp(OAuth2Mixin, BaseApp):  # type: ignore
    client_cls = OAuth2Session

    # Mimics FlaskAppMixin's behaviour of not requiring the current request
    # See closing note: https://docs.authlib.org/en/latest/client/frameworks.html#fetch-user-oauth-token
    def _get_requested_token(self, request: Any) -> OAuth2Token | None:
        return self._fetch_token() if self._fetch_token else None


@pytest.fixture(name="responses")
def responses_fixture() -> Generator[RequestsMock]:
    with _AllowEmptyQueryParamRequestsMock() as mock:
        yield mock


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
