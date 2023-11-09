from schemes.users.views import UserRepr


def test_create_repr_from_domain() -> None:
    user_repr = UserRepr(email="boardman@example.com")

    user = user_repr.to_domain(1)

    assert user.email == "boardman@example.com" and user.authority_id == 1
