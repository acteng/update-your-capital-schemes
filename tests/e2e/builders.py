from tests.e2e.app_client import (
    AuthorityReviewRepr,
    BidStatusRevisionRepr,
    FinancialRevisionRepr,
    MilestoneRevisionRepr,
    OutputRevisionRepr,
    SchemeRepr,
)


def build_scheme(
    id_: int,
    name: str,
    type_: str | None = None,
    funding_programme: str | None = None,
    bid_status: str = "funded",
    financial_revisions: list[FinancialRevisionRepr] | None = None,
    milestone_revisions: list[MilestoneRevisionRepr] | None = None,
    output_revisions: list[OutputRevisionRepr] | None = None,
    authority_reviews: list[AuthorityReviewRepr] | None = None,
) -> SchemeRepr:
    return SchemeRepr(
        id=id_,
        name=name,
        type=type_,
        funding_programme=funding_programme,
        bid_status_revisions=[
            BidStatusRevisionRepr(id=None, effective_date_from="1970-01-01", effective_date_to=None, status=bid_status)
        ],
        financial_revisions=financial_revisions or [],
        milestone_revisions=milestone_revisions or [],
        output_revisions=output_revisions or [],
        authority_reviews=authority_reviews or [],
    )