from datetime import UTC, datetime

from schemes.domain.schemes.data_sources import DataSource
from schemes.domain.schemes.reviews import AuthorityReview
from schemes.infrastructure.api.data_sources import DataSourceModel
from schemes.infrastructure.api.schemes.authority_reviews import (
    CapitalSchemeAuthorityReviewModel,
    CreateCapitalSchemeAuthorityReviewModel,
)


class TestCapitalSchemeAuthorityReviewModel:
    def test_to_domain(self) -> None:
        authority_review_model = CapitalSchemeAuthorityReviewModel(
            review_date=datetime(2020, 1, 2), source=DataSourceModel.AUTHORITY_UPDATE
        )

        authority_review = authority_review_model.to_domain()

        assert (
            authority_review.id is not None
            and authority_review.review_date == datetime(2020, 1, 2)
            and authority_review.source == DataSource.AUTHORITY_UPDATE
        )

    def test_to_domain_converts_dates_to_local_europe_london(self) -> None:
        authority_review_model = CapitalSchemeAuthorityReviewModel(
            review_date=datetime(2020, 6, 1, 12, tzinfo=UTC), source=DataSourceModel.AUTHORITY_UPDATE
        )

        authority_review = authority_review_model.to_domain()

        assert authority_review.review_date == datetime(2020, 6, 1, 13)


class TestCreateCapitalSchemeAuthorityReviewModel:
    def test_from_domain(self) -> None:
        authority_review = AuthorityReview(id_=1, review_date=datetime(2020, 1, 2), source=DataSource.AUTHORITY_UPDATE)

        authority_review_model = CreateCapitalSchemeAuthorityReviewModel.from_domain(authority_review)

        assert authority_review_model == CreateCapitalSchemeAuthorityReviewModel(
            source=DataSourceModel.AUTHORITY_UPDATE
        )
