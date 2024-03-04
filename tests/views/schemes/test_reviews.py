from datetime import datetime

import pytest

from schemes.domain.schemes import AuthorityReview, DataSource
from schemes.views.schemes.data_source import DataSourceRepr
from schemes.views.schemes.reviews import (
    AuthorityReviewRepr,
    SchemeReviewContext,
    SchemeReviewForm,
)


@pytest.mark.usefixtures("app")
class TestSchemeReviewForm:
    def test_create(self) -> None:
        form = SchemeReviewForm()

        assert not form.up_to_date.data


@pytest.mark.usefixtures("app")
class TestSchemeReviewContext:
    def test_create(self) -> None:
        context = SchemeReviewContext()

        assert not context.form.up_to_date.data


class TestAuthorityReviewRepr:
    def test_from_domain(self) -> None:
        authority_review = AuthorityReview(id_=1, review_date=datetime(2020, 1, 1, 12), source=DataSource.ATF4_BID)

        authority_review_repr = AuthorityReviewRepr.from_domain(authority_review)

        assert authority_review_repr == AuthorityReviewRepr(
            id=1, review_date="2020-01-01T12:00:00", source=DataSourceRepr.ATF4_BID
        )

    def test_cannot_from_domain_when_transient(self) -> None:
        authority_review = AuthorityReview(id_=None, review_date=datetime(2020, 1, 1, 12), source=DataSource.ATF4_BID)

        with pytest.raises(ValueError, match="Authority review must be persistent"):
            AuthorityReviewRepr.from_domain(authority_review)

    def test_to_domain(self) -> None:
        authority_review_repr = AuthorityReviewRepr(
            id=1, review_date="2020-01-01T12:00:00", source=DataSourceRepr.ATF4_BID
        )

        authority_review = authority_review_repr.to_domain()

        assert (
            authority_review.id == 1
            and authority_review.review_date == datetime(2020, 1, 1, 12)
            and authority_review.source == DataSource.ATF4_BID
        )
