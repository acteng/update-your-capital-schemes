from tests.e2e.api_client import (
    CapitalSchemeAuthorityReviewModel,
    CapitalSchemeBidStatusDetailsModel,
    CapitalSchemeFinancialModel,
    CapitalSchemeMilestonesModel,
    CapitalSchemeModel,
    CapitalSchemeOutputModel,
    CapitalSchemeOverviewModel,
    CollectionModel,
)
from tests.e2e.app_client import (
    AuthorityReviewRepr,
    BidStatusRevisionRepr,
    FinancialRevisionRepr,
    MilestoneRevisionRepr,
    OutputRevisionRepr,
    OverviewRevisionRepr,
    SchemeRepr,
)


def build_scheme(
    id_: int,
    reference: str,
    name: str,
    authority_abbreviation: str,
    type_: str = "construction",
    funding_programme: str = "ATF2",
    bid_status: str = "funded",
    financial_revisions: list[FinancialRevisionRepr] | None = None,
    milestone_revisions: list[MilestoneRevisionRepr] | None = None,
    output_revisions: list[OutputRevisionRepr] | None = None,
    authority_reviews: list[AuthorityReviewRepr] | None = None,
) -> SchemeRepr:
    return SchemeRepr(
        id=id_,
        reference=reference,
        overview_revisions=[
            OverviewRevisionRepr(
                id=None,
                effective_date_from="1970-01-01",
                effective_date_to=None,
                name=name,
                authority_abbreviation=authority_abbreviation,
                type=type_,
                funding_programme=funding_programme,
            )
        ],
        bid_status_revisions=[
            BidStatusRevisionRepr(id=None, effective_date_from="1970-01-01", effective_date_to=None, status=bid_status)
        ],
        financial_revisions=financial_revisions or [],
        milestone_revisions=milestone_revisions or [],
        output_revisions=output_revisions or [],
        authority_reviews=authority_reviews or [],
    )


def build_capital_scheme_model(
    reference: str,
    name: str,
    bid_submitting_authority: str,
    funding_programme: str,
    type_: str = "construction",
    bid_status_details: CapitalSchemeBidStatusDetailsModel | None = None,
    financials: list[CapitalSchemeFinancialModel] | None = None,
    milestones: CapitalSchemeMilestonesModel | None = None,
    outputs: list[CapitalSchemeOutputModel] | None = None,
    authority_review: CapitalSchemeAuthorityReviewModel | None = None,
) -> CapitalSchemeModel:
    return CapitalSchemeModel(
        reference=reference,
        overview=CapitalSchemeOverviewModel(
            name=name,
            bid_submitting_authority=bid_submitting_authority,
            funding_programme=funding_programme,
            type=type_,
        ),
        bid_status_details=bid_status_details or CapitalSchemeBidStatusDetailsModel(bid_status="funded"),
        financials=CollectionModel[CapitalSchemeFinancialModel](items=financials or []),
        milestones=milestones or CapitalSchemeMilestonesModel(current_milestone=None, items=[]),
        outputs=CollectionModel[CapitalSchemeOutputModel](items=outputs or []),
        authority_review=authority_review,
    )
