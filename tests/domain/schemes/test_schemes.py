from datetime import datetime

import pytest

from schemes.domain.dates import DateRange
from schemes.domain.reporting_window import ReportingWindow
from schemes.domain.schemes import (
    AuthorityReview,
    DataSource,
    Scheme,
    SchemeFunding,
    SchemeMilestones,
    SchemeOutputs,
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
            and scheme.authority_reviews == []
        )

    def test_get_authority_reviews_is_copy(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.update_authority_review(
            AuthorityReview(id_=1, review_date=datetime(2020, 1, 2), source=DataSource.ATF4_BID)
        )

        scheme.authority_reviews.clear()

        assert scheme.authority_reviews

    def test_update_authority_review(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        authority_review = AuthorityReview(id_=1, review_date=datetime(2020, 1, 2), source=DataSource.ATF4_BID)

        scheme.update_authority_review(authority_review)

        assert scheme.authority_reviews == [authority_review]

    def test_update_authority_reviews(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        authority_review1 = AuthorityReview(id_=1, review_date=datetime(2020, 1, 2), source=DataSource.ATF4_BID)
        authority_review2 = AuthorityReview(id_=2, review_date=datetime(2020, 1, 3), source=DataSource.ATF4_BID)

        scheme.update_authority_reviews(authority_review1, authority_review2)

        assert scheme.authority_reviews == [authority_review1, authority_review2]

    def test_last_reviewed(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.update_authority_reviews(
            AuthorityReview(id_=1, review_date=datetime(2020, 1, 2), source=DataSource.ATF4_BID),
            AuthorityReview(id_=2, review_date=datetime(2020, 1, 4), source=DataSource.ATF4_BID),
            AuthorityReview(id_=3, review_date=datetime(2020, 1, 3), source=DataSource.ATF4_BID),
        )

        assert scheme.last_reviewed == datetime(2020, 1, 4)

    def test_last_reviewed_when_no_authority_reviews(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)

        assert scheme.last_reviewed is None

    @pytest.mark.parametrize(
        "review_date, expected_needs_review",
        [
            (datetime(2023, 3, 31), True),
            (datetime(2023, 4, 1), False),
            (datetime(2023, 4, 30), False),
            (datetime(2023, 5, 1), False),
        ],
    )
    def test_needs_review(self, review_date: datetime, expected_needs_review: bool) -> None:
        reporting_window = ReportingWindow(DateRange(datetime(2023, 4, 1), datetime(2023, 4, 30)))
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.update_authority_review(AuthorityReview(id_=1, review_date=review_date, source=DataSource.ATF4_BID))

        assert scheme.needs_review(reporting_window) == expected_needs_review

    def test_needs_review_when_no_authority_reviews(self) -> None:
        reporting_window = ReportingWindow(DateRange(datetime(2023, 4, 1), datetime(2023, 4, 30)))
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)

        assert scheme.needs_review(reporting_window)

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


class TestAuthorityReview:
    def test_create(self) -> None:
        authority_review = AuthorityReview(id_=1, review_date=datetime(2020, 1, 2), source=DataSource.ATF4_BID)

        assert (
            authority_review.id == 1
            and authority_review.review_date == datetime(2020, 1, 2)
            and authority_review.source == DataSource.ATF4_BID
        )
