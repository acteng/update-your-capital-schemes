from authlib.integrations.flask_client import OAuth
from authlib.oauth2.rfc7523 import PrivateKeyJWT
from flask import Flask


class OAuthExtension(OAuth):  # type: ignore
    def __init__(self, app: Flask):
        super().__init__(app)

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
            self.register(
                name="ate",
                fetch_token=lambda: self.ate.fetch_access_token(grant_type="client_credentials"),
                client_id=app.config["ATE_CLIENT_ID"],
                client_secret=app.config["ATE_CLIENT_SECRET"],
                server_metadata_url=app.config["ATE_SERVER_METADATA_URL"],
                access_token_params={"audience": app.config["ATE_AUDIENCE"]},
                api_base_url=app.config["ATE_URL"],
                client_kwargs={"token_endpoint_auth_method": "client_secret_post"},
            )
