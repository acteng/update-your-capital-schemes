from dataclasses import dataclass

from dataclass_wizard import fromdict
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
        authority_repr = fromdict(AuthorityRepr, response.json())
        return authority_repr.to_domain()


@dataclass(frozen=True)
class AuthorityRepr:
    abbreviation: str
    full_name: str

    def to_domain(self) -> Authority:
        return Authority(abbreviation=self.abbreviation, name=self.full_name)
