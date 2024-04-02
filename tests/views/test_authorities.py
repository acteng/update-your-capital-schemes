from schemes.views.authorities import AuthorityRepr


class TestAuthorityRepr:
    def test_to_domain(self) -> None:
        authority_repr = AuthorityRepr(id="LIV", name="Liverpool City Region Combined Authority")

        authority = authority_repr.to_domain()

        assert authority.id == "LIV" and authority.name == "Liverpool City Region Combined Authority"
