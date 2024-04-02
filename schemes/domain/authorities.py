class Authority:
    def __init__(self, id_: str, name: str):
        self.id = id_
        self.name = name


class AuthorityRepository:
    def add(self, *authorities: Authority) -> None:
        raise NotImplementedError()

    def clear(self) -> None:
        raise NotImplementedError()

    def get(self, id_: str) -> Authority | None:
        raise NotImplementedError()
