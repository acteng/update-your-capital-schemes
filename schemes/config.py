class Config:
    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = "sqlite+pysqlite:///file::memory:?uri=true"

    # GOV.UK One Login
    GOVUK_SERVER_METADATA_URL = "https://oidc.integration.account.gov.uk/.well-known/openid-configuration"
    GOVUK_TOKEN_ENDPOINT = "https://oidc.integration.account.gov.uk/token"
    GOVUK_PROFILE_URL = "https://home.integration.account.gov.uk/"
    GOVUK_END_SESSION_ENDPOINT = "https://oidc.integration.account.gov.uk/logout"


class DevConfig(Config):
    name = "dev"

    # GOV.UK One Login
    GOVUK_CLIENT_ID = "ACQWA69dKqUjccEMgMVKu0jX0q4"


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
