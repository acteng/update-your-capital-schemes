from datetime import datetime

import pytest

from schemes.domain.dates import DateRange
from schemes.domain.reporting_window import ReportingWindow
from schemes.domain.schemes import AuthorityReview, DataSource, SchemeReviews


class TestSchemeReviews:
    def test_create(self) -> None:
        reviews = SchemeReviews()

        assert reviews.authority_reviews == []

    def test_get_authority_reviews_is_copy(self) -> None:
        reviews = SchemeReviews()
        reviews.update_authority_review(
            AuthorityReview(id_=1, review_date=datetime(2020, 1, 2), source=DataSource.ATF4_BID)
        )

        reviews.authority_reviews.clear()

        assert reviews.authority_reviews

    def test_update_authority_review(self) -> None:
        reviews = SchemeReviews()
        authority_review = AuthorityReview(id_=1, review_date=datetime(2020, 1, 2), source=DataSource.ATF4_BID)

        reviews.update_authority_review(authority_review)

        assert reviews.authority_reviews == [authority_review]

    def test_update_authority_reviews(self) -> None:
        reviews = SchemeReviews()
        authority_review1 = AuthorityReview(id_=1, review_date=datetime(2020, 1, 2), source=DataSource.ATF4_BID)
        authority_review2 = AuthorityReview(id_=2, review_date=datetime(2020, 1, 3), source=DataSource.ATF4_BID)

        reviews.update_authority_reviews(authority_review1, authority_review2)

        assert reviews.authority_reviews == [authority_review1, authority_review2]

    def test_last_reviewed(self) -> None:
        reviews = SchemeReviews()
        reviews.update_authority_reviews(
            AuthorityReview(id_=1, review_date=datetime(2020, 1, 2), source=DataSource.ATF4_BID),
            AuthorityReview(id_=2, review_date=datetime(2020, 1, 4), source=DataSource.ATF4_BID),
            AuthorityReview(id_=3, review_date=datetime(2020, 1, 3), source=DataSource.ATF4_BID),
        )

        assert reviews.last_reviewed == datetime(2020, 1, 4)

    def test_last_reviewed_when_no_authority_reviews(self) -> None:
        reviews = SchemeReviews()

        assert reviews.last_reviewed is None

    @pytest.mark.parametrize(
        "review_date, expected_needs_review",
        [
            pytest.param(datetime(2023, 3, 31), True, id="review before reporting window"),
            pytest.param(datetime(2023, 4, 1), False, id="review at start of reporting window"),
            pytest.param(datetime(2023, 4, 30), False, id="review at end of reporting window"),
            pytest.param(datetime(2023, 5, 1), False, id="review after reporting window"),
        ],
    )
    def test_needs_review(self, review_date: datetime, expected_needs_review: bool) -> None:
        reporting_window = ReportingWindow(DateRange(datetime(2023, 4, 1), datetime(2023, 5, 1)))
        reviews = SchemeReviews()
        reviews.update_authority_review(AuthorityReview(id_=1, review_date=review_date, source=DataSource.ATF4_BID))

        assert reviews.needs_review(reporting_window) == expected_needs_review

    def test_needs_review_when_no_authority_reviews(self) -> None:
        reporting_window = ReportingWindow(DateRange(datetime(2023, 4, 1), datetime(2023, 5, 1)))
        reviews = SchemeReviews()

        assert reviews.needs_review(reporting_window)


class TestAuthorityReview:
    def test_create(self) -> None:
        authority_review = AuthorityReview(id_=1, review_date=datetime(2020, 1, 2), source=DataSource.ATF4_BID)

        assert (
            authority_review.id == 1
            and authority_review.review_date == datetime(2020, 1, 2)
            and authority_review.source == DataSource.ATF4_BID
        )
