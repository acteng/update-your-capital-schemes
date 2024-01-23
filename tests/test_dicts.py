from schemes.dicts import inverse_dict


def test_inverse_dict() -> None:
    d = {"a": 1, "b": 2, "c": 3}

    assert inverse_dict(d) == {1: "a", 2: "b", 3: "c"}
