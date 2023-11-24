class Authority:
    def __init__(self, id_: int, name: str):
        self.id = id_
        self.name = name


class AuthorityRepository:
    def add(self, *authorities: Authority) -> None:
        raise NotImplementedError()

    def clear(self) -> None:
        raise NotImplementedError()

    def get(self, id_: int) -> Authority | None:
        raise NotImplementedError()

    def get_all(self) -> list[Authority]:
        raise NotImplementedError()
