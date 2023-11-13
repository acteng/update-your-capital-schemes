from schemes.authorities.views import AuthorityRepr


def test_create_domain() -> None:
    authority_repr = AuthorityRepr(id=1, name="Liverpool City Region Combined Authority")

    authority = authority_repr.to_domain()

    assert authority.id == 1 and authority.name == "Liverpool City Region Combined Authority"
