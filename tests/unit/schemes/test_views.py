from schemes.schemes.domain import Scheme
from schemes.schemes.views import SchemeContext, SchemeRepr


class TestSchemeContext:
    def test_create_from_domain(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)

        context = SchemeContext.for_domain(scheme)

        assert context == SchemeContext(reference="ATE00001", name="Wirral Package")


class TestSchemeRepr:
    def test_create_from_domain(self) -> None:
        scheme_repr = SchemeRepr(id=1, name="Wirral Package")

        scheme = scheme_repr.to_domain(2)

        assert scheme.id == 1 and scheme.name == "Wirral Package" and scheme.authority_id == 2
