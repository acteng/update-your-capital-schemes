from dataclasses import dataclass, field
from datetime import datetime
from typing import Self

from flask_wtf import FlaskForm
from wtforms import BooleanField
from wtforms.validators import InputRequired

from schemes.domain.schemes.data_sources import DataSource
from schemes.domain.schemes.reviews import AuthorityReview, SchemeReviews
from schemes.views.forms import FieldsetGovCheckboxInput


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
    def from_domain(cls, reviews: SchemeReviews) -> Self:
        return cls(last_reviewed=reviews.last_reviewed, form=SchemeReviewForm())
