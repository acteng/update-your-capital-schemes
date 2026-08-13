from typing import Any

from pydantic import AnyUrl

from schemes.infrastructure.api.authorities import AuthorityModel
from schemes.infrastructure.api.funding_programmes import FundingProgrammeItemModel
from schemes.infrastructure.api.schemes.overviews import CapitalSchemeOverviewModel, CapitalSchemeTypeModel
from schemes.infrastructure.api.schemes.statuses import CapitalSchemeStatusModel, StatusModel

_dummy_funding_programme_url = "https://api.example/funding-programmes/dummy"
_dummy_authority_url = "https://api.example/authorities/dummy"
_dummy_bid_submitting_capital_schemes_url = "https://api.example/authorities/dummy/capital-schemes/bid-submitting"


def build_funding_programme_item_model(
    id_: AnyUrl = AnyUrl(_dummy_funding_programme_url), code: str = "dummy"
) -> FundingProgrammeItemModel:
    return FundingProgrammeItemModel(id=id_, code=code)


def build_authority_model(
    id_: AnyUrl = AnyUrl(_dummy_authority_url),
    abbreviation: str = "dummy",
    full_name: str = "dummy",
    bid_submitting_capital_schemes: AnyUrl = AnyUrl(_dummy_bid_submitting_capital_schemes_url),
) -> AuthorityModel:
    return AuthorityModel(
        id=id_,
        abbreviation=abbreviation,
        full_name=full_name,
        bid_submitting_capital_schemes=bid_submitting_capital_schemes,
    )


def build_overview_model(
    name: str = "dummy",
    bid_submitting_authority: AnyUrl = AnyUrl(_dummy_authority_url),
    funding_programme: AnyUrl = AnyUrl(_dummy_funding_programme_url),
    type_: CapitalSchemeTypeModel = CapitalSchemeTypeModel.DEVELOPMENT,
) -> CapitalSchemeOverviewModel:
    return CapitalSchemeOverviewModel(
        name=name, bid_submitting_authority=bid_submitting_authority, funding_programme=funding_programme, type=type_
    )


def build_status_model(status: StatusModel = StatusModel.PIPELINE) -> CapitalSchemeStatusModel:
    return CapitalSchemeStatusModel(status=status)


def build_funding_programme_json(id_: str = _dummy_funding_programme_url, code: str = "dummy") -> dict[str, Any]:
    return {"@id": id_, "code": code}


def build_funding_programme_item_json(id_: str = _dummy_funding_programme_url, code: str = "dummy") -> dict[str, Any]:
    return {"@id": id_, "code": code}


def build_authority_json(
    id_: str = _dummy_authority_url,
    abbreviation: str = "dummy",
    full_name: str = "dummy",
    bid_submitting_capital_schemes: str = _dummy_bid_submitting_capital_schemes_url,
) -> dict[str, Any]:
    return {
        "@id": id_,
        "abbreviation": abbreviation,
        "fullName": full_name,
        "bidSubmittingCapitalSchemes": bid_submitting_capital_schemes,
    }


def build_overview_json(
    name: str = "dummy",
    bid_submitting_authority: str = _dummy_authority_url,
    funding_programme: str = _dummy_funding_programme_url,
    type_: str = "development",
) -> dict[str, Any]:
    return {
        "name": name,
        "bidSubmittingAuthority": bid_submitting_authority,
        "fundingProgramme": funding_programme,
        "type": type_,
    }


def build_status_json(status: str = "pipeline") -> dict[str, Any]:
    return {"status": status}


def build_financial_json(type_: str = "expected cost", amount: int = 0, source: str = "Pulse 5") -> dict[str, Any]:
    return {"type": type_, "amount": amount, "source": source}


def build_milestone_json(
    milestone: str = "public consultation completed",
    observation_type: str = "planned",
    status_date: str = "1970-01-01",
    source: str = "Pulse 5",
) -> dict[str, Any]:
    return {"milestone": milestone, "observationType": observation_type, "statusDate": status_date, "source": source}


def build_output_json(
    type_: str = "new segregated cycling facility",
    measure: str = "miles",
    observation_type: str = "planned",
    value: str = "0.000000",
) -> dict[str, Any]:
    return {"type": type_, "measure": measure, "observationType": observation_type, "value": value}


def build_authority_review_json(review_date: str = "1970-01-01T00:00:00Z", source: str = "Pulse 5") -> dict[str, Any]:
    return {"reviewDate": review_date, "source": source}


def build_create_authority_review_json(source: str = "Pulse 5") -> dict[str, Any]:
    return {"source": source}


def build_capital_scheme_json(
    reference: str = "dummy",
    overview: dict[str, Any] | None = None,
    status: dict[str, Any] | None = None,
    financials: list[dict[str, Any]] | None = None,
    milestones: list[dict[str, Any]] | None = None,
    outputs: list[dict[str, Any]] | None = None,
    authority_review: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "reference": reference,
        "overview": overview or build_overview_json(),
        "status": status or build_status_json(),
        "financials": {"items": financials or []},
        "milestones": {"items": milestones or []},
        "outputs": {"items": outputs or []},
        "authorityReview": authority_review if authority_review else None,
    }


def build_capital_scheme_item_json(
    reference: str = "dummy",
    overview: dict[str, Any] | None = None,
    authority_review: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "reference": reference,
        "overview": overview or build_overview_json(),
        "authorityReview": authority_review if authority_review else None,
    }
