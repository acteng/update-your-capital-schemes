from schemes.domain.users import User


class TestUser:
    def test_create(self) -> None:
        user = User(email="boardman@example.com", authority_abbreviation="LIV")

        assert user.email == "boardman@example.com" and user.authority_abbreviation == "LIV"
