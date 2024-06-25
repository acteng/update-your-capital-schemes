import inject
from sqlalchemy import delete, select
from sqlalchemy.orm import Session, selectinload, sessionmaker

from schemes.dicts import inverse_dict
from schemes.domain.dates import DateRange
from schemes.domain.schemes import (
    AuthorityReview,
    BidStatusRevision,
    FinancialRevision,
    FundingProgramme,
    FundingProgrammes,
    MilestoneRevision,
    OutputRevision,
    Scheme,
    SchemeRepository,
    SchemeType,
)
from schemes.infrastructure.database import (
    CapitalSchemeAuthorityReviewEntity,
    CapitalSchemeBidStatusEntity,
    CapitalSchemeEntity,
    CapitalSchemeFinancialEntity,
    CapitalSchemeInterventionEntity,
    CapitalSchemeMilestoneEntity,
)
from schemes.infrastructure.database.schemes.data_source import DataSourceMapper
from schemes.infrastructure.database.schemes.funding import (
    BidStatusMapper,
    FinancialTypeMapper,
)
from schemes.infrastructure.database.schemes.milestones import MilestoneMapper
from schemes.infrastructure.database.schemes.observations import ObservationTypeMapper
from schemes.infrastructure.database.schemes.outputs import OutputTypeMeasureMapper


class DatabaseSchemeRepository(SchemeRepository):
    @inject.autoparams()
    def __init__(self, session_maker: sessionmaker[Session]):
        self._session_maker = session_maker
        self._scheme_type_mapper = SchemeTypeMapper()
        self._funding_programme_mapper = FundingProgrammeMapper()
        self._bid_status_mapper = BidStatusMapper()
        self._milestone_mapper = MilestoneMapper()
        self._observation_type_mapper = ObservationTypeMapper()
        self._financial_type_mapper = FinancialTypeMapper()
        self._data_source_mapper = DataSourceMapper()
        self._output_type_measure_mapper = OutputTypeMeasureMapper()

    def add(self, *schemes: Scheme) -> None:
        with self._session_maker() as session:
            session.add_all(self._capital_scheme_from_domain(scheme) for scheme in schemes)
            session.commit()

    def clear(self) -> None:
        with self._session_maker() as session:
            session.execute(delete(CapitalSchemeAuthorityReviewEntity))
            session.execute(delete(CapitalSchemeInterventionEntity))
            session.execute(delete(CapitalSchemeMilestoneEntity))
            session.execute(delete(CapitalSchemeFinancialEntity))
            session.execute(delete(CapitalSchemeBidStatusEntity))
            session.execute(delete(CapitalSchemeEntity))
            session.commit()

    def get(self, id_: int) -> Scheme | None:
        with self._session_maker() as session:
            result = session.scalars(
                select(CapitalSchemeEntity)
                .options(selectinload("*"))
                .where(CapitalSchemeEntity.capital_scheme_id == id_)
            )
            row = result.one_or_none()
            return self._capital_scheme_to_domain(row) if row else None

    def get_by_authority(self, authority_id: int) -> list[Scheme]:
        with self._session_maker() as session:
            result = session.scalars(
                select(CapitalSchemeEntity)
                .options(selectinload("*"))
                .where(CapitalSchemeEntity.bid_submitting_authority_id == authority_id)
                .order_by(CapitalSchemeEntity.capital_scheme_id)
            )
            return [self._capital_scheme_to_domain(row) for row in result]

    def update(self, scheme: Scheme) -> None:
        with self._session_maker() as session:
            session.merge(self._capital_scheme_from_domain(scheme))
            session.commit()

    def _capital_scheme_from_domain(self, scheme: Scheme) -> CapitalSchemeEntity:
        return CapitalSchemeEntity(
            capital_scheme_id=scheme.id,
            scheme_name=scheme.name,
            bid_submitting_authority_id=scheme.authority_id,
            scheme_type_id=self._scheme_type_mapper.to_id(scheme.type),
            funding_programme_id=self._funding_programme_mapper.to_id(scheme.funding_programme),
            capital_scheme_bid_statuses=[
                self._capital_scheme_bid_status_from_domain(bid_status_revision)
                for bid_status_revision in scheme.funding.bid_status_revisions
            ],
            capital_scheme_financials=[
                self._capital_scheme_financial_from_domain(financial_revision)
                for financial_revision in scheme.funding.financial_revisions
            ],
            capital_scheme_milestones=[
                self._capital_scheme_milestone_from_domain(milestone_revision)
                for milestone_revision in scheme.milestones.milestone_revisions
            ],
            capital_scheme_interventions=[
                self._capital_scheme_intervention_from_domain(output_revision)
                for output_revision in scheme.outputs.output_revisions
            ],
            capital_scheme_authority_reviews=[
                self._capital_scheme_authority_review_from_domain(authority_review)
                for authority_review in scheme.reviews.authority_reviews
            ],
        )

    def _capital_scheme_to_domain(self, capital_scheme: CapitalSchemeEntity) -> Scheme:
        scheme = Scheme(
            id_=capital_scheme.capital_scheme_id,
            name=capital_scheme.scheme_name,
            authority_id=capital_scheme.bid_submitting_authority_id,
            type_=self._scheme_type_mapper.to_domain(capital_scheme.scheme_type_id),
            funding_programme=self._funding_programme_mapper.to_domain(capital_scheme.funding_programme_id),
        )

        for capital_scheme_bid_status in capital_scheme.capital_scheme_bid_statuses:
            scheme.funding.update_bid_status(self._capital_scheme_bid_status_to_domain(capital_scheme_bid_status))

        for capital_scheme_financial in capital_scheme.capital_scheme_financials:
            scheme.funding.update_financial(self._capital_scheme_financial_to_domain(capital_scheme_financial))

        for capital_scheme_milestone in capital_scheme.capital_scheme_milestones:
            scheme.milestones.update_milestone(self._capital_scheme_milestone_to_domain(capital_scheme_milestone))

        for capital_scheme_intervention in capital_scheme.capital_scheme_interventions:
            scheme.outputs.update_output(self._capital_scheme_intervention_to_domain(capital_scheme_intervention))

        for capital_scheme_authority_review in capital_scheme.capital_scheme_authority_reviews:
            scheme.reviews.update_authority_review(
                self._capital_scheme_authority_review_to_domain(capital_scheme_authority_review)
            )

        return scheme

    def _capital_scheme_bid_status_from_domain(
        self, bid_status_revision: BidStatusRevision
    ) -> CapitalSchemeBidStatusEntity:
        return CapitalSchemeBidStatusEntity(
            capital_scheme_bid_status_id=bid_status_revision.id,
            effective_date_from=bid_status_revision.effective.date_from,
            effective_date_to=bid_status_revision.effective.date_to,
            bid_status_id=self._bid_status_mapper.to_id(bid_status_revision.status),
        )

    def _capital_scheme_bid_status_to_domain(
        self, capital_scheme_bid_status: CapitalSchemeBidStatusEntity
    ) -> BidStatusRevision:
        return BidStatusRevision(
            id_=capital_scheme_bid_status.capital_scheme_bid_status_id,
            effective=DateRange(
                capital_scheme_bid_status.effective_date_from, capital_scheme_bid_status.effective_date_to
            ),
            status=self._bid_status_mapper.to_domain(capital_scheme_bid_status.bid_status_id),
        )

    def _capital_scheme_financial_from_domain(
        self, financial_revision: FinancialRevision
    ) -> CapitalSchemeFinancialEntity:
        return CapitalSchemeFinancialEntity(
            capital_scheme_financial_id=financial_revision.id,
            effective_date_from=financial_revision.effective.date_from,
            effective_date_to=financial_revision.effective.date_to,
            financial_type_id=self._financial_type_mapper.to_id(financial_revision.type),
            amount=financial_revision.amount,
            data_source_id=self._data_source_mapper.to_id(financial_revision.source),
        )

    def _capital_scheme_financial_to_domain(
        self, capital_scheme_financial: CapitalSchemeFinancialEntity
    ) -> FinancialRevision:
        return FinancialRevision(
            id_=capital_scheme_financial.capital_scheme_financial_id,
            effective=DateRange(
                capital_scheme_financial.effective_date_from, capital_scheme_financial.effective_date_to
            ),
            type_=self._financial_type_mapper.to_domain(capital_scheme_financial.financial_type_id),
            amount=capital_scheme_financial.amount,
            source=self._data_source_mapper.to_domain(capital_scheme_financial.data_source_id),
        )

    def _capital_scheme_milestone_from_domain(
        self, milestone_revision: MilestoneRevision
    ) -> CapitalSchemeMilestoneEntity:
        return CapitalSchemeMilestoneEntity(
            capital_scheme_milestone_id=milestone_revision.id,
            effective_date_from=milestone_revision.effective.date_from,
            effective_date_to=milestone_revision.effective.date_to,
            milestone_id=self._milestone_mapper.to_id(milestone_revision.milestone),
            observation_type_id=self._observation_type_mapper.to_id(milestone_revision.observation_type),
            status_date=milestone_revision.status_date,
            data_source_id=self._data_source_mapper.to_id(milestone_revision.source),
        )

    def _capital_scheme_milestone_to_domain(
        self, capital_scheme_milestone: CapitalSchemeMilestoneEntity
    ) -> MilestoneRevision:
        return MilestoneRevision(
            id_=capital_scheme_milestone.capital_scheme_milestone_id,
            effective=DateRange(
                capital_scheme_milestone.effective_date_from, capital_scheme_milestone.effective_date_to
            ),
            milestone=self._milestone_mapper.to_domain(capital_scheme_milestone.milestone_id),
            observation_type=self._observation_type_mapper.to_domain(capital_scheme_milestone.observation_type_id),
            status_date=capital_scheme_milestone.status_date,
            source=self._data_source_mapper.to_domain(capital_scheme_milestone.data_source_id),
        )

    def _capital_scheme_intervention_from_domain(
        self, output_revision: OutputRevision
    ) -> CapitalSchemeInterventionEntity:
        return CapitalSchemeInterventionEntity(
            capital_scheme_intervention_id=output_revision.id,
            effective_date_from=output_revision.effective.date_from,
            effective_date_to=output_revision.effective.date_to,
            intervention_type_measure_id=self._output_type_measure_mapper.to_id(output_revision.type_measure),
            intervention_value=output_revision.value,
            observation_type_id=self._observation_type_mapper.to_id(output_revision.observation_type),
        )

    def _capital_scheme_intervention_to_domain(
        self, capital_scheme_intervention: CapitalSchemeInterventionEntity
    ) -> OutputRevision:
        return OutputRevision(
            id_=capital_scheme_intervention.capital_scheme_intervention_id,
            effective=DateRange(
                capital_scheme_intervention.effective_date_from, capital_scheme_intervention.effective_date_to
            ),
            type_measure=self._output_type_measure_mapper.to_domain(
                capital_scheme_intervention.intervention_type_measure_id
            ),
            value=capital_scheme_intervention.intervention_value,
            observation_type=self._observation_type_mapper.to_domain(capital_scheme_intervention.observation_type_id),
        )

    def _capital_scheme_authority_review_from_domain(
        self, authority_review: AuthorityReview
    ) -> CapitalSchemeAuthorityReviewEntity:
        return CapitalSchemeAuthorityReviewEntity(
            capital_scheme_authority_review_id=authority_review.id,
            review_date=authority_review.review_date,
            data_source_id=self._data_source_mapper.to_id(authority_review.source),
        )

    def _capital_scheme_authority_review_to_domain(
        self, capital_scheme_authority_review: CapitalSchemeAuthorityReviewEntity
    ) -> AuthorityReview:
        return AuthorityReview(
            id_=capital_scheme_authority_review.capital_scheme_authority_review_id,
            review_date=capital_scheme_authority_review.review_date,
            source=self._data_source_mapper.to_domain(capital_scheme_authority_review.data_source_id),
        )


class SchemeTypeMapper:
    _IDS = {
        SchemeType.DEVELOPMENT: 1,
        SchemeType.CONSTRUCTION: 2,
    }

    def to_id(self, type_: SchemeType) -> int:
        return self._IDS[type_]

    def to_domain(self, id_: int) -> SchemeType:
        return inverse_dict(self._IDS)[id_]


class FundingProgrammeMapper:
    _IDS = {FundingProgrammes.ATF2: 1, FundingProgrammes.ATF3: 2, FundingProgrammes.ATF4: 3, FundingProgrammes.ATF4E: 4}

    def to_id(self, funding_programme: FundingProgramme) -> int:
        return self._IDS[funding_programme]

    def to_domain(self, id_: int) -> FundingProgramme:
        return inverse_dict(self._IDS)[id_]
