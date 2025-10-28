from datetime import datetime

from schemes.domain.schemes.data_sources import DataSource
from schemes.domain.schemes.reviews import AuthorityReview
from schemes.infrastructure.api.base import BaseModel
from schemes.infrastructure.api.dates import zoned_to_local


class CapitalSchemeAuthorityReviewModel(BaseModel):
    review_date: datetime

    def to_domain(self) -> AuthorityReview:
        # TODO: id, source
        return AuthorityReview(id_=0, review_date=zoned_to_local(self.review_date), source=DataSource.PULSE_5)
