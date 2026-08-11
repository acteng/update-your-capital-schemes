from datetime import datetime

import pytest

from schemes.domain.dates import DateRange
from schemes.domain.schemes.funding import BidStatus, BidStatusRevision
from schemes.domain.schemes.overview import FundingProgrammes, OverviewRevision, SchemeType
from tests.builders import build_scheme


def test_build_scheme() -> None:
    scheme = build_scheme(reference="ATE00001", name="")

    assert scheme.reference == "ATE00001"


def test_build_scheme_with_minimal_overview_fields() -> None:
    scheme = build_scheme(reference="", name="Wirral Package")

    assert (
        scheme.overview.name == "Wirral Package"
        and scheme.overview.authority_abbreviation == ""
        and scheme.overview.type == SchemeType.CONSTRUCTION
        and scheme.overview.funding_programme == FundingProgrammes.ATF2
    )


def test_build_scheme_with_overview_fields() -> None:
    scheme = build_scheme(
        reference="",
        name="Wirral Package",
        authority_abbreviation="LIV",
        type_=SchemeType.DEVELOPMENT,
        funding_programme=FundingProgrammes.ATF4,
    )

    assert (
        scheme.overview.name == "Wirral Package"
        and scheme.overview.authority_abbreviation == "LIV"
        and scheme.overview.type == SchemeType.DEVELOPMENT
        and scheme.overview.funding_programme == FundingProgrammes.ATF4
    )


def test_build_scheme_with_overview_revision() -> None:
    scheme = build_scheme(
        reference="",
        overview_revisions=[
            OverviewRevision(
                effective=DateRange(datetime(2020, 1, 1), None),
                name="Wirral Package",
                authority_abbreviation="LIV",
                type_=SchemeType.DEVELOPMENT,
                funding_programme=FundingProgrammes.ATF4,
            )
        ],
    )

    assert (
        scheme.overview.name == "Wirral Package"
        and scheme.overview.authority_abbreviation == "LIV"
        and scheme.overview.type == SchemeType.DEVELOPMENT
        and scheme.overview.funding_programme == FundingProgrammes.ATF4
    )


def test_build_scheme_with_no_overview_revisions() -> None:
    scheme = build_scheme(reference="", overview_revisions=[])

    assert scheme.overview.overview_revisions == []


def test_cannot_build_scheme_without_overview() -> None:
    with pytest.raises(
        expected_exception=AssertionError, match="Either overview fields or revisions must be specified"
    ):
        build_scheme(reference="")


def test_cannot_build_scheme_with_overview_fields_and_revision() -> None:
    with pytest.raises(
        expected_exception=AssertionError, match="Either overview fields or revisions must be specified"
    ):
        build_scheme(
            reference="",
            name="Wirral Package",
            authority_abbreviation="LIV",
            type_=SchemeType.DEVELOPMENT,
            funding_programme=FundingProgrammes.ATF4,
            overview_revisions=[
                OverviewRevision(
                    effective=DateRange(datetime(2020, 1, 1), None),
                    name="Wirral Package",
                    authority_abbreviation="LIV",
                    type_=SchemeType.DEVELOPMENT,
                    funding_programme=FundingProgrammes.ATF4,
                )
            ],
        )


def test_build_scheme_with_minimal_bid_status_fields() -> None:
    scheme = build_scheme(reference="", name="Wirral Package")

    assert scheme.overview.name == "Wirral Package" and scheme.funding.bid_status == BidStatus.FUNDED


def test_build_scheme_with_bid_status_fields() -> None:
    scheme = build_scheme(reference="", name="Wirral Package", bid_status=BidStatus.SUBMITTED)

    assert scheme.overview.name == "Wirral Package" and scheme.funding.bid_status == BidStatus.SUBMITTED


def test_build_scheme_with_bid_status_revision() -> None:
    scheme = build_scheme(
        reference="",
        name="Wirral Package",
        bid_status_revisions=[
            BidStatusRevision(id_=2, effective=DateRange(datetime(2020, 1, 1), None), status=BidStatus.SUBMITTED)
        ],
    )

    assert scheme.overview.name == "Wirral Package" and scheme.funding.bid_status == BidStatus.SUBMITTED


def test_build_scheme_with_no_bid_status_revisions() -> None:
    scheme = build_scheme(reference="", name="Wirral Package", bid_status_revisions=[])

    assert scheme.overview.name == "Wirral Package" and scheme.funding.bid_status_revisions == []


def test_cannot_build_scheme_with_bid_status_fields_and_revision() -> None:
    with pytest.raises(expected_exception=AssertionError, match="Either bid status or revisions must be specified"):
        build_scheme(
            reference="",
            name="Wirral Package",
            bid_status=BidStatus.SUBMITTED,
            bid_status_revisions=[
                BidStatusRevision(id_=2, effective=DateRange(datetime(2020, 1, 1), None), status=BidStatus.SUBMITTED)
            ],
        )
