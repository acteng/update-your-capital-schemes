from datetime import datetime

import pytest

from schemes.domain.dates import DateRange
from schemes.domain.schemes import (
    BidStatus,
    BidStatusRevision,
    FundingProgrammes,
    OverviewRevision,
    SchemeType,
)
from tests.builders import build_scheme


def test_build_scheme_with_overview_fields() -> None:
    scheme = build_scheme(
        id_=1,
        reference="ATE00001",
        name="Wirral Package",
        authority_id=2,
        type_=SchemeType.DEVELOPMENT,
        funding_programme=FundingProgrammes.ATF4,
    )

    assert (
        scheme.id == 1
        and scheme.reference == "ATE00001"
        and scheme.overview.name == "Wirral Package"
        and scheme.overview.authority_id == 2
        and scheme.overview.type == SchemeType.DEVELOPMENT
        and scheme.overview.funding_programme == FundingProgrammes.ATF4
    )


def test_build_scheme_with_overview_revision() -> None:
    scheme = build_scheme(
        id_=1,
        reference="ATE00001",
        overview_revisions=[
            OverviewRevision(
                id_=2,
                effective=DateRange(datetime(2020, 1, 1), None),
                name="Wirral Package",
                authority_id=2,
                type_=SchemeType.DEVELOPMENT,
                funding_programme=FundingProgrammes.ATF4,
            )
        ],
    )

    assert (
        scheme.id == 1
        and scheme.reference == "ATE00001"
        and scheme.overview.name == "Wirral Package"
        and scheme.overview.authority_id == 2
        and scheme.overview.type == SchemeType.DEVELOPMENT
        and scheme.overview.funding_programme == FundingProgrammes.ATF4
    )


def test_build_scheme_with_no_overview_revisions() -> None:
    scheme = build_scheme(id_=1, reference="ATE00001", overview_revisions=[])

    assert scheme.id == 1 and scheme.reference == "ATE00001" and scheme.overview.overview_revisions == []


def test_cannot_build_scheme_without_overview() -> None:
    with pytest.raises(
        expected_exception=AssertionError, match="Either overview fields or revisions must be specified"
    ):
        build_scheme(id_=1, reference="ATE00001")


def test_cannot_build_scheme_with_overview_fields_and_revision() -> None:
    with pytest.raises(
        expected_exception=AssertionError, match="Either overview fields or revisions must be specified"
    ):
        build_scheme(
            id_=1,
            reference="ATE00001",
            name="Wirral Package",
            authority_id=2,
            type_=SchemeType.DEVELOPMENT,
            funding_programme=FundingProgrammes.ATF4,
            overview_revisions=[
                OverviewRevision(
                    id_=2,
                    effective=DateRange(datetime(2020, 1, 1), None),
                    name="Wirral Package",
                    authority_id=2,
                    type_=SchemeType.DEVELOPMENT,
                    funding_programme=FundingProgrammes.ATF4,
                )
            ],
        )


def test_build_scheme_with_bid_status_fields() -> None:
    scheme = build_scheme(
        id_=1, reference="ATE00001", name="Wirral Package", authority_id=2, bid_status=BidStatus.SUBMITTED
    )

    assert (
        scheme.id == 1
        and scheme.reference == "ATE00001"
        and scheme.overview.name == "Wirral Package"
        and scheme.overview.authority_id == 2
        and scheme.funding.bid_status == BidStatus.SUBMITTED
    )


def test_build_scheme_with_bid_status_revision() -> None:
    scheme = build_scheme(
        id_=1,
        reference="ATE00001",
        name="Wirral Package",
        authority_id=2,
        bid_status_revisions=[
            BidStatusRevision(id_=2, effective=DateRange(datetime(2020, 1, 1), None), status=BidStatus.SUBMITTED)
        ],
    )

    assert (
        scheme.id == 1
        and scheme.reference == "ATE00001"
        and scheme.overview.name == "Wirral Package"
        and scheme.overview.authority_id == 2
        and scheme.funding.bid_status == BidStatus.SUBMITTED
    )


def test_build_scheme_with_no_bid_status_revisions() -> None:
    scheme = build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_id=2, bid_status_revisions=[])

    assert (
        scheme.id == 1
        and scheme.reference == "ATE00001"
        and scheme.overview.name == "Wirral Package"
        and scheme.overview.authority_id == 2
        and scheme.funding.bid_status_revisions == []
    )


def test_cannot_build_scheme_with_bid_status_fields_and_revision() -> None:
    with pytest.raises(expected_exception=AssertionError, match="Either bid status or revisions must be specified"):
        build_scheme(
            id_=1,
            reference="ATE00001",
            name="Wirral Package",
            authority_id=2,
            bid_status=BidStatus.SUBMITTED,
            bid_status_revisions=[
                BidStatusRevision(id_=2, effective=DateRange(datetime(2020, 1, 1), None), status=BidStatus.SUBMITTED)
            ],
        )
