import pytest

from schemes.schemes.domain import Scheme, SchemeType
from schemes.schemes.views import SchemeContext, SchemeRepr


class TestSchemeContext:
    def test_create_from_domain(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)

        context = SchemeContext.for_domain(scheme)

        assert context == SchemeContext(reference="ATE00001", name="Wirral Package")

    @pytest.mark.parametrize(
        "type_, expected_type",
        [(SchemeType.DEVELOPMENT, "Development"), (SchemeType.CONSTRUCTION, "Construction"), (None, None)],
    )
    def test_set_type(self, type_: SchemeType | None, expected_type: str | None) -> None:
        scheme = Scheme(id_=0, name="", authority_id=0, type_=type_)

        context = SchemeContext.for_domain(scheme)

        assert context.type == expected_type


class TestSchemeRepr:
    def test_create_from_domain(self) -> None:
        scheme_repr = SchemeRepr(id=1, name="Wirral Package")

        scheme = scheme_repr.to_domain(2)

        assert scheme.id == 1 and scheme.name == "Wirral Package" and scheme.authority_id == 2

    @pytest.mark.parametrize(
        "type_, expected_type",
        [("development", SchemeType.DEVELOPMENT), ("construction", SchemeType.CONSTRUCTION), (None, None)],
    )
    def test_set_type(self, type_: str | None, expected_type: SchemeType | None) -> None:
        scheme_repr = SchemeRepr(id=0, name="", type=type_)

        scheme = scheme_repr.to_domain(0)

        assert scheme.type == expected_type
