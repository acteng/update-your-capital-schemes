class Config:
    GOVUK_SERVER_METADATA_URL = "https://oidc.integration.account.gov.uk/.well-known/openid-configuration"
    GOVUK_TOKEN_ENDPOINT = "https://oidc.integration.account.gov.uk/token"
    GOVUK_PROFILE_URL = "https://home.integration.account.gov.uk/"


class DevConfig(Config):
    name = "dev"
    GOVUK_CLIENT_ID = "ACQWA69dKqUjccEMgMVKu0jX0q4"


class TestConfig(Config):
    GOVUK_CLIENT_ID = "0OJC1ThcrcGoFtEmxxiFXedQsqn"
