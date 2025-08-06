from datetime import datetime

from schemes.domain.reporting_window import ReportingWindow
from schemes.domain.schemes.data_sources import DataSource


class AuthorityReview:
    # TODO: domain identifier should be mandatory for transient instances
    def __init__(self, id_: int | None, review_date: datetime, source: DataSource):
        self._id = id_
        self._review_date = review_date
        self._source = source

    @property
    def id(self) -> int | None:
        return self._id

    @property
    def review_date(self) -> datetime:
        return self._review_date

    @property
    def source(self) -> DataSource:
        return self._source


class SchemeReviews:
    def __init__(self) -> None:
        self._authority_reviews: list[AuthorityReview] = []

    @property
    def authority_reviews(self) -> list[AuthorityReview]:
        return list(self._authority_reviews)

    def update_authority_review(self, authority_review: AuthorityReview) -> None:
        self._authority_reviews.append(authority_review)

    def update_authority_reviews(self, *authority_reviews: AuthorityReview) -> None:
        for authority_review in authority_reviews:
            self.update_authority_review(authority_review)

    @property
    def last_reviewed(self) -> datetime | None:
        return (
            sorted(authority_review.review_date for authority_review in self._authority_reviews)[-1]
            if self._authority_reviews
            else None
        )

    def needs_review(self, reporting_window: ReportingWindow) -> bool:
        last_reviewed = self.last_reviewed
        return last_reviewed is None or last_reviewed < reporting_window.window.date_from
