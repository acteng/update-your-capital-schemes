import pytest

from schemes.domain.schemes.overview import SchemeOverview
from schemes.domain.schemes.schemes import Status
from tests.unit.domain.builders import build_scheme


def test_build_scheme() -> None:
    scheme = build_scheme(reference="ATE00001", name="")

    assert scheme.reference == "ATE00001" and scheme.status == Status.ACTIVE


def test_build_scheme_with_minimal_overview_fields() -> None:
    scheme = build_scheme(reference="", name="Wirral Package")

    assert scheme.overview.name == "Wirral Package" and scheme.overview.authority_abbreviation == ""


def test_build_scheme_with_overview_fields() -> None:
    scheme = build_scheme(reference="", name="Wirral Package", authority_abbreviation="LIV")

    assert scheme.overview.name == "Wirral Package" and scheme.overview.authority_abbreviation == "LIV"


def test_build_scheme_with_overview() -> None:
    scheme = build_scheme(reference="", overview=SchemeOverview(name="Wirral Package", authority_abbreviation="LIV"))

    assert scheme.overview.name == "Wirral Package" and scheme.overview.authority_abbreviation == "LIV"


def test_cannot_build_scheme_without_overview() -> None:
    with pytest.raises(expected_exception=AssertionError, match="Either overview fields or overview must be specified"):
        build_scheme(reference="")


def test_cannot_build_scheme_with_overview_fields_and_overview() -> None:
    with pytest.raises(expected_exception=AssertionError, match="Either overview fields or overview must be specified"):
        build_scheme(
            reference="",
            name="Wirral Package",
            authority_abbreviation="LIV",
            overview=SchemeOverview(name="Wirral Package", authority_abbreviation="LIV"),
        )


def test_build_scheme_with_status() -> None:
    scheme = build_scheme(reference="", name="", status=Status.PAUSED)

    assert scheme.status == Status.PAUSED
