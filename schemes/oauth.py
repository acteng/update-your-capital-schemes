from authlib.integrations.base_client import BaseApp, InvalidTokenError
from authlib.integrations.base_client.async_app import AsyncOAuth2Mixin
from authlib.integrations.base_client.async_openid import AsyncOpenIDMixin
from authlib.integrations.flask_client import OAuth
from authlib.integrations.httpx_client import AsyncOAuth2Client
from authlib.oauth2.rfc6749 import OAuth2Token
from authlib.oauth2.rfc7523 import PrivateKeyJWT
from flask import Flask, Request


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


# Workaround: https://github.com/authlib/authlib/issues/818
class _AccessTokenParamsAsyncFlaskOAuth2App(AsyncOAuth2Mixin, AsyncOpenIDMixin, BaseApp):  # type: ignore
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
                client_cls=_AccessTokenParamsAsyncFlaskOAuth2App,
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
