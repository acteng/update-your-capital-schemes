from schemes.views.authorities import AuthorityRepr


class TestAuthorityRepr:
    def test_to_domain(self) -> None:
        authority_repr = AuthorityRepr(abbreviation="LIV", name="Liverpool City Region Combined Authority")

        authority = authority_repr.to_domain()

        assert authority.abbreviation == "LIV" and authority.name == "Liverpool City Region Combined Authority"
