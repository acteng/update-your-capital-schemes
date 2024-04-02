from tests.e2e.app_client import AuthorityReviewRepr, BidStatusRevisionRepr, SchemeRepr


def build_scheme(
    id_: int,
    name: str,
    funding_programme: str | None = None,
    bid_status: str = "funded",
    authority_reviews: list[AuthorityReviewRepr] | None = None,
) -> SchemeRepr:
    return SchemeRepr(
        id=id_,
        name=name,
        funding_programme=funding_programme,
        bid_status_revisions=[
            BidStatusRevisionRepr(id=None, effective_date_from="1970-01-01", effective_date_to=None, status=bid_status)
        ],
        authority_reviews=authority_reviews or [],
    )
