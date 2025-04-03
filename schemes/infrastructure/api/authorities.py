from requests import Response

from schemes.domain.authorities import Authority, AuthorityRepository
from schemes.infrastructure.api.oauth import RemoteApp


class ApiAuthorityRepository(AuthorityRepository):
    def __init__(self, remote_app: RemoteApp):
        self._remote_app = remote_app

    def get(self, abbreviation: str) -> Authority | None:
        token = self._remote_app.fetch_access_token(grant_type="client_credentials")
        response: Response = self._remote_app.get(f"/authorities/{abbreviation}", token=token)

        if response.status_code == 404:
            return None

        response.raise_for_status()
        body = response.json()
        return Authority(abbreviation=body["abbreviation"], name=body["fullName"])
