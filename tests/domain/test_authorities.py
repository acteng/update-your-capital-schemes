from schemes.domain.authorities import Authority


class TestAuthority:
    def test_create(self) -> None:
        authority = Authority(id_=1, name="Liverpool City Region Combined Authority")

        assert authority.id == 1 and authority.name == "Liverpool City Region Combined Authority"
