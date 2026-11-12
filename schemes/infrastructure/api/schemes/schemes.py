from typing import Any

from schemes.domain.schemes.financials import FundingProgramme, SchemeFunding
from schemes.domain.schemes.schemes import Scheme, SchemeRepository
from schemes.infrastructure.api.authorities import AuthorityModel
from schemes.infrastructure.api.base import BaseModel
from schemes.infrastructure.api.collections import CollectionModel
from schemes.infrastructure.api.funding_programmes import FundingProgrammeModel
from schemes.infrastructure.api.schemes.authority_reviews import (
    CapitalSchemeAuthorityReviewModel,
    CreateCapitalSchemeAuthorityReviewModel,
)
from schemes.infrastructure.api.schemes.financials import CapitalSchemeFinancialsModel, CapitalSchemeSpendModel
from schemes.infrastructure.api.schemes.improvements import ImprovementModel
from schemes.infrastructure.api.schemes.milestones import CapitalSchemeMilestoneModel
from schemes.infrastructure.api.schemes.outputs import CapitalSchemeOutputModel
from schemes.infrastructure.api.schemes.overviews import CapitalSchemeOverviewModel
from schemes.infrastructure.api.schemes.statuses import CapitalSchemeStatusModel
from schemes.oauth import AsyncBaseApp, ClientAsyncBaseApp


class CapitalSchemeModel(BaseModel):
    reference: str
    overview: CapitalSchemeOverviewModel
    status: CapitalSchemeStatusModel
    financials: CapitalSchemeFinancialsModel
    milestones: CollectionModel[CapitalSchemeMilestoneModel]
    outputs: CollectionModel[CapitalSchemeOutputModel]
    authority_review: CapitalSchemeAuthorityReviewModel | None = None

    def to_domain(
        self, authority_model: AuthorityModel, funding_programme_models: list[FundingProgrammeModel]
    ) -> Scheme:
        scheme = Scheme(
            reference=self.reference,
            overview=self.overview.to_domain(authority_model),
            status=self.status.status.to_domain(),
        )
        scheme.financials.update_fundings(*self.financials.to_funding_domain(funding_programme_models))
        spend = self.financials.to_spend_domain()
        if spend:
            scheme.financials.update_spend(spend)
        scheme.milestones.update_milestones(*[milestone.to_domain() for milestone in self.milestones.items])
        scheme.outputs.update_outputs(*[output.to_domain() for output in self.outputs.items])

        if self.authority_review:
            scheme.reviews.update_authority_review(self.authority_review.to_domain())

        return scheme


class CapitalSchemeItemModel(BaseModel):
    reference: str
    overview: CapitalSchemeOverviewModel
    status: CapitalSchemeStatusModel
    authority_review: CapitalSchemeAuthorityReviewModel | None = None

    def to_domain(self, authority_model: AuthorityModel) -> Scheme:
        scheme = Scheme(
            reference=self.reference,
            overview=self.overview.to_domain(authority_model),
            status=self.status.status.to_domain(),
        )
        # TODO: financials, milestones, outputs

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

            improvement_url = capital_scheme_model.overview.improvement
            if not improvement_url:
                return None

            improvement_model = await self._get_improvement_model_by_url(client, str(improvement_url))

            authority_url = improvement_model.overview.funding_managed_by
            authority_model = await self._get_authority_model_by_url(client, str(authority_url))

            funding_programmes_model = await self._get_funding_programmes_model(client)

            return capital_scheme_model.to_domain(authority_model, funding_programmes_model.items)

    async def get_by_authority(self, authority_abbreviation: str) -> list[Scheme]:
        async with self._remote_app.client() as client:
            authority_url = f"/authorities/{authority_abbreviation}"
            authority_model = await self._get_authority_model_by_url(client, authority_url)
            funding_programmes_model = await self._get_funding_programmes_model(
                client, is_eligible_for_authority_update=True
            )
            funding_programme_codes = [
                funding_programme_model.code for funding_programme_model in funding_programmes_model.items
            ]

            capital_scheme_items_model = await self._get_capital_scheme_items_model_by_url(
                client, str(authority_model.funding_managed_by_capital_schemes), funding_programme_codes
            )
            return [
                self._add_dummy_eligible_funding_programme(capital_scheme_item_model.to_domain(authority_model))
                for capital_scheme_item_model in capital_scheme_items_model.items
            ]

    @staticmethod
    def _add_dummy_eligible_funding_programme(scheme: Scheme) -> Scheme:
        """
        The capital scheme item model does not contain funding but whether a scheme is updateable depends on an eligible
        for authority update funding programme being present. Add a placeholder funding so that the scheme can be
        updated.

        This can be justified as the input capital schemes are already filtered by funding programmes that are eligible
        for authority update.
        """
        scheme.financials.update_funding(
            SchemeFunding(
                funding_programme=FundingProgramme(code="dummy", is_eligible_for_authority_update=True), amount=0
            )
        )
        return scheme

    async def update(self, scheme: Scheme) -> None:
        async with self._remote_app.client() as client:
            await self._update_financials(client, scheme)
            await self._update_milestones(client, scheme)
            await self._update_authority_reviews(client, scheme)

    async def _get_funding_programmes_model(
        self, remote_app: AsyncBaseApp, is_eligible_for_authority_update: bool | None = None
    ) -> CollectionModel[FundingProgrammeModel]:
        params = (
            {"eligible-for-authority-update": is_eligible_for_authority_update}
            if is_eligible_for_authority_update is not None
            else None
        )
        response = await remote_app.get("/funding-programmes", params=params, request=self._dummy_request())
        response.raise_for_status()
        return CollectionModel[FundingProgrammeModel].model_validate(response.json())

    async def _get_capital_scheme_items_model_by_url(
        self,
        remote_app: AsyncBaseApp,
        url: str,
        funding_programme_codes: list[str],
    ) -> CollectionModel[CapitalSchemeItemModel]:
        response = await remote_app.get(
            url,
            params={"funding-programme-code": funding_programme_codes, "status": "active"},
            request=self._dummy_request(),
        )
        response.raise_for_status()
        return CollectionModel[CapitalSchemeItemModel].model_validate(response.json())

    async def _get_capital_scheme_model_by_url(self, remote_app: AsyncBaseApp, url: str) -> CapitalSchemeModel:
        response = await remote_app.get(url, request=self._dummy_request())
        response.raise_for_status()
        return CapitalSchemeModel.model_validate(response.json())

    async def _get_authority_model_by_url(self, remote_app: AsyncBaseApp, url: str) -> AuthorityModel:
        response = await remote_app.get(url, request=self._dummy_request())
        response.raise_for_status()
        return AuthorityModel.model_validate(response.json())

    async def _get_improvement_model_by_url(self, remote_app: AsyncBaseApp, url: str) -> ImprovementModel:
        response = await remote_app.get(url, request=self._dummy_request())
        response.raise_for_status()
        return ImprovementModel.model_validate(response.json())

    async def _update_financials(self, remote_app: AsyncBaseApp, scheme: Scheme) -> None:
        spend = scheme.financials.spend
        if spend and spend.surrogate_id is None:
            spend_model = CapitalSchemeSpendModel.from_domain(spend)
            await self._create_spend(remote_app, scheme.reference, spend_model)

    async def _create_spend(
        self, remote_app: AsyncBaseApp, capital_scheme_reference: str, spend_model: CapitalSchemeSpendModel
    ) -> None:
        spend_json = spend_model.model_dump(mode="json", by_alias=True)
        response = await remote_app.post(
            f"/capital-schemes/{capital_scheme_reference}/financials/spend",
            json=spend_json,
            request=self._dummy_request(),
        )
        response.raise_for_status()

    async def _update_milestones(self, remote_app: AsyncBaseApp, scheme: Scheme) -> None:
        new_milestones = [milestone for milestone in scheme.milestones.milestones if milestone.surrogate_id is None]
        if new_milestones:
            milestones_model = CollectionModel[CapitalSchemeMilestoneModel](
                items=[CapitalSchemeMilestoneModel.from_domain(milestone) for milestone in new_milestones]
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
            if authority_review.surrogate_id is None:
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
