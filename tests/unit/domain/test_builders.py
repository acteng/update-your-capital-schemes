import pytest

from schemes.domain.schemes.overview import FundingProgrammes, SchemeOverview
from schemes.domain.schemes.schemes import Status
from tests.unit.domain.builders import build_scheme


def test_build_scheme() -> None:
    scheme = build_scheme(reference="ATE00001", name="")

    assert scheme.reference == "ATE00001" and scheme.status == Status.ACTIVE


def test_build_scheme_with_minimal_overview_fields() -> None:
    scheme = build_scheme(reference="", name="Wirral Package")

    assert (
        scheme.overview.name == "Wirral Package"
        and scheme.overview.authority_abbreviation == ""
        and scheme.overview.funding_programme == FundingProgrammes.ATF2
    )


def test_build_scheme_with_overview_fields() -> None:
    scheme = build_scheme(
        reference="",
        name="Wirral Package",
        authority_abbreviation="LIV",
        funding_programme=FundingProgrammes.ATF4,
    )

    assert (
        scheme.overview.name == "Wirral Package"
        and scheme.overview.authority_abbreviation == "LIV"
        and scheme.overview.funding_programme == FundingProgrammes.ATF4
    )


def test_build_scheme_with_overview() -> None:
    scheme = build_scheme(
        reference="",
        overview=SchemeOverview(
            name="Wirral Package", authority_abbreviation="LIV", funding_programme=FundingProgrammes.ATF4
        ),
    )

    assert (
        scheme.overview.name == "Wirral Package"
        and scheme.overview.authority_abbreviation == "LIV"
        and scheme.overview.funding_programme == FundingProgrammes.ATF4
    )


def test_cannot_build_scheme_without_overview() -> None:
    with pytest.raises(expected_exception=AssertionError, match="Either overview fields or overview must be specified"):
        build_scheme(reference="")


def test_cannot_build_scheme_with_overview_fields_and_overview() -> None:
    with pytest.raises(expected_exception=AssertionError, match="Either overview fields or overview must be specified"):
        build_scheme(
            reference="",
            name="Wirral Package",
            authority_abbreviation="LIV",
            funding_programme=FundingProgrammes.ATF4,
            overview=SchemeOverview(
                name="Wirral Package", authority_abbreviation="LIV", funding_programme=FundingProgrammes.ATF4
            ),
        )


def test_build_scheme_with_status() -> None:
    scheme = build_scheme(reference="", name="", status=Status.PAUSED)

    assert scheme.status == Status.PAUSED
