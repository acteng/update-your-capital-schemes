from authlib.integrations.flask_client import OAuth
from flask import current_app

from schemes.domain.authorities import Authority, AuthorityRepository


class ApiAuthorityRepository(AuthorityRepository):
    def __init__(self, url: str):
        self._url = url

    def get(self, abbreviation: str) -> Authority | None:
        oauth = self._get_oauth()
        token = oauth.ate.fetch_access_token(grant_type="client_credentials")
        response = oauth.ate.get(f"{self._url}/authorities/{abbreviation}", token=token)
        response.raise_for_status()
        body = response.json()
        return Authority(abbreviation=body["abbreviation"], name=body["fullName"])

    @staticmethod
    def _get_oauth() -> OAuth:
        return current_app.extensions["authlib.integrations.flask_client"]
