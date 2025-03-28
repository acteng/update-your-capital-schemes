class Authority:
    def __init__(self, abbreviation: str, name: str):
        self._abbreviation = abbreviation
        self._name = name

    @property
    def abbreviation(self) -> str:
        return self._abbreviation

    @property
    def name(self) -> str:
        return self._name


class AuthorityRepository:
    def add(self, *authorities: Authority) -> None:
        raise NotImplementedError()

    def clear(self) -> None:
        raise NotImplementedError()

    def get(self, abbreviation: str) -> Authority | None:
        raise NotImplementedError()
