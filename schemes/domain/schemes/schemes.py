from __future__ import annotations

from datetime import datetime
from enum import Enum, auto, unique

from schemes.domain.schemes.funding import DataSource, SchemeFunding
from schemes.domain.schemes.milestones import SchemeMilestones
from schemes.domain.schemes.outputs import SchemeOutputs


class Scheme:
    def __init__(self, id_: int, name: str, authority_id: int):
        self.id = id_
        self.name = name
        self.authority_id = authority_id
        self.type: SchemeType | None = None
        self.funding_programme: FundingProgramme | None = None
        self._authority_reviews: list[AuthorityReview] = []
        self._funding = SchemeFunding()
        self._milestones = SchemeMilestones()
        self._outputs = SchemeOutputs()

    @property
    def reference(self) -> str:
        return f"ATE{self.id:05}"

    @property
    def authority_reviews(self) -> list[AuthorityReview]:
        return list(self._authority_reviews)

    def update_authority_review(self, authority_review: AuthorityReview) -> None:
        self._authority_reviews.append(authority_review)

    @property
    def last_reviewed(self) -> datetime | None:
        return (
            sorted(authority_review.review_date for authority_review in self._authority_reviews)[-1]
            if self._authority_reviews
            else None
        )

    @property
    def funding(self) -> SchemeFunding:
        return self._funding

    @property
    def milestones(self) -> SchemeMilestones:
        return self._milestones

    @property
    def outputs(self) -> SchemeOutputs:
        return self._outputs


@unique
class SchemeType(Enum):
    DEVELOPMENT = auto()
    CONSTRUCTION = auto()


@unique
class FundingProgramme(Enum):
    ATF2 = auto()
    ATF3 = auto()
    ATF4 = auto()
    ATF4E = auto()
    ATF5 = auto()
    MRN = auto()
    LUF = auto()
    CRSTS = auto()


class AuthorityReview:
    def __init__(self, id_: int, review_date: datetime, source: DataSource):
        self.id = id_
        self.review_date = review_date
        self.source = source


class SchemeRepository:
    def add(self, *schemes: Scheme) -> None:
        raise NotImplementedError()

    def clear(self) -> None:
        raise NotImplementedError()

    def get(self, id_: int) -> Scheme | None:
        raise NotImplementedError()

    def get_by_authority(self, authority_id: int) -> list[Scheme]:
        raise NotImplementedError()

    def update(self, scheme: Scheme) -> None:
        raise NotImplementedError()
