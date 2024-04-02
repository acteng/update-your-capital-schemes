from schemes.domain.authorities import Authority


class TestAuthority:
    def test_create(self) -> None:
        authority = Authority(id_="LIV", name="Liverpool City Region Combined Authority")

        assert authority.id == "LIV" and authority.name == "Liverpool City Region Combined Authority"
