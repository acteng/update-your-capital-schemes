from schemes.views.users import UserRepr


class TestUserRepr:
    def test_to_domain(self) -> None:
        user_repr = UserRepr(email="boardman@example.com")

        user = user_repr.to_domain("LIV")

        assert user.email == "boardman@example.com" and user.authority_abbreviation == "LIV"
