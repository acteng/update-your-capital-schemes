from dataclasses import dataclass


@dataclass
class Scheme:
    id: int
    name: str
    authority_id: int

    @property
    def reference(self) -> str:
        return f"ATE{self.id:05}"
