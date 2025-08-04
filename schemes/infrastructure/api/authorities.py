from requests import Response

from schemes.domain.authorities import Authority, AuthorityRepository
from schemes.infrastructure.api.base import BaseModel
from schemes.infrastructure.api.oauth import RemoteApp


class ApiAuthorityRepository(AuthorityRepository):
    def __init__(self, remote_app: RemoteApp):
        self._remote_app = remote_app

    def get(self, abbreviation: str) -> Authority | None:
        response: Response = self._remote_app.get(f"/authorities/{abbreviation}")

        if response.status_code == 404:
            return None

        response.raise_for_status()
        authority_model = AuthorityModel.model_validate(response.json())
        return authority_model.to_domain()


class AuthorityModel(BaseModel):
    abbreviation: str
    full_name: str

    def to_domain(self) -> Authority:
        return Authority(abbreviation=self.abbreviation, name=self.full_name)
