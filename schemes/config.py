import logging
from datetime import timedelta


class Config:
    # Logging
    LOGGER_LEVEL = logging.INFO

    # Flask
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    SEND_FILE_MAX_AGE_DEFAULT = timedelta(hours=1)

    # Flask-SQLAlchemy
    SQLALCHEMY_DATABASE_URI = "sqlite+pysqlite:///:memory:"

    # Flask-Session
    SESSION_TYPE = "sqlalchemy"
    SESSION_CLEANUP_N_REQUESTS = 100

    # GOV.UK One Login
    GOVUK_SERVER_METADATA_URL = "https://oidc.integration.account.gov.uk/.well-known/openid-configuration"
    GOVUK_TOKEN_ENDPOINT = "https://oidc.integration.account.gov.uk/token"
    GOVUK_PROFILE_URL = "https://home.integration.account.gov.uk/"
    GOVUK_END_SESSION_ENDPOINT = "https://oidc.integration.account.gov.uk/logout"
    GOVUK_CLIENT_ID = "ACQWA69dKqUjccEMgMVKu0jX0q4"

    # ATE API
    ATE_CLIENT_ID = "dDppdgxOYh5TZzAfiVQG3O5kEUOrKbUK"
    ATE_SERVER_METADATA_URL = "https://ate-api-dev.uk.auth0.com/.well-known/openid-configuration"
    ATE_AUDIENCE = "https://dev.api.activetravelengland.gov.uk"


class LocalConfig(Config):
    name = "local"

    # Logging
    LOGGER_LEVEL = logging.DEBUG


class GoogleConfig(Config):
    # Flask-SQLAlchemy
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": int(timedelta(minutes=30).total_seconds())}


class DevConfig(GoogleConfig):
    pass


class TestConfig(GoogleConfig):
    # GOV.UK One Login
    GOVUK_CLIENT_ID = "0OJC1ThcrcGoFtEmxxiFXedQsqn"

    # ATE API
    ATE_CLIENT_ID = "ztrG3zRot21yuGbF473wJIwlBulod2ZB"
    ATE_SERVER_METADATA_URL = "https://ate-api-test.uk.auth0.com/.well-known/openid-configuration"
    ATE_AUDIENCE = "https://test.api.activetravelengland.gov.uk"


class ProdConfig(GoogleConfig):
    # GOV.UK One Login
    GOVUK_SERVER_METADATA_URL = "https://oidc.account.gov.uk/.well-known/openid-configuration"
    GOVUK_TOKEN_ENDPOINT = "https://oidc.account.gov.uk/token"
    GOVUK_PROFILE_URL = "https://home.account.gov.uk/"
    GOVUK_END_SESSION_ENDPOINT = "https://oidc.account.gov.uk/logout"
    GOVUK_CLIENT_ID = "S1hl5G31dSsMYqPaOuiRVOLhBX0"

    # ATE API
    ATE_CLIENT_ID = "7NycUJoSOH8bgyN6M93xxqR5lNHihNcZ"
    ATE_SERVER_METADATA_URL = "https://ate-api-prod.uk.auth0.com/.well-known/openid-configuration"
    ATE_AUDIENCE = "https://api.activetravelengland.gov.uk"
