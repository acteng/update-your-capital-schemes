from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from flask_wtf import FlaskForm

from schemes.domain.schemes import AuthorityReview
from schemes.views.schemes.data_source import DataSourceRepr


class SchemeReviewForm(FlaskForm):  # type: ignore
    pass


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
