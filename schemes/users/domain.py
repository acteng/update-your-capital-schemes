from dataclasses import dataclass


@dataclass
class User:
    email: str
    authority_id: int
