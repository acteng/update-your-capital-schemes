from __future__ import annotations

from dataclasses import dataclass

from schemes.dicts import as_shallow_dict, inverse_dict


def test_inverse_dict() -> None:
    d = {"a": 1, "b": 2, "c": 3}

    assert inverse_dict(d) == {1: "a", 2: "b", 3: "c"}


@dataclass
class Person:
    name: str
    address: Address


@dataclass
class Address:
    city: str


def test_as_shallow_dict() -> None:
    address = Address(city="Liverpool")
    person = Person(name="Boardman", address=address)

    assert as_shallow_dict(person) == {"name": "Boardman", "address": address}
