from schemes.domain.authorities import Authority


class TestAuthority:
    def test_create(self) -> None:
        authority = Authority(abbreviation="LIV", name="Liverpool City Region Combined Authority")

        assert authority.abbreviation == "LIV" and authority.name == "Liverpool City Region Combined Authority"
