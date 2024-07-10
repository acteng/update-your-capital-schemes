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
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_recycle": int(timedelta(minutes=30).total_seconds())}

    # Flask-Session
    SESSION_TYPE = "sqlalchemy"
    SESSION_CLEANUP_N_REQUESTS = 100

    # GOV.UK One Login
    GOVUK_SERVER_METADATA_URL = "https://oidc.integration.account.gov.uk/.well-known/openid-configuration"
    GOVUK_TOKEN_ENDPOINT = "https://oidc.integration.account.gov.uk/token"
    GOVUK_PROFILE_URL = "https://home.integration.account.gov.uk/"
    GOVUK_END_SESSION_ENDPOINT = "https://oidc.integration.account.gov.uk/logout"
    GOVUK_CLIENT_ID = "ACQWA69dKqUjccEMgMVKu0jX0q4"


class LocalConfig(Config):
    name = "local"

    # Logging
    LOGGER_LEVEL = logging.DEBUG


class DevConfig(Config):
    pass


class TestConfig(Config):
    # GOV.UK One Login
    GOVUK_CLIENT_ID = "0OJC1ThcrcGoFtEmxxiFXedQsqn"


class ProdConfig(Config):
    # GOV.UK One Login
    GOVUK_SERVER_METADATA_URL = "https://oidc.account.gov.uk/.well-known/openid-configuration"
    GOVUK_TOKEN_ENDPOINT = "https://oidc.account.gov.uk/token"
    GOVUK_PROFILE_URL = "https://home.account.gov.uk/"
    GOVUK_END_SESSION_ENDPOINT = "https://oidc.account.gov.uk/logout"
    GOVUK_CLIENT_ID = "S1hl5G31dSsMYqPaOuiRVOLhBX0"
