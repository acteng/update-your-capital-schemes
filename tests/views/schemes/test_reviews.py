from datetime import datetime

import pytest
from flask_wtf.csrf import generate_csrf
from werkzeug.datastructures import MultiDict

from schemes.domain.schemes.data_sources import DataSource
from schemes.domain.schemes.reviews import AuthorityReview, SchemeReviews
from schemes.views.schemes.data_sources import DataSourceRepr
from schemes.views.schemes.reviews import AuthorityReviewRepr, SchemeReviewContext, SchemeReviewForm


@pytest.mark.usefixtures("app")
class TestSchemeReviewForm:
    def test_create(self) -> None:
        form = SchemeReviewForm()

        assert not form.up_to_date.data

    def test_update_domain(self) -> None:
        form = SchemeReviewForm()
        reviews = SchemeReviews()
        reviews.update_authority_review(
            AuthorityReview(id_=1, review_date=datetime(2023, 1, 1, 12), source=DataSource.ATF4_BID)
        )

        form.update_domain(reviews, now=datetime(2023, 4, 24, 12))

        review1: AuthorityReview
        review2: AuthorityReview
        review1, review2 = reviews.authority_reviews
        assert review2.review_date == datetime(2023, 4, 24, 12) and review2.source == DataSource.AUTHORITY_UPDATE

    def test_no_errors_when_valid(self) -> None:
        form = SchemeReviewForm(formdata=MultiDict([("csrf_token", generate_csrf()), ("up_to_date", "confirmed")]))

        form.validate()

        assert not form.errors

    def test_up_to_date_is_required(self) -> None:
        form = SchemeReviewForm(formdata=MultiDict([]))

        form.validate()

        assert "Confirm this scheme is up-to-date" in form.errors["up_to_date"]


@pytest.mark.usefixtures("app")
class TestSchemeReviewContext:
    def test_from_domain(self) -> None:
        reviews = SchemeReviews()

        context = SchemeReviewContext.from_domain(reviews)

        assert context.last_reviewed is None and not context.form.up_to_date.data

    def test_from_domain_sets_last_reviewed(self) -> None:
        reviews = SchemeReviews()
        reviews.update_authority_reviews(
            AuthorityReview(id_=1, review_date=datetime(2020, 1, 1), source=DataSource.ATF4_BID),
            AuthorityReview(id_=2, review_date=datetime(2020, 1, 2), source=DataSource.ATF4_BID),
        )

        context = SchemeReviewContext.from_domain(reviews)

        assert context.last_reviewed == datetime(2020, 1, 2)


class TestAuthorityReviewRepr:
    def test_from_domain(self) -> None:
        authority_review = AuthorityReview(id_=1, review_date=datetime(2020, 1, 1, 12), source=DataSource.ATF4_BID)

        authority_review_repr = AuthorityReviewRepr.from_domain(authority_review)

        assert authority_review_repr == AuthorityReviewRepr(
            id=1, review_date="2020-01-01T12:00:00", source=DataSourceRepr.ATF4_BID
        )

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
