from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import Engine, func, select
from sqlalchemy.orm import Session

from schemes.domain.authorities import Authority
from schemes.domain.schemes import (
    DataSource,
    DateRange,
    FinancialRevision,
    FinancialType,
    FundingProgramme,
    Milestone,
    MilestoneRevision,
    ObservationType,
    OutputRevision,
    OutputTypeMeasure,
    Scheme,
    SchemeType,
)
from schemes.infrastructure import (
    CapitalSchemeEntity,
    CapitalSchemeFinancialEntity,
    SchemeInterventionEntity,
    SchemeMilestoneEntity,
)
from schemes.infrastructure.authorities import DatabaseAuthorityRepository
from schemes.infrastructure.schemes import DatabaseSchemeRepository
from schemes.infrastructure.schemes.schemes import (
    FundingProgrammeMapper,
    SchemeTypeMapper,
)


class TestDatabaseSchemeRepository:
    @pytest.fixture(name="authorities")
    def authorities_fixture(self, engine: Engine) -> DatabaseAuthorityRepository:
        repository: DatabaseAuthorityRepository = DatabaseAuthorityRepository(engine)
        return repository

    @pytest.fixture(name="schemes")
    def schemes_fixture(self, engine: Engine) -> DatabaseSchemeRepository:
        repository: DatabaseSchemeRepository = DatabaseSchemeRepository(engine)
        return repository

    @pytest.fixture(name="authority", autouse=True)
    def authority_fixture(self, authorities: DatabaseAuthorityRepository) -> None:
        authorities.add(
            Authority(id_=1, name="Liverpool City Region Combined Authority"),
            Authority(id_=2, name="West Yorkshire Combined Authority"),
        )

    def test_add_schemes(self, schemes: DatabaseSchemeRepository, engine: Engine) -> None:
        scheme1 = Scheme(id_=1, name="Wirral Package", authority_id=1)
        scheme1.type = SchemeType.DEVELOPMENT
        scheme1.funding_programme = FundingProgramme.ATF3

        schemes.add(scheme1, Scheme(id_=2, name="School Streets", authority_id=1))

        with Session(engine) as session:
            row1, row2 = session.scalars(select(CapitalSchemeEntity).order_by(CapitalSchemeEntity.capital_scheme_id))
        assert (
            row1.capital_scheme_id == 1
            and row1.scheme_name == "Wirral Package"
            and row1.bid_submitting_authority_id == 1
            and row1.scheme_type_id == 1
            and row1.funding_programme_id == 2
        )
        assert (
            row2.capital_scheme_id == 2
            and row2.scheme_name == "School Streets"
            and row2.bid_submitting_authority_id == 1
        )

    def test_add_schemes_financial_revisions(self, schemes: DatabaseSchemeRepository, engine: Engine) -> None:
        scheme1 = Scheme(id_=1, name="Wirral Package", authority_id=1)
        scheme1.funding.update_financials(
            FinancialRevision(
                id_=2,
                effective=DateRange(date(2020, 1, 1), date(2020, 1, 31)),
                type_=FinancialType.FUNDING_ALLOCATION,
                amount=100_000,
                source=DataSource.ATF4_BID,
            ),
            FinancialRevision(
                id_=3,
                effective=DateRange(date(2020, 2, 1), None),
                type_=FinancialType.FUNDING_ALLOCATION,
                amount=200_000,
                source=DataSource.ATF4_BID,
            ),
        )

        schemes.add(scheme1, Scheme(id_=2, name="School Streets", authority_id=1))

        with Session(engine) as session:
            row1, row2 = session.scalars(
                select(CapitalSchemeFinancialEntity).order_by(CapitalSchemeFinancialEntity.capital_scheme_financial_id)
            )
        assert (
            row1.capital_scheme_financial_id == 2
            and row1.capital_scheme_id == 1
            and row1.effective_date_from == date(2020, 1, 1)
            and row1.effective_date_to == date(2020, 1, 31)
            and row1.financial_type_id == 3
            and row1.amount == 100_000
            and row1.data_source_id == 3
        )
        assert (
            row2.capital_scheme_financial_id == 3
            and row2.capital_scheme_id == 1
            and row2.effective_date_from == date(2020, 2, 1)
            and row2.effective_date_to is None
            and row2.financial_type_id == 3
            and row2.amount == 200_000
            and row2.data_source_id == 3
        )

    def test_add_schemes_milestone_revisions(self, schemes: DatabaseSchemeRepository, engine: Engine) -> None:
        scheme1 = Scheme(id_=1, name="Wirral Package", authority_id=1)
        scheme1.milestones.update_milestones(
            MilestoneRevision(
                id_=2,
                effective=DateRange(date(2020, 1, 1), date(2020, 1, 31)),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.PLANNED,
                status_date=date(2020, 2, 1),
            ),
            MilestoneRevision(
                id_=3,
                effective=DateRange(date(2020, 2, 1), None),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.PLANNED,
                status_date=date(2020, 3, 1),
            ),
        )

        schemes.add(scheme1, Scheme(id_=2, name="School Streets", authority_id=1))

        with Session(engine) as session:
            row1, row2 = session.scalars(
                select(SchemeMilestoneEntity).order_by(SchemeMilestoneEntity.scheme_milestone_id)
            )
        assert (
            row1.scheme_milestone_id == 2
            and row1.capital_scheme_id == 1
            and row1.effective_date_from == date(2020, 1, 1)
            and row1.effective_date_to == date(2020, 1, 31)
            and row1.milestone_id == 6
            and row1.observation_type_id == 1
            and row1.status_date == date(2020, 2, 1)
        )
        assert (
            row2.scheme_milestone_id == 3
            and row2.capital_scheme_id == 1
            and row2.effective_date_from == date(2020, 2, 1)
            and row2.effective_date_to is None
            and row2.milestone_id == 6
            and row2.observation_type_id == 1
            and row2.status_date == date(2020, 3, 1)
        )

    def test_add_schemes_output_revisions(self, schemes: DatabaseSchemeRepository, engine: Engine) -> None:
        scheme1 = Scheme(id_=1, name="Wirral Package", authority_id=1)
        scheme1.outputs.update_outputs(
            OutputRevision(
                id_=3,
                effective=DateRange(date(2020, 1, 1), date(2020, 1, 31)),
                type_measure=OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES,
                value=Decimal(10),
                observation_type=ObservationType.PLANNED,
            ),
            OutputRevision(
                id_=4,
                effective=DateRange(date(2020, 2, 1), None),
                type_measure=OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES,
                value=Decimal(20),
                observation_type=ObservationType.PLANNED,
            ),
        )

        schemes.add(scheme1, Scheme(id_=2, name="School Streets", authority_id=1))

        with Session(engine) as session:
            row1, row2 = session.scalars(
                select(SchemeInterventionEntity).order_by(SchemeInterventionEntity.scheme_intervention_id)
            )
        assert (
            row1.scheme_intervention_id == 3
            and row1.capital_scheme_id == 1
            and row1.effective_date_from == date(2020, 1, 1)
            and row1.effective_date_to == date(2020, 1, 31)
            and row1.intervention_type_measure_id == 4
            and row1.intervention_value == Decimal(10)
            and row1.observation_type_id == 1
        )
        assert (
            row2.scheme_intervention_id == 4
            and row2.capital_scheme_id == 1
            and row2.effective_date_from == date(2020, 2, 1)
            and row2.effective_date_to is None
            and row2.intervention_type_measure_id == 4
            and row2.intervention_value == Decimal(20)
            and row2.observation_type_id == 1
        )

    def test_get_scheme(self, schemes: DatabaseSchemeRepository, engine: Engine) -> None:
        with Session(engine) as session:
            session.add(
                CapitalSchemeEntity(
                    capital_scheme_id=1,
                    scheme_name="Wirral Package",
                    bid_submitting_authority_id=1,
                    scheme_type_id=1,
                    funding_programme_id=2,
                )
            )
            session.commit()

        scheme = schemes.get(1)

        assert (
            scheme
            and scheme.id == 1
            and scheme.name == "Wirral Package"
            and scheme.authority_id == 1
            and scheme.type == SchemeType.DEVELOPMENT
            and scheme.funding_programme == FundingProgramme.ATF3
        )

    def test_get_scheme_financial_revisions(self, schemes: DatabaseSchemeRepository, engine: Engine) -> None:
        with Session(engine) as session:
            session.add_all(
                [
                    CapitalSchemeEntity(
                        capital_scheme_id=1,
                        scheme_name="Wirral Package",
                        bid_submitting_authority_id=1,
                    ),
                    CapitalSchemeFinancialEntity(
                        capital_scheme_financial_id=2,
                        capital_scheme_id=1,
                        effective_date_from=date(2020, 1, 1),
                        effective_date_to=date(2020, 1, 31),
                        financial_type_id=3,
                        amount=100_000,
                        data_source_id=3,
                    ),
                    CapitalSchemeFinancialEntity(
                        capital_scheme_financial_id=3,
                        capital_scheme_id=1,
                        effective_date_from=date(2020, 2, 1),
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
        financial_revision1, financial_revision2 = scheme.funding.financial_revisions
        assert (
            financial_revision1.id == 2
            and financial_revision1.effective == DateRange(date(2020, 1, 1), date(2020, 1, 31))
            and financial_revision1.type == FinancialType.FUNDING_ALLOCATION
            and financial_revision1.amount == 100_000
            and financial_revision1.source == DataSource.ATF4_BID
        )
        assert (
            financial_revision2.id == 3
            and financial_revision2.effective == DateRange(date(2020, 2, 1), None)
            and financial_revision2.type == FinancialType.FUNDING_ALLOCATION
            and financial_revision2.amount == 200_000
            and financial_revision2.source == DataSource.ATF4_BID
        )

    def test_get_scheme_milestone_revisions(self, schemes: DatabaseSchemeRepository, engine: Engine) -> None:
        with Session(engine) as session:
            session.add_all(
                [
                    CapitalSchemeEntity(
                        capital_scheme_id=1,
                        scheme_name="Wirral Package",
                        bid_submitting_authority_id=1,
                    ),
                    SchemeMilestoneEntity(
                        scheme_milestone_id=2,
                        capital_scheme_id=1,
                        effective_date_from=date(2020, 1, 1),
                        effective_date_to=date(2020, 1, 31),
                        milestone_id=6,
                        observation_type_id=1,
                        status_date=date(2020, 2, 1),
                    ),
                    SchemeMilestoneEntity(
                        scheme_milestone_id=3,
                        capital_scheme_id=1,
                        effective_date_from=date(2020, 2, 1),
                        effective_date_to=None,
                        milestone_id=6,
                        observation_type_id=1,
                        status_date=date(2020, 3, 1),
                    ),
                ]
            )
            session.commit()

        scheme = schemes.get(1)

        assert scheme
        milestone_revision1, milestone_revision2 = scheme.milestones.milestone_revisions
        assert (
            milestone_revision1.id == 2
            and milestone_revision1.effective == DateRange(date(2020, 1, 1), date(2020, 1, 31))
            and milestone_revision1.milestone == Milestone.DETAILED_DESIGN_COMPLETED
            and milestone_revision1.observation_type == ObservationType.PLANNED
            and milestone_revision1.status_date == date(2020, 2, 1)
        )
        assert (
            milestone_revision2.id == 3
            and milestone_revision2.effective == DateRange(date(2020, 2, 1), None)
            and milestone_revision2.milestone == Milestone.DETAILED_DESIGN_COMPLETED
            and milestone_revision2.observation_type == ObservationType.PLANNED
            and milestone_revision2.status_date == date(2020, 3, 1)
        )

    def test_get_scheme_output_revisions(self, schemes: DatabaseSchemeRepository, engine: Engine) -> None:
        with Session(engine) as session:
            session.add_all(
                [
                    CapitalSchemeEntity(
                        capital_scheme_id=1,
                        scheme_name="Wirral Package",
                        bid_submitting_authority_id=1,
                    ),
                    SchemeInterventionEntity(
                        scheme_intervention_id=2,
                        capital_scheme_id=1,
                        effective_date_from=date(2020, 1, 1),
                        effective_date_to=date(2020, 1, 31),
                        intervention_type_measure_id=4,
                        intervention_value=Decimal(10),
                        observation_type_id=1,
                    ),
                    SchemeInterventionEntity(
                        scheme_intervention_id=3,
                        capital_scheme_id=1,
                        effective_date_from=date(2020, 2, 1),
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
        output_revision1, output_revision2 = scheme.outputs.output_revisions
        assert (
            output_revision1.id == 2
            and output_revision1.effective == DateRange(date(2020, 1, 1), date(2020, 1, 31))
            and output_revision1.type_measure == OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES
            and output_revision1.value == Decimal(10)
            and output_revision1.observation_type == ObservationType.PLANNED
        )
        assert (
            output_revision2.id == 3
            and output_revision2.effective == DateRange(date(2020, 2, 1), None)
            and output_revision2.type_measure == OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES
            and output_revision2.value == Decimal(20)
            and output_revision2.observation_type == ObservationType.PLANNED
        )

    def test_get_scheme_that_does_not_exist(self, schemes: DatabaseSchemeRepository, engine: Engine) -> None:
        with Session(engine) as session:
            session.add(
                CapitalSchemeEntity(
                    capital_scheme_id=1,
                    scheme_name="Wirral Package",
                    bid_submitting_authority_id=1,
                )
            )
            session.commit()

        assert schemes.get(2) is None

    def test_get_all_schemes_by_authority(self, schemes: DatabaseSchemeRepository, engine: Engine) -> None:
        with Session(engine) as session:
            session.add_all(
                [
                    CapitalSchemeEntity(
                        capital_scheme_id=1,
                        scheme_name="Wirral Package",
                        bid_submitting_authority_id=1,
                        scheme_type_id=1,
                        funding_programme_id=2,
                    ),
                    CapitalSchemeEntity(
                        capital_scheme_id=2, scheme_name="School Streets", bid_submitting_authority_id=1
                    ),
                    CapitalSchemeEntity(
                        capital_scheme_id=3, scheme_name="Hospital Fields Road", bid_submitting_authority_id=2
                    ),
                ]
            )
            session.commit()

        scheme1: Scheme
        scheme2: Scheme
        scheme1, scheme2 = schemes.get_by_authority(1)

        assert (
            scheme1.id == 1
            and scheme1.name == "Wirral Package"
            and scheme1.authority_id == 1
            and scheme1.type == SchemeType.DEVELOPMENT
            and scheme1.funding_programme == FundingProgramme.ATF3
        )
        assert scheme2.id == 2 and scheme2.name == "School Streets" and scheme1.authority_id == 1

    def test_get_all_schemes_financial_revisions_by_authority(
        self, schemes: DatabaseSchemeRepository, engine: Engine
    ) -> None:
        with Session(engine) as session:
            session.add_all(
                [
                    CapitalSchemeEntity(
                        capital_scheme_id=1, scheme_name="Wirral Package", bid_submitting_authority_id=1
                    ),
                    CapitalSchemeFinancialEntity(
                        capital_scheme_id=1,
                        effective_date_from=date(2020, 1, 1),
                        effective_date_to=None,
                        financial_type_id=3,
                        amount=100_000,
                        data_source_id=3,
                    ),
                    CapitalSchemeEntity(
                        capital_scheme_id=2, scheme_name="School Streets", bid_submitting_authority_id=2
                    ),
                    CapitalSchemeFinancialEntity(
                        capital_scheme_id=2,
                        effective_date_from=date(2020, 2, 1),
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
        (financial_revision1,) = scheme1.funding.financial_revisions
        assert (
            financial_revision1.effective == DateRange(date(2020, 1, 1), None)
            and financial_revision1.type == FinancialType.FUNDING_ALLOCATION
            and financial_revision1.amount == 100_000
            and financial_revision1.source == DataSource.ATF4_BID
        )

    def test_get_all_schemes_milestone_revisions_by_authority(
        self, schemes: DatabaseSchemeRepository, engine: Engine
    ) -> None:
        with Session(engine) as session:
            session.add_all(
                [
                    CapitalSchemeEntity(
                        capital_scheme_id=1, scheme_name="Wirral Package", bid_submitting_authority_id=1
                    ),
                    SchemeMilestoneEntity(
                        scheme_milestone_id=4,
                        capital_scheme_id=1,
                        effective_date_from=date(2020, 1, 1),
                        effective_date_to=None,
                        milestone_id=6,
                        observation_type_id=1,
                        status_date=date(2020, 2, 1),
                    ),
                    CapitalSchemeEntity(
                        capital_scheme_id=2, scheme_name="School Streets", bid_submitting_authority_id=1
                    ),
                    SchemeMilestoneEntity(
                        scheme_milestone_id=5,
                        capital_scheme_id=2,
                        effective_date_from=date(2020, 2, 1),
                        effective_date_to=None,
                        milestone_id=6,
                        observation_type_id=1,
                        status_date=date(2020, 3, 1),
                    ),
                    CapitalSchemeEntity(
                        capital_scheme_id=3, scheme_name="Hospital Fields Road", bid_submitting_authority_id=2
                    ),
                    SchemeMilestoneEntity(
                        scheme_milestone_id=6,
                        capital_scheme_id=3,
                        effective_date_from=date(2020, 3, 1),
                        effective_date_to=None,
                        milestone_id=6,
                        observation_type_id=1,
                        status_date=date(2020, 4, 1),
                    ),
                ]
            )
            session.commit()

        scheme1: Scheme
        scheme2: Scheme
        scheme1, scheme2 = schemes.get_by_authority(1)

        assert scheme1.id == 1
        (milestone_revision1,) = scheme1.milestones.milestone_revisions
        assert (
            milestone_revision1.id == 4
            and milestone_revision1.effective == DateRange(date(2020, 1, 1), None)
            and milestone_revision1.milestone == Milestone.DETAILED_DESIGN_COMPLETED
            and milestone_revision1.observation_type == ObservationType.PLANNED
            and milestone_revision1.status_date == date(2020, 2, 1)
        )
        assert scheme2.id == 2
        (milestone_revision2,) = scheme2.milestones.milestone_revisions
        assert (
            milestone_revision2.id == 5
            and milestone_revision2.effective == DateRange(date(2020, 2, 1), None)
            and milestone_revision2.milestone == Milestone.DETAILED_DESIGN_COMPLETED
            and milestone_revision2.observation_type == ObservationType.PLANNED
            and milestone_revision2.status_date == date(2020, 3, 1)
        )

    def test_get_all_schemes_output_revisions_by_authority(
        self, schemes: DatabaseSchemeRepository, engine: Engine
    ) -> None:
        with Session(engine) as session:
            session.add_all(
                [
                    CapitalSchemeEntity(
                        capital_scheme_id=1, scheme_name="Wirral Package", bid_submitting_authority_id=1
                    ),
                    SchemeInterventionEntity(
                        scheme_intervention_id=4,
                        capital_scheme_id=1,
                        effective_date_from=date(2020, 1, 1),
                        effective_date_to=None,
                        intervention_type_measure_id=4,
                        intervention_value=Decimal(10),
                        observation_type_id=1,
                    ),
                    CapitalSchemeEntity(
                        capital_scheme_id=2, scheme_name="School Streets", bid_submitting_authority_id=1
                    ),
                    SchemeInterventionEntity(
                        scheme_intervention_id=5,
                        capital_scheme_id=2,
                        effective_date_from=date(2020, 2, 1),
                        effective_date_to=None,
                        intervention_type_measure_id=4,
                        intervention_value=Decimal(20),
                        observation_type_id=1,
                    ),
                    CapitalSchemeEntity(
                        capital_scheme_id=3, scheme_name="Hospital Fields Road", bid_submitting_authority_id=2
                    ),
                    SchemeInterventionEntity(
                        scheme_intervention_id=6,
                        capital_scheme_id=3,
                        effective_date_from=date(2020, 3, 1),
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
        (output_revision1,) = scheme1.outputs.output_revisions
        assert (
            output_revision1.id == 4
            and output_revision1.effective == DateRange(date(2020, 1, 1), None)
            and output_revision1.type_measure == OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES
            and output_revision1.value == Decimal(10)
            and output_revision1.observation_type == ObservationType.PLANNED
        )
        assert scheme2.id == 2
        (output_revision2,) = scheme2.outputs.output_revisions
        assert (
            output_revision2.id == 5
            and output_revision2.effective == DateRange(date(2020, 2, 1), None)
            and output_revision2.type_measure == OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES
            and output_revision2.value == Decimal(20)
            and output_revision2.observation_type == ObservationType.PLANNED
        )

    def test_clear_all_schemes(self, schemes: DatabaseSchemeRepository, engine: Engine) -> None:
        with Session(engine) as session:
            session.add_all(
                [
                    CapitalSchemeEntity(
                        capital_scheme_id=1, scheme_name="Wirral Package", bid_submitting_authority_id=1
                    ),
                    CapitalSchemeFinancialEntity(
                        capital_scheme_id=1,
                        effective_date_from=date(2020, 1, 1),
                        effective_date_to=None,
                        financial_type_id=3,
                        amount=100_000,
                        data_source_id=3,
                    ),
                    SchemeMilestoneEntity(
                        capital_scheme_id=1,
                        effective_date_from=date(2020, 1, 1),
                        effective_date_to=None,
                        milestone_id=5,
                        observation_type_id=1,
                        status_date=date(2020, 2, 1),
                    ),
                    SchemeInterventionEntity(
                        capital_scheme_id=1,
                        effective_date_from=date(2020, 1, 1),
                        effective_date_to=None,
                        intervention_type_measure_id=4,
                        intervention_value=Decimal(10),
                        observation_type_id=1,
                    ),
                    CapitalSchemeEntity(
                        capital_scheme_id=2, scheme_name="School Streets", bid_submitting_authority_id=1
                    ),
                ]
            )
            session.commit()

        schemes.clear()

        with Session(engine) as session:
            assert session.execute(select(func.count()).select_from(CapitalSchemeEntity)).scalar_one() == 0


@pytest.mark.parametrize("type_, id_", [(SchemeType.DEVELOPMENT, 1), (SchemeType.CONSTRUCTION, 2), (None, None)])
class TestSchemeTypeMapper:
    def test_to_id(self, type_: SchemeType | None, id_: int | None) -> None:
        assert SchemeTypeMapper().to_id(type_) == id_

    def test_to_domain(self, type_: SchemeType | None, id_: int | None) -> None:
        assert SchemeTypeMapper().to_domain(id_) == type_


@pytest.mark.parametrize(
    "funding_programme, id_",
    [
        (FundingProgramme.ATF2, 1),
        (FundingProgramme.ATF3, 2),
        (FundingProgramme.ATF4, 3),
        (FundingProgramme.ATF4E, 4),
        (FundingProgramme.ATF5, 5),
        (FundingProgramme.MRN, 6),
        (FundingProgramme.LUF, 7),
        (FundingProgramme.CRSTS, 8),
        (None, None),
    ],
)
class TestFundingProgrammeMapper:
    def test_to_id(self, funding_programme: FundingProgramme | None, id_: int | None) -> None:
        assert FundingProgrammeMapper().to_id(funding_programme) == id_

    def test_to_domain(self, funding_programme: FundingProgramme | None, id_: int | None) -> None:
        assert FundingProgrammeMapper().to_domain(id_) == funding_programme
