from authlib.integrations.flask_client import OAuth
from authlib.integrations.requests_client import OAuth2Session
from authlib.oauth2.rfc6749 import OAuth2Token
from authlib.oauth2.rfc7523 import PrivateKeyJWT
from flask import Flask


class _AccessTokenParamsOAuth2Session(OAuth2Session):  # type: ignore
    """
    An OAuth2 session that supports extra parameters to fetch access token.

    See: https://github.com/authlib/authlib/issues/783
    """

    def ensure_active_token(self, token: OAuth2Token = None) -> bool:
        access_token_params = self.metadata.get("access_token_params") or {}

        # Copy of OAuth2Client.ensure_active_token:
        if token is None:
            token = self.token
        if not token.is_expired(leeway=self.leeway):
            return True
        refresh_token = token.get("refresh_token")
        url = self.metadata.get("token_endpoint")
        if refresh_token and url:
            self.refresh_token(url, refresh_token=refresh_token)
            return True
        elif self.metadata.get("grant_type") == "client_credentials":
            access_token = token["access_token"]
            # Include extra parameters to fetch access token
            new_token = self.fetch_token(url, grant_type="client_credentials", **access_token_params)
            if self.update_token:
                self.update_token(new_token, access_token=access_token)
            return True

        return False


class OAuthExtension(OAuth):  # type: ignore
    def __init__(self, app: Flask):
        super().__init__(app)

        # Workaround: https://github.com/authlib/authlib/issues/783
        self.oauth2_client_cls.client_cls = _AccessTokenParamsOAuth2Session

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
                fetch_token=lambda: self.ate.fetch_access_token(),
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
