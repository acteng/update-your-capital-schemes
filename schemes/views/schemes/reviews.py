from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from flask_wtf import FlaskForm
from pydantic import BaseModel
from wtforms import BooleanField
from wtforms.validators import InputRequired

from schemes.domain.schemes.data_sources import DataSource
from schemes.domain.schemes.reviews import AuthorityReview, SchemeReviews
from schemes.views.forms import FieldsetGovCheckboxInput
from schemes.views.schemes.data_sources import DataSourceRepr


class SchemeReviewForm(FlaskForm):  # type: ignore
    up_to_date = BooleanField(
        widget=FieldsetGovCheckboxInput(),
        validators=[InputRequired(message="Confirm this scheme is up-to-date")],
    )

    def update_domain(self, reviews: SchemeReviews, now: datetime) -> None:
        reviews.update_authority_review(AuthorityReview(id_=None, review_date=now, source=DataSource.AUTHORITY_UPDATE))


@dataclass(frozen=True)
class SchemeReviewContext:
    last_reviewed: datetime | None
    form: SchemeReviewForm = field(default_factory=SchemeReviewForm)

    @classmethod
    def from_domain(cls, reviews: SchemeReviews) -> SchemeReviewContext:
        return cls(last_reviewed=reviews.last_reviewed, form=SchemeReviewForm())


class AuthorityReviewRepr(BaseModel):
    review_date: str
    source: DataSourceRepr
    id: int | None = None

    @classmethod
    def from_domain(cls, authority_review: AuthorityReview) -> AuthorityReviewRepr:
        return cls(
            id=authority_review.id,
            review_date=authority_review.review_date.isoformat(),
            source=DataSourceRepr.from_domain(authority_review.source),
        )

    def to_domain(self) -> AuthorityReview:
        return AuthorityReview(
            id_=self.id, review_date=datetime.fromisoformat(self.review_date), source=self.source.to_domain()
        )
