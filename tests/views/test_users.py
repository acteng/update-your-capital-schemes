from schemes.views.users import UserRepr


class TestUserRepr:
    def test_to_domain(self) -> None:
        user_repr = UserRepr(email="boardman@example.com", authority_abbreviation="LIV")

        user = user_repr.to_domain()

        assert user.email == "boardman@example.com" and user.authority_abbreviation == "LIV"
