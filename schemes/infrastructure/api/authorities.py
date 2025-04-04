from authlib.integrations.base_client import BaseApp, OAuth2Mixin

from schemes.domain.authorities import Authority, AuthorityRepository

type RemoteApp = BaseApp | OAuth2Mixin


class ApiAuthorityRepository(AuthorityRepository):
    def __init__(self, remote_app: RemoteApp):
        self._remote_app = remote_app

    def get(self, abbreviation: str) -> Authority | None:
        token = self._remote_app.fetch_access_token(grant_type="client_credentials")
        response = self._remote_app.get(f"/authorities/{abbreviation}", token=token)
        response.raise_for_status()
        body = response.json()
        return Authority(abbreviation=body["abbreviation"], name=body["fullName"])
