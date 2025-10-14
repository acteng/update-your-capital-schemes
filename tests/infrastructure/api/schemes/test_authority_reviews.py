from datetime import UTC, datetime

from schemes.infrastructure.api.schemes.authority_reviews import CapitalSchemeAuthorityReviewModel


class TestCapitalSchemeAuthorityReviewModel:
    def test_to_domain(self) -> None:
        authority_review_model = CapitalSchemeAuthorityReviewModel(review_date=datetime(2020, 1, 2))

        authority_review = authority_review_model.to_domain()

        assert authority_review.review_date == datetime(2020, 1, 2)

    def test_to_domain_converts_dates_to_local_europe_london(self) -> None:
        authority_review_model = CapitalSchemeAuthorityReviewModel(review_date=datetime(2020, 6, 1, 12, tzinfo=UTC))

        authority_review = authority_review_model.to_domain()

        assert authority_review.review_date == datetime(2020, 6, 1, 13)
