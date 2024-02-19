from datetime import datetime

from schemes.domain.schemes import (
    DataSource,
    Scheme,
    SchemeFunding,
    SchemeMilestones,
    SchemeOutputs,
)
from schemes.domain.schemes.schemes import AuthorityReview


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

    def test_last_reviewed(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.update_authority_review(
            AuthorityReview(id_=1, review_date=datetime(2020, 1, 2), source=DataSource.ATF4_BID)
        )
        scheme.update_authority_review(
            AuthorityReview(id_=2, review_date=datetime(2020, 1, 4), source=DataSource.ATF4_BID)
        )
        scheme.update_authority_review(
            AuthorityReview(id_=3, review_date=datetime(2020, 1, 3), source=DataSource.ATF4_BID)
        )

        assert scheme.last_reviewed == datetime(2020, 1, 4)

    def test_last_reviewed_when_no_authority_reviews(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)

        assert scheme.last_reviewed is None

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
