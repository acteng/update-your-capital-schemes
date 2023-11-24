from schemes.views.users import UserRepr


class TestUserRepr:
    def test_create_domain(self) -> None:
        user_repr = UserRepr(email="boardman@example.com")

        user = user_repr.to_domain(1)

        assert user.email == "boardman@example.com" and user.authority_id == 1
