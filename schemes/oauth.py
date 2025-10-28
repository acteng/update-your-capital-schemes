from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from authlib.integrations.base_client import InvalidTokenError
from authlib.integrations.base_client.async_app import AsyncOAuth2Mixin, _http_request
from authlib.integrations.base_client.async_openid import AsyncOpenIDMixin
from authlib.integrations.flask_client import OAuth
from authlib.integrations.httpx_client import AsyncOAuth2Client
from authlib.oauth2.rfc6749 import OAuth2Token
from authlib.oauth2.rfc7523 import PrivateKeyJWT
from flask import Flask, Request
from httpx import AsyncClient, Response, Timeout


class _AccessTokenParamsAsyncOAuth2Client(AsyncOAuth2Client):  # type: ignore
    """
    An OAuth2 session that supports extra parameters to fetch access token.

    See: https://github.com/authlib/authlib/issues/783
    """

    async def ensure_active_token(self, token: OAuth2Token = None) -> None:
        access_token_params = self.metadata.get("access_token_params") or {}

        # Copy of AsyncOAuth2Client.ensure_active_token:
        async with self._token_refresh_lock:
            if self.token.is_expired(leeway=self.leeway):
                refresh_token = token.get("refresh_token")
                url = self.metadata.get("token_endpoint")
                if refresh_token and url:
                    await self.refresh_token(url, refresh_token=refresh_token)
                elif self.metadata.get("grant_type") == "client_credentials":
                    access_token = token["access_token"]
                    # Include extra parameters to fetch access token
                    new_token = await self.fetch_token(url, grant_type="client_credentials", **access_token_params)
                    if self.update_token:
                        await self.update_token(new_token, access_token=access_token)
                else:
                    raise InvalidTokenError()


# Workaround: https://github.com/authlib/authlib/issues/819
class AsyncBaseApp:
    client_cls: type | None = None
    OAUTH_APP_CONFIG: Any = None

    async def request(self, method: str, url: str, token: OAuth2Token | None = None, **kwargs: Any) -> Response:
        raise NotImplementedError()

    async def get(self, url: str, **kwargs: Any) -> Response:
        return await self.request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs: Any) -> Response:
        return await self.request("POST", url, **kwargs)


# Workaround: https://github.com/authlib/authlib/issues/822
class ClientAsyncBaseApp(AsyncBaseApp):
    @asynccontextmanager
    def client(self) -> AsyncIterator[AsyncBaseApp]:
        raise NotImplementedError()


class _AsyncBaseAppAdapter(AsyncBaseApp):
    def __init__(self, remote_app: AsyncOAuth2Mixin, client: AsyncClient):
        self._remote_app = remote_app
        self._client = client

    async def request(self, method: str, url: str, token: OAuth2Token | None = None, **kwargs: Any) -> Response:
        response: Response = await _http_request(self._remote_app, self._client, method, url, token, kwargs)
        return response


# Workaround: https://github.com/authlib/authlib/issues/822
class ClientAsyncOAuth2Mixin(AsyncOAuth2Mixin):  # type: ignore
    @asynccontextmanager
    async def client(self) -> AsyncIterator[AsyncBaseApp]:
        metadata = await self.load_server_metadata()
        async with self._get_oauth_client(**metadata) as client:
            yield _AsyncBaseAppAdapter(self, client)


# Workaround: https://github.com/authlib/authlib/issues/818
# Workaround: https://github.com/authlib/authlib/issues/822
class _ClientAccessTokenParamsAsyncFlaskOAuth2App(ClientAsyncOAuth2Mixin, AsyncOpenIDMixin, ClientAsyncBaseApp):  # type: ignore
    # Workaround: https://github.com/authlib/authlib/issues/783
    client_cls = _AccessTokenParamsAsyncOAuth2Client


class OAuthExtension(OAuth):  # type: ignore
    def __init__(self, app: Flask):
        super().__init__(app)
        self._ate_token: OAuth2Token | None = None

        self.register(
            name="govuk",
            client_id=app.config["GOVUK_CLIENT_ID"],
            client_secret=app.config["GOVUK_CLIENT_SECRET"].encode(),
            server_metadata_url=app.config["GOVUK_SERVER_METADATA_URL"],
            client_kwargs={
                "scope": "openid email",
                "token_endpoint_auth_method": PrivateKeyJWT(app.config["GOVUK_TOKEN_ENDPOINT"]),
            },
        )

        if "ATE_URL" in app.config:
            access_token_params = {"audience": app.config["ATE_AUDIENCE"]}
            self.register(
                name="ate",
                client_cls=_ClientAccessTokenParamsAsyncFlaskOAuth2App,
                fetch_token=self._fetch_ate_token,
                update_token=self._update_ate_token,
                client_id=app.config["ATE_CLIENT_ID"],
                client_secret=app.config["ATE_CLIENT_SECRET"],
                server_metadata_url=app.config["ATE_SERVER_METADATA_URL"],
                access_token_params=access_token_params,
                api_base_url=app.config["ATE_URL"],
                client_kwargs={
                    # Workaround: https://github.com/authlib/authlib/issues/780
                    "grant_type": "client_credentials",
                    "token_endpoint_auth_method": "client_secret_post",
                    # Workaround: https://github.com/authlib/authlib/issues/783
                    "access_token_params": access_token_params,
                    "http2": True,
                    "timeout": Timeout(10),
                },
            )

    async def _fetch_ate_token(self, request: Request) -> OAuth2Token:
        if not self._ate_token:
            self._ate_token = await self.ate.fetch_access_token()
        return self._ate_token

    async def _update_ate_token(
        self, token: OAuth2Token, refresh_token: str | None = None, access_token: str | None = None
    ) -> None:
        self._ate_token = token
