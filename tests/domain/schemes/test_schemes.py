from datetime import datetime

import pytest

from schemes.domain.dates import DateRange
from schemes.domain.schemes import (
    BidStatus,
    BidStatusRevision,
    Scheme,
    SchemeFunding,
    SchemeMilestones,
    SchemeOutputs,
    SchemeReviews,
)


class TestScheme:
    def test_create(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)

        assert (
            scheme.id == 1
            and scheme.name == "Wirral Package"
            and scheme.authority_id == 2
            and scheme.type is None
            and scheme.funding_programme is None
        )

    def test_get_reference(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)

        assert scheme.reference == "ATE00001"

    def test_get_funding(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)

        assert isinstance(scheme.funding, SchemeFunding)

    def test_get_milestones(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)

        assert isinstance(scheme.milestones, SchemeMilestones)

    def test_get_outputs(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)

        assert isinstance(scheme.outputs, SchemeOutputs)

    def test_get_reviews(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)

        assert isinstance(scheme.reviews, SchemeReviews)

    @pytest.mark.parametrize(
        "bid_status, expected_updateable",
        [
            (BidStatus.SUBMITTED, False),
            (BidStatus.FUNDED, True),
            (BidStatus.NOT_FUNDED, False),
            (BidStatus.SPLIT, False),
            (BidStatus.DELETED, False),
        ],
    )
    def test_is_updateable(self, bid_status: BidStatus, expected_updateable: bool) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.funding.update_bid_status(
            BidStatusRevision(id_=3, effective=DateRange(datetime(2000, 1, 2), None), status=bid_status)
        )

        assert scheme.is_updateable == expected_updateable
