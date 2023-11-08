class Scheme:
    def __init__(self, id_: int, name: str, authority_id: int):
        self.id = id_
        self.name = name
        self.authority_id = authority_id

    @property
    def reference(self) -> str:
        return f"ATE{self.id:05}"
