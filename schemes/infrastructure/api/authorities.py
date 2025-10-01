from typing import Annotated, Any

from pydantic import AnyUrl, Field

from schemes.domain.authorities import Authority, AuthorityRepository
from schemes.infrastructure.api.base import BaseModel
from schemes.oauth import AsyncBaseApp


class AuthorityModel(BaseModel):
    id: Annotated[AnyUrl, Field(alias="@id")]
    abbreviation: str
    full_name: str

    def to_domain(self) -> Authority:
        return Authority(abbreviation=self.abbreviation, name=self.full_name)


class ApiAuthorityRepository(AuthorityRepository):
    def __init__(self, remote_app: AsyncBaseApp):
        self._remote_app = remote_app

    async def get(self, abbreviation: str) -> Authority | None:
        response = await self._remote_app.get(f"/authorities/{abbreviation}", request=self._dummy_request())

        if response.status_code == 404:
            return None

        response.raise_for_status()
        authority_model = AuthorityModel.model_validate(response.json())
        return authority_model.to_domain()

    # See: https://github.com/authlib/authlib/issues/818#issuecomment-3257950062
    @staticmethod
    def _dummy_request() -> Any:
        return object()
