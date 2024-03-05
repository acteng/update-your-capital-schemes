from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import BooleanField

from schemes.domain.schemes import AuthorityReview, DataSource, SchemeReviews
from schemes.views.forms import FieldsetGovCheckboxInput
from schemes.views.schemes.data_source import DataSourceRepr


class SchemeReviewForm(FlaskForm):  # type: ignore
    up_to_date = BooleanField(widget=FieldsetGovCheckboxInput())

    def update_domain(self, reviews: SchemeReviews, now: datetime) -> None:
        reviews.update_authority_review(AuthorityReview(id_=None, review_date=now, source=DataSource.AUTHORITY_UPDATE))


@dataclass(frozen=True)
class SchemeReviewContext:
    form: SchemeReviewForm = field(default_factory=SchemeReviewForm)


@dataclass(frozen=True)
class AuthorityReviewRepr:
    id: int
    review_date: str
    source: DataSourceRepr

    @classmethod
    def from_domain(cls, authority_review: AuthorityReview) -> AuthorityReviewRepr:
        if not authority_review.id:
            raise ValueError("Authority review must be persistent")

        return AuthorityReviewRepr(
            id=authority_review.id,
            review_date=authority_review.review_date.isoformat(),
            source=DataSourceRepr.from_domain(authority_review.source),
        )

    def to_domain(self) -> AuthorityReview:
        return AuthorityReview(
            id_=self.id, review_date=datetime.fromisoformat(self.review_date), source=self.source.to_domain()
        )
