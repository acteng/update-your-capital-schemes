from schemes.domain.schemes.schemes import Scheme, SchemeRepository
from schemes.infrastructure.api.oauth import RemoteApp


class ApiSchemeRepository(SchemeRepository):
    def __init__(self, remote_app: RemoteApp):
        self._remote_app = remote_app

    def get_by_authority(self, authority_abbreviation: str) -> list[Scheme]:
        # TODO: implement
        return []
