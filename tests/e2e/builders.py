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
