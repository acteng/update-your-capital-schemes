from datetime import date, datetime
from decimal import Decimal

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from schemes.domain.authorities import Authority
from schemes.domain.dates import DateRange
from schemes.domain.schemes import (
    AuthorityReview,
    BidStatus,
    BidStatusRevision,
    DataSource,
    FinancialRevision,
    FinancialType,
    FundingProgramme,
    FundingProgrammes,
    Milestone,
    MilestoneRevision,
    ObservationType,
    OutputRevision,
    OutputTypeMeasure,
    OverviewRevision,
    Scheme,
    SchemeType,
)
from schemes.infrastructure.database import (
    CapitalSchemeAuthorityReviewEntity,
    CapitalSchemeBidStatusEntity,
    CapitalSchemeEntity,
    CapitalSchemeFinancialEntity,
    CapitalSchemeInterventionEntity,
    CapitalSchemeMilestoneEntity,
    CapitalSchemeOverviewEntity,
)
from schemes.infrastructure.database.authorities import DatabaseAuthorityRepository
from schemes.infrastructure.database.schemes import DatabaseSchemeRepository
from schemes.infrastructure.database.schemes.schemes import FundingProgrammeMapper
from tests.builders import build_scheme


class TestDatabaseSchemeRepository:
    @pytest.fixture(name="authorities")
    def authorities_fixture(self, session_maker: sessionmaker[Session]) -> DatabaseAuthorityRepository:
        repository: DatabaseAuthorityRepository = DatabaseAuthorityRepository(session_maker)
        return repository

    @pytest.fixture(name="schemes")
    def schemes_fixture(self, session_maker: sessionmaker[Session]) -> DatabaseSchemeRepository:
        repository: DatabaseSchemeRepository = DatabaseSchemeRepository(session_maker)
        return repository

    @pytest.fixture(name="authority", autouse=True)
    def authority_fixture(self, authorities: DatabaseAuthorityRepository) -> None:
        authorities.add(
            Authority(id_=1, name="Liverpool City Region Combined Authority"),
            Authority(id_=2, name="West Yorkshire Combined Authority"),
        )

    def test_add_schemes(self, schemes: DatabaseSchemeRepository, session_maker: sessionmaker[Session]) -> None:
        scheme1 = build_scheme(
            id_=1,
            name="Wirral Package",
            authority_id=1,
            funding_programme=FundingProgrammes.ATF3,
        )

        schemes.add(scheme1, build_scheme(id_=2, name="School Streets", authority_id=1))

        row1: CapitalSchemeEntity
        row2: CapitalSchemeEntity
        with session_maker() as session:
            row1, row2 = session.scalars(select(CapitalSchemeEntity).order_by(CapitalSchemeEntity.capital_scheme_id))
        assert row1.capital_scheme_id == 1 and row1.funding_programme_id == 2
        assert row2.capital_scheme_id == 2

    def test_add_schemes_overview_revisions(
        self, schemes: DatabaseSchemeRepository, session_maker: sessionmaker[Session]
    ) -> None:
        scheme = build_scheme(
            id_=1,
            overview_revisions=[
                OverviewRevision(
                    id_=2,
                    effective=DateRange(datetime(2020, 1, 1), datetime(2020, 2, 1)),
                    name="Wirral Package",
                    authority_id=1,
                    type_=SchemeType.DEVELOPMENT,
                ),
                OverviewRevision(
                    id_=3,
                    effective=DateRange(datetime(2020, 2, 1), None),
                    name="School Streets",
                    authority_id=2,
                    type_=SchemeType.CONSTRUCTION,
                ),
            ],
        )

        schemes.add(scheme)

        row1: CapitalSchemeOverviewEntity
        row2: CapitalSchemeOverviewEntity
        with session_maker() as session:
            row1, row2 = session.scalars(
                select(CapitalSchemeOverviewEntity).order_by(CapitalSchemeOverviewEntity.capital_scheme_overview_id)
            )

        assert (
            row1.capital_scheme_overview_id == 2
            and row1.capital_scheme_id == 1
            and row1.effective_date_from == datetime(2020, 1, 1)
            and row1.effective_date_to == datetime(2020, 2, 1)
            and row1.scheme_name == "Wirral Package"
            and row1.bid_submitting_authority_id == 1
            and row1.scheme_type_id == 1
        )
        assert (
            row2.capital_scheme_overview_id == 3
            and row2.capital_scheme_id == 1
            and row2.effective_date_from == datetime(2020, 2, 1)
            and row2.effective_date_to is None
            and row2.scheme_name == "School Streets"
            and row2.bid_submitting_authority_id == 2
            and row2.scheme_type_id == 2
        )

    def test_add_schemes_bid_status_revisions(
        self, schemes: DatabaseSchemeRepository, session_maker: sessionmaker[Session]
    ) -> None:
        scheme = build_scheme(
            id_=1,
            name="Wirral Package",
            authority_id=1,
            bid_status_revisions=[
                BidStatusRevision(
                    id_=2, effective=DateRange(datetime(2020, 1, 1), datetime(2020, 2, 1)), status=BidStatus.SUBMITTED
                ),
                BidStatusRevision(id_=3, effective=DateRange(datetime(2020, 2, 1), None), status=BidStatus.FUNDED),
            ],
        )

        schemes.add(scheme)

        row1: CapitalSchemeBidStatusEntity
        row2: CapitalSchemeBidStatusEntity
        with session_maker() as session:
            row1, row2 = session.scalars(
                select(CapitalSchemeBidStatusEntity).order_by(CapitalSchemeBidStatusEntity.capital_scheme_bid_status_id)
            )
        assert (
            row1.capital_scheme_bid_status_id == 2
            and row1.capital_scheme_id == 1
            and row1.effective_date_from == datetime(2020, 1, 1)
            and row1.effective_date_to == datetime(2020, 2, 1)
            and row1.bid_status_id == 1
        )
        assert (
            row2.capital_scheme_bid_status_id == 3
            and row2.capital_scheme_id == 1
            and row2.effective_date_from == datetime(2020, 2, 1)
            and row2.effective_date_to is None
            and row2.bid_status_id == 2
        )

    def test_add_schemes_financial_revisions(
        self, schemes: DatabaseSchemeRepository, session_maker: sessionmaker[Session]
    ) -> None:
        scheme = build_scheme(id_=1, name="Wirral Package", authority_id=1)
        scheme.funding.update_financials(
            FinancialRevision(
                id_=2,
                effective=DateRange(datetime(2020, 1, 1), datetime(2020, 2, 1)),
                type_=FinancialType.FUNDING_ALLOCATION,
                amount=100_000,
                source=DataSource.ATF4_BID,
            ),
            FinancialRevision(
                id_=3,
                effective=DateRange(datetime(2020, 2, 1), None),
                type_=FinancialType.FUNDING_ALLOCATION,
                amount=200_000,
                source=DataSource.ATF4_BID,
            ),
        )

        schemes.add(scheme)

        row1: CapitalSchemeFinancialEntity
        row2: CapitalSchemeFinancialEntity
        with session_maker() as session:
            row1, row2 = session.scalars(
                select(CapitalSchemeFinancialEntity).order_by(CapitalSchemeFinancialEntity.capital_scheme_financial_id)
            )
        assert (
            row1.capital_scheme_financial_id == 2
            and row1.capital_scheme_id == 1
            and row1.effective_date_from == datetime(2020, 1, 1)
            and row1.effective_date_to == datetime(2020, 2, 1)
            and row1.financial_type_id == 3
            and row1.amount == 100_000
            and row1.data_source_id == 3
        )
        assert (
            row2.capital_scheme_financial_id == 3
            and row2.capital_scheme_id == 1
            and row2.effective_date_from == datetime(2020, 2, 1)
            and row2.effective_date_to is None
            and row2.financial_type_id == 3
            and row2.amount == 200_000
            and row2.data_source_id == 3
        )

    def test_add_schemes_milestone_revisions(
        self, schemes: DatabaseSchemeRepository, session_maker: sessionmaker[Session]
    ) -> None:
        scheme = build_scheme(id_=1, name="Wirral Package", authority_id=1)
        scheme.milestones.update_milestones(
            MilestoneRevision(
                id_=2,
                effective=DateRange(datetime(2020, 1, 1), datetime(2020, 2, 1)),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.PLANNED,
                status_date=date(2020, 2, 1),
                source=DataSource.ATF4_BID,
            ),
            MilestoneRevision(
                id_=3,
                effective=DateRange(datetime(2020, 2, 1), None),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.PLANNED,
                status_date=date(2020, 3, 1),
                source=DataSource.ATF4_BID,
            ),
        )

        schemes.add(scheme)

        row1: CapitalSchemeMilestoneEntity
        row2: CapitalSchemeMilestoneEntity
        with session_maker() as session:
            row1, row2 = session.scalars(
                select(CapitalSchemeMilestoneEntity).order_by(CapitalSchemeMilestoneEntity.capital_scheme_milestone_id)
            )
        assert (
            row1.capital_scheme_milestone_id == 2
            and row1.capital_scheme_id == 1
            and row1.effective_date_from == datetime(2020, 1, 1)
            and row1.effective_date_to == datetime(2020, 2, 1)
            and row1.milestone_id == 6
            and row1.observation_type_id == 1
            and row1.status_date == date(2020, 2, 1)
            and row1.data_source_id == 3
        )
        assert (
            row2.capital_scheme_milestone_id == 3
            and row2.capital_scheme_id == 1
            and row2.effective_date_from == datetime(2020, 2, 1)
            and row2.effective_date_to is None
            and row2.milestone_id == 6
            and row2.observation_type_id == 1
            and row2.status_date == date(2020, 3, 1)
            and row2.data_source_id == 3
        )

    def test_add_schemes_output_revisions(
        self, schemes: DatabaseSchemeRepository, session_maker: sessionmaker[Session]
    ) -> None:
        scheme = build_scheme(id_=1, name="Wirral Package", authority_id=1)
        scheme.outputs.update_outputs(
            OutputRevision(
                id_=3,
                effective=DateRange(datetime(2020, 1, 1), datetime(2020, 2, 1)),
                type_measure=OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES,
                value=Decimal(10),
                observation_type=ObservationType.PLANNED,
            ),
            OutputRevision(
                id_=4,
                effective=DateRange(datetime(2020, 2, 1), None),
                type_measure=OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES,
                value=Decimal(20),
                observation_type=ObservationType.PLANNED,
            ),
        )

        schemes.add(scheme)

        row1: CapitalSchemeInterventionEntity
        row2: CapitalSchemeInterventionEntity
        with session_maker() as session:
            row1, row2 = session.scalars(
                select(CapitalSchemeInterventionEntity).order_by(
                    CapitalSchemeInterventionEntity.capital_scheme_intervention_id
                )
            )
        assert (
            row1.capital_scheme_intervention_id == 3
            and row1.capital_scheme_id == 1
            and row1.effective_date_from == datetime(2020, 1, 1)
            and row1.effective_date_to == datetime(2020, 2, 1)
            and row1.intervention_type_measure_id == 4
            and row1.intervention_value == Decimal(10)
            and row1.observation_type_id == 1
        )
        assert (
            row2.capital_scheme_intervention_id == 4
            and row2.capital_scheme_id == 1
            and row2.effective_date_from == datetime(2020, 2, 1)
            and row2.effective_date_to is None
            and row2.intervention_type_measure_id == 4
            and row2.intervention_value == Decimal(20)
            and row2.observation_type_id == 1
        )

    def test_add_schemes_authority_reviews(
        self, schemes: DatabaseSchemeRepository, session_maker: sessionmaker[Session]
    ) -> None:
        scheme = build_scheme(id_=1, name="Wirral Package", authority_id=1)
        scheme.reviews.update_authority_reviews(
            AuthorityReview(id_=2, review_date=datetime(2020, 1, 1), source=DataSource.ATF4_BID),
            AuthorityReview(id_=3, review_date=datetime(2020, 2, 1), source=DataSource.PULSE_6),
        )

        schemes.add(scheme)

        row1: CapitalSchemeAuthorityReviewEntity
        row2: CapitalSchemeAuthorityReviewEntity
        with session_maker() as session:
            row1, row2 = session.scalars(
                select(CapitalSchemeAuthorityReviewEntity).order_by(
                    CapitalSchemeAuthorityReviewEntity.capital_scheme_authority_review_id
                )
            )
        assert (
            row1.capital_scheme_authority_review_id == 2
            and row1.capital_scheme_id == 1
            and row1.review_date == datetime(2020, 1, 1)
            and row1.data_source_id == 3
        )
        assert (
            row2.capital_scheme_authority_review_id == 3
            and row2.capital_scheme_id == 1
            and row2.review_date == datetime(2020, 2, 1)
            and row2.data_source_id == 2
        )

    def test_get_scheme(self, schemes: DatabaseSchemeRepository, session_maker: sessionmaker[Session]) -> None:
        with session_maker() as session:
            session.add(CapitalSchemeEntity(capital_scheme_id=1, funding_programme_id=2))
            session.commit()

        scheme = schemes.get(1)

        assert scheme and scheme.id == 1 and scheme.funding_programme == FundingProgrammes.ATF3

    def test_get_scheme_overview_revisions(
        self, schemes: DatabaseSchemeRepository, session_maker: sessionmaker[Session]
    ) -> None:
        with session_maker() as session:
            session.add_all(
                [
                    CapitalSchemeEntity(capital_scheme_id=1, funding_programme_id=3),
                    CapitalSchemeOverviewEntity(
                        capital_scheme_overview_id=2,
                        capital_scheme_id=1,
                        effective_date_from=datetime(2020, 1, 1),
                        effective_date_to=datetime(2020, 2, 1),
                        scheme_name="Wirral Package",
                        bid_submitting_authority_id=1,
                        scheme_type_id=1,
                    ),
                    CapitalSchemeOverviewEntity(
                        capital_scheme_overview_id=3,
                        capital_scheme_id=1,
                        effective_date_from=datetime(2020, 2, 1),
                        effective_date_to=None,
                        scheme_name="School Streets",
                        bid_submitting_authority_id=2,
                        scheme_type_id=2,
                    ),
                ]
            )
            session.commit()

        scheme = schemes.get(1)

        assert scheme
        overview_revision1: OverviewRevision
        overview_revision2: OverviewRevision
        overview_revision1, overview_revision2 = scheme.overview.overview_revisions
        assert (
            overview_revision1.id == 2
            and overview_revision1.effective == DateRange(datetime(2020, 1, 1), datetime(2020, 2, 1))
            and overview_revision1.name == "Wirral Package"
            and overview_revision1.authority_id == 1
            and overview_revision1.type == SchemeType.DEVELOPMENT
        )
        assert (
            overview_revision2.id == 3
            and overview_revision2.effective == DateRange(datetime(2020, 2, 1), None)
            and overview_revision2.name == "School Streets"
            and overview_revision2.authority_id == 2
            and overview_revision2.type == SchemeType.CONSTRUCTION
        )

    def test_get_scheme_bid_status_revisions(
        self, schemes: DatabaseSchemeRepository, session_maker: sessionmaker[Session]
    ) -> None:
        with session_maker() as session:
            session.add_all(
                [
                    CapitalSchemeEntity(capital_scheme_id=1, funding_programme_id=3),
                    CapitalSchemeBidStatusEntity(
                        capital_scheme_bid_status_id=2,
                        capital_scheme_id=1,
                        effective_date_from=datetime(2020, 1, 1),
                        effective_date_to=datetime(2020, 2, 1),
                        bid_status_id=1,
                    ),
                    CapitalSchemeBidStatusEntity(
                        capital_scheme_bid_status_id=3,
                        capital_scheme_id=1,
                        effective_date_from=datetime(2020, 2, 1),
                        effective_date_to=None,
                        bid_status_id=2,
                    ),
                ]
            )
            session.commit()

        scheme = schemes.get(1)

        assert scheme
        bid_status_revision1: BidStatusRevision
        bid_status_revision2: BidStatusRevision
        bid_status_revision1, bid_status_revision2 = scheme.funding.bid_status_revisions
        assert (
            bid_status_revision1.id == 2
            and bid_status_revision1.effective == DateRange(datetime(2020, 1, 1), datetime(2020, 2, 1))
            and bid_status_revision1.status == BidStatus.SUBMITTED
        )
        assert (
            bid_status_revision2.id == 3
            and bid_status_revision2.effective == DateRange(datetime(2020, 2, 1), None)
            and bid_status_revision2.status == BidStatus.FUNDED
        )

    def test_get_scheme_financial_revisions(
        self, schemes: DatabaseSchemeRepository, session_maker: sessionmaker[Session]
    ) -> None:
        with session_maker() as session:
            session.add_all(
                [
                    CapitalSchemeEntity(capital_scheme_id=1, funding_programme_id=3),
                    CapitalSchemeFinancialEntity(
                        capital_scheme_financial_id=2,
                        capital_scheme_id=1,
                        effective_date_from=datetime(2020, 1, 1),
                        effective_date_to=datetime(2020, 2, 1),
                        financial_type_id=3,
                        amount=100_000,
                        data_source_id=3,
                    ),
                    CapitalSchemeFinancialEntity(
                        capital_scheme_financial_id=3,
                        capital_scheme_id=1,
                        effective_date_from=datetime(2020, 2, 1),
                        effective_date_to=None,
                        financial_type_id=3,
                        amount=200_000,
                        data_source_id=3,
                    ),
                ]
            )
            session.commit()

        scheme = schemes.get(1)

        assert scheme
        financial_revision1: FinancialRevision
        financial_revision2: FinancialRevision
        financial_revision1, financial_revision2 = scheme.funding.financial_revisions
        assert (
            financial_revision1.id == 2
            and financial_revision1.effective == DateRange(datetime(2020, 1, 1), datetime(2020, 2, 1))
            and financial_revision1.type == FinancialType.FUNDING_ALLOCATION
            and financial_revision1.amount == 100_000
            and financial_revision1.source == DataSource.ATF4_BID
        )
        assert (
            financial_revision2.id == 3
            and financial_revision2.effective == DateRange(datetime(2020, 2, 1), None)
            and financial_revision2.type == FinancialType.FUNDING_ALLOCATION
            and financial_revision2.amount == 200_000
            and financial_revision2.source == DataSource.ATF4_BID
        )

    def test_get_scheme_milestone_revisions(
        self, schemes: DatabaseSchemeRepository, session_maker: sessionmaker[Session]
    ) -> None:
        with session_maker() as session:
            session.add_all(
                [
                    CapitalSchemeEntity(capital_scheme_id=1, funding_programme_id=3),
                    CapitalSchemeMilestoneEntity(
                        capital_scheme_milestone_id=2,
                        capital_scheme_id=1,
                        effective_date_from=datetime(2020, 1, 1),
                        effective_date_to=datetime(2020, 2, 1),
                        milestone_id=6,
                        observation_type_id=1,
                        status_date=date(2020, 2, 1),
                        data_source_id=3,
                    ),
                    CapitalSchemeMilestoneEntity(
                        capital_scheme_milestone_id=3,
                        capital_scheme_id=1,
                        effective_date_from=datetime(2020, 2, 1),
                        effective_date_to=None,
                        milestone_id=6,
                        observation_type_id=1,
                        status_date=date(2020, 3, 1),
                        data_source_id=3,
                    ),
                ]
            )
            session.commit()

        scheme = schemes.get(1)

        assert scheme
        milestone_revision1: MilestoneRevision
        milestone_revision2: MilestoneRevision
        milestone_revision1, milestone_revision2 = scheme.milestones.milestone_revisions
        assert (
            milestone_revision1.id == 2
            and milestone_revision1.effective == DateRange(datetime(2020, 1, 1), datetime(2020, 2, 1))
            and milestone_revision1.milestone == Milestone.DETAILED_DESIGN_COMPLETED
            and milestone_revision1.observation_type == ObservationType.PLANNED
            and milestone_revision1.status_date == date(2020, 2, 1)
            and milestone_revision1.source == DataSource.ATF4_BID
        )
        assert (
            milestone_revision2.id == 3
            and milestone_revision2.effective == DateRange(datetime(2020, 2, 1), None)
            and milestone_revision2.milestone == Milestone.DETAILED_DESIGN_COMPLETED
            and milestone_revision2.observation_type == ObservationType.PLANNED
            and milestone_revision2.status_date == date(2020, 3, 1)
            and milestone_revision2.source == DataSource.ATF4_BID
        )

    def test_get_scheme_output_revisions(
        self, schemes: DatabaseSchemeRepository, session_maker: sessionmaker[Session]
    ) -> None:
        with session_maker() as session:
            session.add_all(
                [
                    CapitalSchemeEntity(capital_scheme_id=1, funding_programme_id=3),
                    CapitalSchemeInterventionEntity(
                        capital_scheme_intervention_id=2,
                        capital_scheme_id=1,
                        effective_date_from=datetime(2020, 1, 1),
                        effective_date_to=datetime(2020, 2, 1),
                        intervention_type_measure_id=4,
                        intervention_value=Decimal(10),
                        observation_type_id=1,
                    ),
                    CapitalSchemeInterventionEntity(
                        capital_scheme_intervention_id=3,
                        capital_scheme_id=1,
                        effective_date_from=datetime(2020, 2, 1),
                        effective_date_to=None,
                        intervention_type_measure_id=4,
                        intervention_value=Decimal(20),
                        observation_type_id=1,
                    ),
                ]
            )
            session.commit()

        scheme = schemes.get(1)

        assert scheme
        output_revision1: OutputRevision
        output_revision2: OutputRevision
        output_revision1, output_revision2 = scheme.outputs.output_revisions
        assert (
            output_revision1.id == 2
            and output_revision1.effective == DateRange(datetime(2020, 1, 1), datetime(2020, 2, 1))
            and output_revision1.type_measure == OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES
            and output_revision1.value == Decimal(10)
            and output_revision1.observation_type == ObservationType.PLANNED
        )
        assert (
            output_revision2.id == 3
            and output_revision2.effective == DateRange(datetime(2020, 2, 1), None)
            and output_revision2.type_measure == OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES
            and output_revision2.value == Decimal(20)
            and output_revision2.observation_type == ObservationType.PLANNED
        )

    def test_get_scheme_authority_reviews(
        self, schemes: DatabaseSchemeRepository, session_maker: sessionmaker[Session]
    ) -> None:
        with session_maker() as session:
            session.add_all(
                [
                    CapitalSchemeEntity(capital_scheme_id=1, funding_programme_id=3),
                    CapitalSchemeAuthorityReviewEntity(
                        capital_scheme_authority_review_id=2,
                        capital_scheme_id=1,
                        review_date=datetime(2020, 1, 1),
                        data_source_id=3,
                    ),
                    CapitalSchemeAuthorityReviewEntity(
                        capital_scheme_authority_review_id=3,
                        capital_scheme_id=1,
                        review_date=datetime(2020, 2, 1),
                        data_source_id=2,
                    ),
                ]
            )
            session.commit()

        scheme = schemes.get(1)

        assert scheme
        authority_review1: AuthorityReview
        authority_review2: AuthorityReview
        authority_review1, authority_review2 = scheme.reviews.authority_reviews
        assert (
            authority_review1.id == 2
            and authority_review1.review_date == datetime(2020, 1, 1)
            and authority_review1.source == DataSource.ATF4_BID
        )
        assert (
            authority_review2.id == 3
            and authority_review2.review_date == datetime(2020, 2, 1)
            and authority_review2.source == DataSource.PULSE_6
        )

    def test_get_scheme_that_does_not_exist(
        self, schemes: DatabaseSchemeRepository, session_maker: sessionmaker[Session]
    ) -> None:
        with session_maker() as session:
            session.add(CapitalSchemeEntity(capital_scheme_id=1, funding_programme_id=3))
            session.commit()

        assert schemes.get(2) is None

    def test_get_all_schemes_by_authority(
        self, schemes: DatabaseSchemeRepository, session_maker: sessionmaker[Session]
    ) -> None:
        with session_maker() as session:
            session.add_all(
                [
                    CapitalSchemeEntity(capital_scheme_id=1, funding_programme_id=2),
                    CapitalSchemeOverviewEntity(
                        capital_scheme_overview_id=4,
                        capital_scheme_id=1,
                        effective_date_from=datetime(2020, 1, 1),
                        effective_date_to=None,
                        scheme_name="Wirral Package",
                        bid_submitting_authority_id=1,
                        scheme_type_id=2,
                    ),
                    CapitalSchemeEntity(capital_scheme_id=2, funding_programme_id=3),
                    CapitalSchemeOverviewEntity(
                        capital_scheme_overview_id=5,
                        capital_scheme_id=2,
                        effective_date_from=datetime(2020, 1, 1),
                        effective_date_to=None,
                        scheme_name="School Streets",
                        bid_submitting_authority_id=1,
                        scheme_type_id=2,
                    ),
                    CapitalSchemeEntity(capital_scheme_id=3, funding_programme_id=3),
                    CapitalSchemeOverviewEntity(
                        capital_scheme_overview_id=6,
                        capital_scheme_id=3,
                        effective_date_from=datetime(2020, 1, 1),
                        effective_date_to=None,
                        scheme_name="Hospital Fields Road",
                        bid_submitting_authority_id=2,
                        scheme_type_id=2,
                    ),
                ]
            )
            session.commit()

        scheme1: Scheme
        scheme2: Scheme
        scheme1, scheme2 = schemes.get_by_authority(1)

        assert scheme1.id == 1 and scheme1.funding_programme == FundingProgrammes.ATF3
        assert scheme2.id == 2

    def test_get_all_schemes_overview_revisions_by_authority(
        self, schemes: DatabaseSchemeRepository, session_maker: sessionmaker[Session]
    ) -> None:
        with session_maker() as session:
            session.add_all(
                [
                    CapitalSchemeEntity(capital_scheme_id=1, funding_programme_id=3),
                    CapitalSchemeOverviewEntity(
                        capital_scheme_overview_id=3,
                        capital_scheme_id=1,
                        effective_date_from=datetime(2020, 1, 1),
                        effective_date_to=None,
                        scheme_name="Wirral Package",
                        bid_submitting_authority_id=1,
                        scheme_type_id=1,
                    ),
                    CapitalSchemeEntity(capital_scheme_id=2, funding_programme_id=3),
                    CapitalSchemeOverviewEntity(
                        capital_scheme_overview_id=4,
                        capital_scheme_id=2,
                        effective_date_from=datetime(2020, 2, 1),
                        effective_date_to=None,
                        scheme_name="School Streets",
                        bid_submitting_authority_id=2,
                        scheme_type_id=2,
                    ),
                ]
            )
            session.commit()

        scheme1: Scheme
        (scheme1,) = schemes.get_by_authority(1)

        assert scheme1.id == 1
        overview_revision1: OverviewRevision
        (overview_revision1,) = scheme1.overview.overview_revisions
        assert (
            overview_revision1.id == 3
            and overview_revision1.effective == DateRange(datetime(2020, 1, 1), None)
            and overview_revision1.name == "Wirral Package"
            and overview_revision1.authority_id == 1
            and overview_revision1.type == SchemeType.DEVELOPMENT
        )

    def test_get_all_schemes_bid_status_revisions_by_authority(
        self, schemes: DatabaseSchemeRepository, session_maker: sessionmaker[Session]
    ) -> None:
        with session_maker() as session:
            session.add_all(
                [
                    CapitalSchemeEntity(capital_scheme_id=1, funding_programme_id=3),
                    CapitalSchemeOverviewEntity(
                        capital_scheme_overview_id=3,
                        capital_scheme_id=1,
                        effective_date_from=datetime(2020, 1, 1),
                        effective_date_to=None,
                        scheme_name="Wirral Package",
                        bid_submitting_authority_id=1,
                        scheme_type_id=2,
                    ),
                    CapitalSchemeBidStatusEntity(
                        capital_scheme_bid_status_id=5,
                        capital_scheme_id=1,
                        effective_date_from=datetime(2020, 1, 1),
                        effective_date_to=None,
                        bid_status_id=2,
                    ),
                    CapitalSchemeEntity(capital_scheme_id=2, funding_programme_id=3),
                    CapitalSchemeOverviewEntity(
                        capital_scheme_overview_id=4,
                        capital_scheme_id=2,
                        effective_date_from=datetime(2020, 1, 1),
                        effective_date_to=None,
                        scheme_name="School Streets",
                        bid_submitting_authority_id=2,
                        scheme_type_id=2,
                    ),
                    CapitalSchemeBidStatusEntity(
                        capital_scheme_bid_status_id=6,
                        capital_scheme_id=2,
                        effective_date_from=datetime(2020, 2, 1),
                        effective_date_to=None,
                        bid_status_id=2,
                    ),
                ]
            )
            session.commit()

        scheme1: Scheme
        (scheme1,) = schemes.get_by_authority(1)

        assert scheme1.id == 1
        bid_status_revision1: BidStatusRevision
        (bid_status_revision1,) = scheme1.funding.bid_status_revisions
        assert (
            bid_status_revision1.id == 5
            and bid_status_revision1.effective == DateRange(datetime(2020, 1, 1), None)
            and bid_status_revision1.status == BidStatus.FUNDED
        )

    def test_get_all_schemes_financial_revisions_by_authority(
        self, schemes: DatabaseSchemeRepository, session_maker: sessionmaker[Session]
    ) -> None:
        with session_maker() as session:
            session.add_all(
                [
                    CapitalSchemeEntity(capital_scheme_id=1, funding_programme_id=3),
                    CapitalSchemeOverviewEntity(
                        capital_scheme_overview_id=3,
                        capital_scheme_id=1,
                        effective_date_from=datetime(2020, 1, 1),
                        effective_date_to=None,
                        scheme_name="Wirral Package",
                        bid_submitting_authority_id=1,
                        scheme_type_id=2,
                    ),
                    CapitalSchemeFinancialEntity(
                        capital_scheme_financial_id=5,
                        capital_scheme_id=1,
                        effective_date_from=datetime(2020, 1, 1),
                        effective_date_to=None,
                        financial_type_id=3,
                        amount=100_000,
                        data_source_id=3,
                    ),
                    CapitalSchemeEntity(capital_scheme_id=2, funding_programme_id=3),
                    CapitalSchemeOverviewEntity(
                        capital_scheme_overview_id=4,
                        capital_scheme_id=2,
                        effective_date_from=datetime(2020, 1, 1),
                        effective_date_to=None,
                        scheme_name="School Streets",
                        bid_submitting_authority_id=2,
                        scheme_type_id=2,
                    ),
                    CapitalSchemeFinancialEntity(
                        capital_scheme_financial_id=6,
                        capital_scheme_id=2,
                        effective_date_from=datetime(2020, 2, 1),
                        effective_date_to=None,
                        financial_type_id=3,
                        amount=200_000,
                        data_source_id=3,
                    ),
                ]
            )
            session.commit()

        scheme1: Scheme
        (scheme1,) = schemes.get_by_authority(1)

        assert scheme1.id == 1
        financial_revision1: FinancialRevision
        (financial_revision1,) = scheme1.funding.financial_revisions
        assert (
            financial_revision1.id == 5
            and financial_revision1.effective == DateRange(datetime(2020, 1, 1), None)
            and financial_revision1.type == FinancialType.FUNDING_ALLOCATION
            and financial_revision1.amount == 100_000
            and financial_revision1.source == DataSource.ATF4_BID
        )

    def test_get_all_schemes_milestone_revisions_by_authority(
        self, schemes: DatabaseSchemeRepository, session_maker: sessionmaker[Session]
    ) -> None:
        with session_maker() as session:
            session.add_all(
                [
                    CapitalSchemeEntity(capital_scheme_id=1, funding_programme_id=3),
                    CapitalSchemeOverviewEntity(
                        capital_scheme_overview_id=4,
                        capital_scheme_id=1,
                        effective_date_from=datetime(2020, 1, 1),
                        effective_date_to=None,
                        scheme_name="Wirral Package",
                        bid_submitting_authority_id=1,
                        scheme_type_id=2,
                    ),
                    CapitalSchemeMilestoneEntity(
                        capital_scheme_milestone_id=7,
                        capital_scheme_id=1,
                        effective_date_from=datetime(2020, 1, 1),
                        effective_date_to=None,
                        milestone_id=6,
                        observation_type_id=1,
                        status_date=date(2020, 2, 1),
                        data_source_id=3,
                    ),
                    CapitalSchemeEntity(capital_scheme_id=2, funding_programme_id=3),
                    CapitalSchemeOverviewEntity(
                        capital_scheme_overview_id=5,
                        capital_scheme_id=2,
                        effective_date_from=datetime(2020, 1, 1),
                        effective_date_to=None,
                        scheme_name="School Streets",
                        bid_submitting_authority_id=1,
                        scheme_type_id=2,
                    ),
                    CapitalSchemeMilestoneEntity(
                        capital_scheme_milestone_id=8,
                        capital_scheme_id=2,
                        effective_date_from=datetime(2020, 2, 1),
                        effective_date_to=None,
                        milestone_id=6,
                        observation_type_id=1,
                        status_date=date(2020, 3, 1),
                        data_source_id=3,
                    ),
                    CapitalSchemeEntity(capital_scheme_id=3, funding_programme_id=3),
                    CapitalSchemeOverviewEntity(
                        capital_scheme_overview_id=6,
                        capital_scheme_id=3,
                        effective_date_from=datetime(2020, 1, 1),
                        effective_date_to=None,
                        scheme_name="Hospital Fields Road",
                        bid_submitting_authority_id=2,
                        scheme_type_id=2,
                    ),
                    CapitalSchemeMilestoneEntity(
                        capital_scheme_milestone_id=9,
                        capital_scheme_id=3,
                        effective_date_from=datetime(2020, 3, 1),
                        effective_date_to=None,
                        milestone_id=6,
                        observation_type_id=1,
                        status_date=date(2020, 4, 1),
                        data_source_id=3,
                    ),
                ]
            )
            session.commit()

        scheme1: Scheme
        scheme2: Scheme
        scheme1, scheme2 = schemes.get_by_authority(1)

        assert scheme1.id == 1
        milestone_revision1: MilestoneRevision
        (milestone_revision1,) = scheme1.milestones.milestone_revisions
        assert (
            milestone_revision1.id == 7
            and milestone_revision1.effective == DateRange(datetime(2020, 1, 1), None)
            and milestone_revision1.milestone == Milestone.DETAILED_DESIGN_COMPLETED
            and milestone_revision1.observation_type == ObservationType.PLANNED
            and milestone_revision1.status_date == date(2020, 2, 1)
            and milestone_revision1.source == DataSource.ATF4_BID
        )
        assert scheme2.id == 2
        milestone_revision2: MilestoneRevision
        (milestone_revision2,) = scheme2.milestones.milestone_revisions
        assert (
            milestone_revision2.id == 8
            and milestone_revision2.effective == DateRange(datetime(2020, 2, 1), None)
            and milestone_revision2.milestone == Milestone.DETAILED_DESIGN_COMPLETED
            and milestone_revision2.observation_type == ObservationType.PLANNED
            and milestone_revision2.status_date == date(2020, 3, 1)
            and milestone_revision2.source == DataSource.ATF4_BID
        )

    def test_get_all_schemes_output_revisions_by_authority(
        self, schemes: DatabaseSchemeRepository, session_maker: sessionmaker[Session]
    ) -> None:
        with session_maker() as session:
            session.add_all(
                [
                    CapitalSchemeEntity(capital_scheme_id=1, funding_programme_id=3),
                    CapitalSchemeOverviewEntity(
                        capital_scheme_overview_id=4,
                        capital_scheme_id=1,
                        effective_date_from=datetime(2020, 1, 1),
                        effective_date_to=None,
                        scheme_name="Wirral Package",
                        bid_submitting_authority_id=1,
                        scheme_type_id=2,
                    ),
                    CapitalSchemeInterventionEntity(
                        capital_scheme_intervention_id=7,
                        capital_scheme_id=1,
                        effective_date_from=datetime(2020, 1, 1),
                        effective_date_to=None,
                        intervention_type_measure_id=4,
                        intervention_value=Decimal(10),
                        observation_type_id=1,
                    ),
                    CapitalSchemeEntity(capital_scheme_id=2, funding_programme_id=3),
                    CapitalSchemeOverviewEntity(
                        capital_scheme_overview_id=5,
                        capital_scheme_id=2,
                        effective_date_from=datetime(2020, 1, 1),
                        effective_date_to=None,
                        scheme_name="School Streets",
                        bid_submitting_authority_id=1,
                        scheme_type_id=2,
                    ),
                    CapitalSchemeInterventionEntity(
                        capital_scheme_intervention_id=8,
                        capital_scheme_id=2,
                        effective_date_from=datetime(2020, 2, 1),
                        effective_date_to=None,
                        intervention_type_measure_id=4,
                        intervention_value=Decimal(20),
                        observation_type_id=1,
                    ),
                    CapitalSchemeEntity(capital_scheme_id=3, funding_programme_id=3),
                    CapitalSchemeOverviewEntity(
                        capital_scheme_overview_id=6,
                        capital_scheme_id=3,
                        effective_date_from=datetime(2020, 1, 1),
                        effective_date_to=None,
                        scheme_name="Hospital Fields Road",
                        bid_submitting_authority_id=2,
                        scheme_type_id=2,
                    ),
                    CapitalSchemeInterventionEntity(
                        capital_scheme_intervention_id=9,
                        capital_scheme_id=3,
                        effective_date_from=datetime(2020, 3, 1),
                        effective_date_to=None,
                        intervention_type_measure_id=4,
                        intervention_value=Decimal(30),
                        observation_type_id=1,
                    ),
                ]
            )
            session.commit()

        scheme1: Scheme
        scheme2: Scheme
        scheme1, scheme2 = schemes.get_by_authority(1)

        assert scheme1.id == 1
        output_revision1: OutputRevision
        (output_revision1,) = scheme1.outputs.output_revisions
        assert (
            output_revision1.id == 7
            and output_revision1.effective == DateRange(datetime(2020, 1, 1), None)
            and output_revision1.type_measure == OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES
            and output_revision1.value == Decimal(10)
            and output_revision1.observation_type == ObservationType.PLANNED
        )
        assert scheme2.id == 2
        output_revision2: OutputRevision
        (output_revision2,) = scheme2.outputs.output_revisions
        assert (
            output_revision2.id == 8
            and output_revision2.effective == DateRange(datetime(2020, 2, 1), None)
            and output_revision2.type_measure == OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES
            and output_revision2.value == Decimal(20)
            and output_revision2.observation_type == ObservationType.PLANNED
        )

    def test_get_all_schemes_authority_reviews_by_authority(
        self, schemes: DatabaseSchemeRepository, session_maker: sessionmaker[Session]
    ) -> None:
        with session_maker() as session:
            session.add_all(
                [
                    CapitalSchemeEntity(capital_scheme_id=1, funding_programme_id=3),
                    CapitalSchemeOverviewEntity(
                        capital_scheme_overview_id=3,
                        capital_scheme_id=1,
                        effective_date_from=datetime(2020, 1, 1),
                        effective_date_to=None,
                        scheme_name="Wirral Package",
                        bid_submitting_authority_id=1,
                        scheme_type_id=2,
                    ),
                    CapitalSchemeAuthorityReviewEntity(
                        capital_scheme_authority_review_id=5,
                        capital_scheme_id=1,
                        review_date=datetime(2020, 1, 1),
                        data_source_id=3,
                    ),
                    CapitalSchemeEntity(capital_scheme_id=2, funding_programme_id=3),
                    CapitalSchemeOverviewEntity(
                        capital_scheme_overview_id=4,
                        capital_scheme_id=2,
                        effective_date_from=datetime(2020, 1, 1),
                        effective_date_to=None,
                        scheme_name="School Streets",
                        bid_submitting_authority_id=2,
                        scheme_type_id=2,
                    ),
                    CapitalSchemeAuthorityReviewEntity(
                        capital_scheme_authority_review_id=6,
                        capital_scheme_id=2,
                        review_date=datetime(2020, 2, 1),
                        data_source_id=2,
                    ),
                ]
            )
            session.commit()

        scheme1: Scheme
        (scheme1,) = schemes.get_by_authority(1)

        assert scheme1.id == 1
        authority_review1: AuthorityReview
        (authority_review1,) = scheme1.reviews.authority_reviews
        assert (
            authority_review1.id == 5
            and authority_review1.review_date == datetime(2020, 1, 1)
            and authority_review1.source == DataSource.ATF4_BID
        )

    def test_clear_all_schemes(self, schemes: DatabaseSchemeRepository, session_maker: sessionmaker[Session]) -> None:
        with session_maker() as session:
            session.add_all(
                [
                    CapitalSchemeEntity(capital_scheme_id=1, funding_programme_id=3),
                    CapitalSchemeOverviewEntity(
                        capital_scheme_id=1,
                        effective_date_from=datetime(2020, 1, 1),
                        effective_date_to=None,
                        scheme_name="Wirral Package",
                        bid_submitting_authority_id=1,
                        scheme_type_id=2,
                    ),
                    CapitalSchemeBidStatusEntity(
                        capital_scheme_id=1,
                        effective_date_from=datetime(2020, 1, 1),
                        effective_date_to=None,
                        bid_status_id=2,
                    ),
                    CapitalSchemeFinancialEntity(
                        capital_scheme_id=1,
                        effective_date_from=datetime(2020, 1, 1),
                        effective_date_to=None,
                        financial_type_id=3,
                        amount=100_000,
                        data_source_id=3,
                    ),
                    CapitalSchemeMilestoneEntity(
                        capital_scheme_id=1,
                        effective_date_from=datetime(2020, 1, 1),
                        effective_date_to=None,
                        milestone_id=5,
                        observation_type_id=1,
                        status_date=date(2020, 2, 1),
                        data_source_id=3,
                    ),
                    CapitalSchemeInterventionEntity(
                        capital_scheme_id=1,
                        effective_date_from=datetime(2020, 1, 1),
                        effective_date_to=None,
                        intervention_type_measure_id=4,
                        intervention_value=Decimal(10),
                        observation_type_id=1,
                    ),
                    CapitalSchemeAuthorityReviewEntity(
                        capital_scheme_id=1, review_date=datetime(2020, 1, 1, 12), data_source_id=3
                    ),
                    CapitalSchemeEntity(capital_scheme_id=2, funding_programme_id=3),
                ]
            )
            session.commit()

        schemes.clear()

        with session_maker() as session:
            assert session.execute(select(func.count()).select_from(CapitalSchemeEntity)).scalar_one() == 0

    def test_update_scheme_financial_revisions(
        self, schemes: DatabaseSchemeRepository, session_maker: sessionmaker[Session]
    ) -> None:
        with session_maker() as session:
            session.add_all(
                [
                    CapitalSchemeEntity(capital_scheme_id=1, funding_programme_id=3),
                    CapitalSchemeFinancialEntity(
                        capital_scheme_financial_id=2,
                        capital_scheme_id=1,
                        effective_date_from=datetime(2020, 1, 1),
                        effective_date_to=None,
                        financial_type_id=4,
                        amount=50_000,
                        data_source_id=3,
                    ),
                ]
            )
            session.commit()
        scheme = schemes.get(1)
        assert scheme
        scheme.funding.financial_revisions[0].effective = DateRange(datetime(2020, 1, 1), datetime(2020, 2, 1))
        scheme.funding.update_financial(
            FinancialRevision(
                id_=3,
                effective=DateRange(datetime(2020, 2, 1), None),
                type_=FinancialType.SPEND_TO_DATE,
                amount=60_000,
                source=DataSource.AUTHORITY_UPDATE,
            )
        )

        schemes.update(scheme)

        with session_maker() as session:
            row = session.get_one(CapitalSchemeEntity, 1)
            capital_scheme_financial1: CapitalSchemeFinancialEntity
            capital_scheme_financial2: CapitalSchemeFinancialEntity
            capital_scheme_financial1, capital_scheme_financial2 = row.capital_scheme_financials
        assert (
            capital_scheme_financial1.capital_scheme_financial_id == 2
            and capital_scheme_financial1.effective_date_to == datetime(2020, 2, 1)
        )
        assert (
            capital_scheme_financial2.capital_scheme_financial_id == 3
            and capital_scheme_financial2.capital_scheme_id == 1
            and capital_scheme_financial2.effective_date_from == datetime(2020, 2, 1)
            and capital_scheme_financial2.effective_date_to is None
            and capital_scheme_financial2.financial_type_id == 4
            and capital_scheme_financial2.amount == 60_000
            and capital_scheme_financial2.data_source_id == 16
        )

    def test_update_scheme_milestone_revisions(
        self, schemes: DatabaseSchemeRepository, session_maker: sessionmaker[Session]
    ) -> None:
        with session_maker() as session:
            session.add_all(
                [
                    CapitalSchemeEntity(capital_scheme_id=1, funding_programme_id=3),
                    CapitalSchemeMilestoneEntity(
                        capital_scheme_milestone_id=2,
                        capital_scheme_id=1,
                        effective_date_from=datetime(2020, 1, 1),
                        effective_date_to=None,
                        milestone_id=6,
                        observation_type_id=1,
                        status_date=date(2020, 2, 1),
                        data_source_id=3,
                    ),
                ]
            )
            session.commit()
        scheme = schemes.get(1)
        assert scheme
        scheme.milestones.milestone_revisions[0].effective = DateRange(datetime(2020, 1, 1), datetime(2020, 2, 1))
        scheme.milestones.update_milestone(
            MilestoneRevision(
                id_=3,
                effective=DateRange(datetime(2020, 2, 1), None),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.PLANNED,
                status_date=date(2020, 3, 1),
                source=DataSource.AUTHORITY_UPDATE,
            ),
        )

        schemes.update(scheme)

        with session_maker() as session:
            row = session.get_one(CapitalSchemeEntity, 1)
            capital_scheme_milestone1: CapitalSchemeMilestoneEntity
            capital_scheme_milestone2: CapitalSchemeMilestoneEntity
            capital_scheme_milestone1, capital_scheme_milestone2 = row.capital_scheme_milestones
        assert (
            capital_scheme_milestone1.capital_scheme_milestone_id == 2
            and capital_scheme_milestone1.effective_date_to == datetime(2020, 2, 1)
        )
        assert (
            capital_scheme_milestone2.capital_scheme_milestone_id == 3
            and capital_scheme_milestone2.capital_scheme_id == 1
            and capital_scheme_milestone2.effective_date_from == datetime(2020, 2, 1)
            and capital_scheme_milestone2.effective_date_to is None
            and capital_scheme_milestone2.milestone_id == 6
            and capital_scheme_milestone2.observation_type_id == 1
            and capital_scheme_milestone2.status_date == date(2020, 3, 1)
            and capital_scheme_milestone2.data_source_id == 16
        )

    def test_update_scheme_authority_reviews(
        self, schemes: DatabaseSchemeRepository, session_maker: sessionmaker[Session]
    ) -> None:
        with session_maker() as session:
            session.add_all(
                [
                    CapitalSchemeEntity(capital_scheme_id=1, funding_programme_id=3),
                    CapitalSchemeAuthorityReviewEntity(
                        capital_scheme_authority_review_id=2,
                        capital_scheme_id=1,
                        review_date=datetime(2020, 1, 1),
                        data_source_id=3,
                    ),
                ]
            )
            session.commit()
        scheme = schemes.get(1)
        assert scheme
        scheme.reviews.update_authority_review(
            AuthorityReview(id_=3, review_date=datetime(2020, 1, 2), source=DataSource.AUTHORITY_UPDATE)
        )

        schemes.update(scheme)

        with session_maker() as session:
            row = session.get_one(CapitalSchemeEntity, 1)
            capital_scheme_authority_review1: CapitalSchemeAuthorityReviewEntity
            capital_scheme_authority_review2: CapitalSchemeAuthorityReviewEntity
            capital_scheme_authority_review1, capital_scheme_authority_review2 = row.capital_scheme_authority_reviews
        assert (
            capital_scheme_authority_review2.capital_scheme_authority_review_id == 3
            and capital_scheme_authority_review2.capital_scheme_id == 1
            and capital_scheme_authority_review2.review_date == datetime(2020, 1, 2)
            and capital_scheme_authority_review2.data_source_id == 16
        )


@pytest.mark.parametrize(
    "funding_programme, id_",
    [
        (FundingProgrammes.ATF2, 1),
        (FundingProgrammes.ATF3, 2),
        (FundingProgrammes.ATF4, 3),
        (FundingProgrammes.ATF4E, 4),
    ],
)
class TestFundingProgrammeMapper:
    def test_to_id(self, funding_programme: FundingProgramme, id_: int) -> None:
        assert FundingProgrammeMapper().to_id(funding_programme) == id_

    def test_to_domain(self, funding_programme: FundingProgramme, id_: int) -> None:
        assert FundingProgrammeMapper().to_domain(id_) == funding_programme
