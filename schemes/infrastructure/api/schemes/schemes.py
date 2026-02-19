import asyncio
from typing import Any

from pydantic import AnyUrl

from schemes.domain.schemes.schemes import Scheme, SchemeRepository
from schemes.infrastructure.api.authorities import AuthorityModel
from schemes.infrastructure.api.base import BaseModel
from schemes.infrastructure.api.collections import CollectionModel
from schemes.infrastructure.api.funding_programmes import FundingProgrammeItemModel, FundingProgrammeModel
from schemes.infrastructure.api.schemes.authority_reviews import (
    CapitalSchemeAuthorityReviewModel,
    CreateCapitalSchemeAuthorityReviewModel,
)
from schemes.infrastructure.api.schemes.bid_statuses import CapitalSchemeBidStatusDetailsModel
from schemes.infrastructure.api.schemes.financials import CapitalSchemeFinancialModel
from schemes.infrastructure.api.schemes.milestones import CapitalSchemeMilestoneModel
from schemes.infrastructure.api.schemes.outputs import CapitalSchemeOutputModel
from schemes.infrastructure.api.schemes.overviews import CapitalSchemeOverviewModel
from schemes.oauth import AsyncBaseApp, ClientAsyncBaseApp


class CapitalSchemeModel(BaseModel):
    reference: str
    overview: CapitalSchemeOverviewModel
    bid_status_details: CapitalSchemeBidStatusDetailsModel
    financials: CollectionModel[CapitalSchemeFinancialModel]
    milestones: CollectionModel[CapitalSchemeMilestoneModel]
    outputs: CollectionModel[CapitalSchemeOutputModel]
    authority_review: CapitalSchemeAuthorityReviewModel | None = None

    def to_domain(
        self,
        authority_models: list[AuthorityModel],
        funding_programme_item_models: list[FundingProgrammeModel] | list[FundingProgrammeItemModel],
    ) -> Scheme:
        # TODO: id
        scheme = Scheme(id_=0, reference=self.reference)
        scheme.overview.update_overview(self.overview.to_domain(authority_models, funding_programme_item_models))
        scheme.funding.update_bid_status(self.bid_status_details.to_domain())
        scheme.funding.update_financials(*[financial.to_domain() for financial in self.financials.items])
        scheme.milestones.update_milestones(*[milestone.to_domain() for milestone in self.milestones.items])
        scheme.outputs.update_outputs(*[output.to_domain() for output in self.outputs.items])

        if self.authority_review:
            scheme.reviews.update_authority_review(self.authority_review.to_domain())

        return scheme


class ApiSchemeRepository(SchemeRepository):
    def __init__(self, remote_app: ClientAsyncBaseApp):
        self._remote_app = remote_app

    async def get(self, reference: str) -> Scheme | None:
        async with self._remote_app.client() as client:
            response = await client.get(f"/capital-schemes/{reference}", request=self._dummy_request())

            if response.status_code == 404:
                return None

            response.raise_for_status()
            capital_scheme_model = CapitalSchemeModel.model_validate(response.json())

            authority_url = capital_scheme_model.overview.bid_submitting_authority
            authority_models = [await self._get_authority_model_by_url(client, str(authority_url))]

            funding_programme_url = capital_scheme_model.overview.funding_programme
            funding_programme_models = [
                await self._get_funding_programme_model_by_url(client, str(funding_programme_url))
            ]

            return capital_scheme_model.to_domain(authority_models, funding_programme_models)

    async def get_by_authority(self, authority_abbreviation: str) -> list[Scheme]:
        async with self._remote_app.client() as client:
            authority_url = f"/authorities/{authority_abbreviation}"
            authority_model = await self._get_authority_model_by_url(client, authority_url)
            funding_programme_items_model = await self._get_funding_programme_items_model(client)
            funding_programme_codes = [
                funding_programme_item_model.code
                for funding_programme_item_model in funding_programme_items_model.items
            ]
            milestones = await self._get_milestones(client)

            capital_scheme_urls_model = await self._get_capital_scheme_urls_by_url(
                client, str(authority_model.bid_submitting_capital_schemes), funding_programme_codes, milestones
            )
            capital_scheme_models = await asyncio.gather(
                *[
                    self._get_capital_scheme_model_by_url(client, str(capital_scheme_url))
                    for capital_scheme_url in capital_scheme_urls_model.items
                ]
            )
            return [
                capital_scheme_model.to_domain([authority_model], funding_programme_items_model.items)
                for capital_scheme_model in capital_scheme_models
            ]

    async def update(self, scheme: Scheme) -> None:
        async with self._remote_app.client() as client:
            await self._update_financials(client, scheme)
            await self._update_milestones(client, scheme)
            await self._update_authority_reviews(client, scheme)

    async def _get_funding_programme_items_model(
        self, remote_app: AsyncBaseApp
    ) -> CollectionModel[FundingProgrammeItemModel]:
        response = await remote_app.get(
            "/funding-programmes", params={"eligible-for-authority-update": "true"}, request=self._dummy_request()
        )
        response.raise_for_status()
        return CollectionModel[FundingProgrammeItemModel].model_validate(response.json())

    async def _get_funding_programme_model_by_url(self, remote_app: AsyncBaseApp, url: str) -> FundingProgrammeModel:
        response = await remote_app.get(url, request=self._dummy_request())
        response.raise_for_status()
        return FundingProgrammeModel.model_validate(response.json())

    async def _get_milestones(self, remote_app: AsyncBaseApp) -> list[str]:
        response = await remote_app.get(
            "/capital-schemes/milestones", params={"active": "true", "complete": "false"}, request=self._dummy_request()
        )
        response.raise_for_status()

        collection_model = CollectionModel[str].model_validate(response.json())
        no_milestone = ""
        return collection_model.items + [no_milestone]

    async def _get_capital_scheme_urls_by_url(
        self,
        remote_app: AsyncBaseApp,
        url: str,
        funding_programme_codes: list[str],
        current_milestones: list[str],
    ) -> CollectionModel[AnyUrl]:
        response = await remote_app.get(
            url,
            params={
                "funding-programme-code": funding_programme_codes,
                "bid-status": "funded",
                "current-milestone": current_milestones,
            },
            request=self._dummy_request(),
        )
        response.raise_for_status()
        return CollectionModel[AnyUrl].model_validate(response.json())

    async def _get_capital_scheme_model_by_url(self, remote_app: AsyncBaseApp, url: str) -> CapitalSchemeModel:
        response = await remote_app.get(url, request=self._dummy_request())
        response.raise_for_status()
        return CapitalSchemeModel.model_validate(response.json())

    async def _get_authority_model_by_url(self, remote_app: AsyncBaseApp, url: str) -> AuthorityModel:
        response = await remote_app.get(url, request=self._dummy_request())
        response.raise_for_status()
        return AuthorityModel.model_validate(response.json())

    async def _update_financials(self, remote_app: AsyncBaseApp, scheme: Scheme) -> None:
        for financial_revision in scheme.funding.financial_revisions:
            if financial_revision.id is None:
                financial_model = CapitalSchemeFinancialModel.from_domain(financial_revision)
                await self._create_financial(remote_app, scheme.reference, financial_model)

    async def _create_financial(
        self, remote_app: AsyncBaseApp, capital_scheme_reference: str, financial_model: CapitalSchemeFinancialModel
    ) -> None:
        financial_json = financial_model.model_dump(mode="json", by_alias=True)
        response = await remote_app.post(
            f"/capital-schemes/{capital_scheme_reference}/financials",
            json=financial_json,
            request=self._dummy_request(),
        )
        response.raise_for_status()

    async def _update_milestones(self, remote_app: AsyncBaseApp, scheme: Scheme) -> None:
        new_milestone_revisions = [
            milestone_revision
            for milestone_revision in scheme.milestones.milestone_revisions
            if milestone_revision.id is None
        ]
        if new_milestone_revisions:
            milestones_model = CollectionModel[CapitalSchemeMilestoneModel](
                items=[
                    CapitalSchemeMilestoneModel.from_domain(milestone_revision)
                    for milestone_revision in new_milestone_revisions
                ]
            )
            await self._create_milestones(remote_app, scheme.reference, milestones_model)

    async def _create_milestones(
        self,
        remote_app: AsyncBaseApp,
        capital_scheme_reference: str,
        milestones_model: CollectionModel[CapitalSchemeMilestoneModel],
    ) -> None:
        milestones_json = milestones_model.model_dump(mode="json", by_alias=True)
        response = await remote_app.post(
            f"/capital-schemes/{capital_scheme_reference}/milestones",
            json=milestones_json,
            request=self._dummy_request(),
        )
        response.raise_for_status()

    async def _update_authority_reviews(self, remote_app: AsyncBaseApp, scheme: Scheme) -> None:
        for authority_review in scheme.reviews.authority_reviews:
            if authority_review.id is None:
                authority_review_model = CreateCapitalSchemeAuthorityReviewModel.from_domain(authority_review)
                await self._create_authority_review(remote_app, scheme.reference, authority_review_model)

    async def _create_authority_review(
        self,
        remote_app: AsyncBaseApp,
        capital_scheme_reference: str,
        authority_review_model: CreateCapitalSchemeAuthorityReviewModel,
    ) -> None:
        authority_review_json = authority_review_model.model_dump(mode="json", by_alias=True)
        response = await remote_app.post(
            f"/capital-schemes/{capital_scheme_reference}/authority-reviews",
            json=authority_review_json,
            request=self._dummy_request(),
        )
        response.raise_for_status()

    # See: https://github.com/authlib/authlib/issues/818#issuecomment-3257950062
    @staticmethod
    def _dummy_request() -> Any:
        return object()
