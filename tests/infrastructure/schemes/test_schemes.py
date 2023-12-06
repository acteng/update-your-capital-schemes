from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import Engine, MetaData, func, insert, select

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
from schemes.infrastructure.authorities import DatabaseAuthorityRepository
from schemes.infrastructure.authorities import add_tables as authorities_add_tables
from schemes.infrastructure.schemes import DatabaseSchemeRepository
from schemes.infrastructure.schemes import add_tables as schemes_add_tables
from schemes.infrastructure.schemes.schemes import (
    FundingProgrammeMapper,
    SchemeTypeMapper,
)


class TestDatabaseSchemeRepository:
    @pytest.fixture(name="metadata")
    def metadata_fixture(self) -> MetaData:
        metadata = MetaData()
        authorities_add_tables(metadata)
        schemes_add_tables(metadata)
        return metadata

    @pytest.fixture(name="engine")
    def engine_fixture(self, engine: Engine, metadata: MetaData) -> Engine:
        metadata.create_all(engine)
        return engine

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

    def test_add_schemes(self, schemes: DatabaseSchemeRepository, engine: Engine, metadata: MetaData) -> None:
        scheme1 = Scheme(id_=1, name="Wirral Package", authority_id=1)
        scheme1.type = SchemeType.DEVELOPMENT
        scheme1.funding_programme = FundingProgramme.ATF3

        schemes.add(scheme1, Scheme(id_=2, name="School Streets", authority_id=1))

        capital_scheme_table = metadata.tables["capital_scheme"]
        with engine.connect() as connection:
            row1, row2 = connection.execute(
                select(capital_scheme_table).order_by(capital_scheme_table.c.capital_scheme_id)
            )
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

    def test_add_schemes_financial_revisions(
        self, schemes: DatabaseSchemeRepository, engine: Engine, metadata: MetaData
    ) -> None:
        scheme1 = Scheme(id_=1, name="Wirral Package", authority_id=1)
        scheme1.funding.update_financials(
            FinancialRevision(
                effective=DateRange(date(2020, 1, 1), date(2020, 1, 31)),
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Decimal(100000),
                source=DataSource.ATF4_BID,
            ),
            FinancialRevision(
                effective=DateRange(date(2020, 2, 1), None),
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Decimal(200000),
                source=DataSource.ATF4_BID,
            ),
        )

        schemes.add(scheme1, Scheme(id_=2, name="School Streets", authority_id=1))

        capital_scheme_financial_table = metadata.tables["capital_scheme_financial"]
        with engine.connect() as connection:
            row1, row2 = connection.execute(
                select(capital_scheme_financial_table).order_by(
                    capital_scheme_financial_table.c.capital_scheme_financial_id
                )
            )
        assert (
            row1.capital_scheme_id == 1
            and row1.effective_date_from == date(2020, 1, 1)
            and row1.effective_date_to == date(2020, 1, 31)
            and row1.financial_type_id == 3
            and row1.amount == Decimal(100000)
            and row1.data_source_id == 3
        )
        assert (
            row2.capital_scheme_id == 1
            and row2.effective_date_from == date(2020, 2, 1)
            and row2.effective_date_to is None
            and row2.financial_type_id == 3
            and row2.amount == Decimal(200000)
            and row2.data_source_id == 3
        )

    def test_add_schemes_milestone_revisions(
        self, schemes: DatabaseSchemeRepository, engine: Engine, metadata: MetaData
    ) -> None:
        scheme1 = Scheme(id_=1, name="Wirral Package", authority_id=1)
        scheme1.milestones.update_milestones(
            MilestoneRevision(
                effective=DateRange(date(2020, 1, 1), date(2020, 1, 31)),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.PLANNED,
                status_date=date(2020, 2, 1),
            ),
            MilestoneRevision(
                effective=DateRange(date(2020, 2, 1), None),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.PLANNED,
                status_date=date(2020, 3, 1),
            ),
        )

        schemes.add(scheme1, Scheme(id_=2, name="School Streets", authority_id=1))

        scheme_milestone_table = metadata.tables["scheme_milestone"]
        with engine.connect() as connection:
            row1, row2 = connection.execute(
                select(scheme_milestone_table).order_by(scheme_milestone_table.c.scheme_milestone_id)
            )
        assert (
            row1.capital_scheme_id == 1
            and row1.effective_date_from == date(2020, 1, 1)
            and row1.effective_date_to == date(2020, 1, 31)
            and row1.milestone_id == 5
            and row1.observation_type_id == 1
            and row1.status_date == date(2020, 2, 1)
        )
        assert (
            row2.capital_scheme_id == 1
            and row2.effective_date_from == date(2020, 2, 1)
            and row2.effective_date_to is None
            and row2.milestone_id == 5
            and row2.observation_type_id == 1
            and row2.status_date == date(2020, 3, 1)
        )

    def test_add_schemes_output_revisions(
        self, schemes: DatabaseSchemeRepository, engine: Engine, metadata: MetaData
    ) -> None:
        scheme1 = Scheme(id_=1, name="Wirral Package", authority_id=1)
        scheme1.outputs.update_outputs(
            OutputRevision(
                effective=DateRange(date(2020, 1, 1), date(2020, 1, 31)),
                type_measure=OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES,
                value=Decimal(10),
                observation_type=ObservationType.PLANNED,
            ),
            OutputRevision(
                effective=DateRange(date(2020, 2, 1), None),
                type_measure=OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES,
                value=Decimal(20),
                observation_type=ObservationType.PLANNED,
            ),
        )

        schemes.add(scheme1, Scheme(id_=2, name="School Streets", authority_id=1))

        scheme_intervention_table = metadata.tables["scheme_intervention"]
        with engine.connect() as connection:
            row1, row2 = connection.execute(
                select(scheme_intervention_table).order_by(scheme_intervention_table.c.scheme_intervention_id)
            )
        assert (
            row1.capital_scheme_id == 1
            and row1.effective_date_from == date(2020, 1, 1)
            and row1.effective_date_to == date(2020, 1, 31)
            and row1.intervention_type_measure_id == 4
            and row1.intervention_value == Decimal(10)
            and row1.observation_type_id == 1
        )
        assert (
            row2.capital_scheme_id == 1
            and row2.effective_date_from == date(2020, 2, 1)
            and row2.effective_date_to is None
            and row2.intervention_type_measure_id == 4
            and row2.intervention_value == Decimal(20)
            and row2.observation_type_id == 1
        )

    def test_get_scheme(self, schemes: DatabaseSchemeRepository, engine: Engine, metadata: MetaData) -> None:
        with engine.begin() as connection:
            connection.execute(
                insert(metadata.tables["capital_scheme"]).values(
                    capital_scheme_id=1,
                    scheme_name="Wirral Package",
                    bid_submitting_authority_id=1,
                    scheme_type_id=1,
                    funding_programme_id=2,
                )
            )

        scheme = schemes.get(1)

        assert (
            scheme
            and scheme.id == 1
            and scheme.name == "Wirral Package"
            and scheme.authority_id == 1
            and scheme.type == SchemeType.DEVELOPMENT
            and scheme.funding_programme == FundingProgramme.ATF3
        )

    def test_get_scheme_financial_revisions(
        self, schemes: DatabaseSchemeRepository, engine: Engine, metadata: MetaData
    ) -> None:
        with engine.begin() as connection:
            connection.execute(
                insert(metadata.tables["capital_scheme"]).values(
                    capital_scheme_id=1,
                    scheme_name="Wirral Package",
                    bid_submitting_authority_id=1,
                )
            )
            connection.execute(
                insert(metadata.tables["capital_scheme_financial"]).values(
                    capital_scheme_id=1,
                    effective_date_from=date(2020, 1, 1),
                    effective_date_to=date(2020, 1, 31),
                    financial_type_id=3,
                    amount=Decimal(100000),
                    data_source_id=3,
                )
            )
            connection.execute(
                insert(metadata.tables["capital_scheme_financial"]).values(
                    capital_scheme_id=1,
                    effective_date_from=date(2020, 2, 1),
                    effective_date_to=None,
                    financial_type_id=3,
                    amount=Decimal(200000),
                    data_source_id=3,
                )
            )

        scheme = schemes.get(1)

        assert scheme and scheme.funding.financial_revisions == [
            FinancialRevision(
                effective=DateRange(date(2020, 1, 1), date(2020, 1, 31)),
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Decimal(100000),
                source=DataSource.ATF4_BID,
            ),
            FinancialRevision(
                effective=DateRange(date(2020, 2, 1), None),
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Decimal(200000),
                source=DataSource.ATF4_BID,
            ),
        ]

    def test_get_scheme_milestone_revisions(
        self, schemes: DatabaseSchemeRepository, engine: Engine, metadata: MetaData
    ) -> None:
        with engine.begin() as connection:
            connection.execute(
                insert(metadata.tables["capital_scheme"]).values(
                    capital_scheme_id=1,
                    scheme_name="Wirral Package",
                    bid_submitting_authority_id=1,
                )
            )
            connection.execute(
                insert(metadata.tables["scheme_milestone"]).values(
                    capital_scheme_id=1,
                    effective_date_from=date(2020, 1, 1),
                    effective_date_to=date(2020, 1, 31),
                    milestone_id=5,
                    observation_type_id=1,
                    status_date=date(2020, 2, 1),
                )
            )
            connection.execute(
                insert(metadata.tables["scheme_milestone"]).values(
                    capital_scheme_id=1,
                    effective_date_from=date(2020, 2, 1),
                    effective_date_to=None,
                    milestone_id=5,
                    observation_type_id=1,
                    status_date=date(2020, 3, 1),
                )
            )

        scheme = schemes.get(1)

        assert scheme and scheme.milestones.milestone_revisions == [
            MilestoneRevision(
                effective=DateRange(date(2020, 1, 1), date(2020, 1, 31)),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.PLANNED,
                status_date=date(2020, 2, 1),
            ),
            MilestoneRevision(
                effective=DateRange(date(2020, 2, 1), None),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.PLANNED,
                status_date=date(2020, 3, 1),
            ),
        ]

    def test_get_scheme_output_revisions(
        self, schemes: DatabaseSchemeRepository, engine: Engine, metadata: MetaData
    ) -> None:
        with engine.begin() as connection:
            connection.execute(
                insert(metadata.tables["capital_scheme"]).values(
                    capital_scheme_id=1,
                    scheme_name="Wirral Package",
                    bid_submitting_authority_id=1,
                )
            )
            connection.execute(
                insert(metadata.tables["scheme_intervention"]).values(
                    capital_scheme_id=1,
                    effective_date_from=date(2020, 1, 1),
                    effective_date_to=date(2020, 1, 31),
                    intervention_type_measure_id=4,
                    intervention_value=Decimal(10),
                    observation_type_id=1,
                )
            )
            connection.execute(
                insert(metadata.tables["scheme_intervention"]).values(
                    capital_scheme_id=1,
                    effective_date_from=date(2020, 2, 1),
                    effective_date_to=None,
                    intervention_type_measure_id=4,
                    intervention_value=Decimal(20),
                    observation_type_id=1,
                )
            )

        scheme = schemes.get(1)

        assert scheme and scheme.outputs.output_revisions == [
            OutputRevision(
                effective=DateRange(date(2020, 1, 1), date(2020, 1, 31)),
                type_measure=OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES,
                value=Decimal(10),
                observation_type=ObservationType.PLANNED,
            ),
            OutputRevision(
                effective=DateRange(date(2020, 2, 1), None),
                type_measure=OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES,
                value=Decimal(20),
                observation_type=ObservationType.PLANNED,
            ),
        ]

    def test_get_scheme_output_revision_with_no_value(
        self, schemes: DatabaseSchemeRepository, engine: Engine, metadata: MetaData
    ) -> None:
        with engine.begin() as connection:
            connection.execute(
                insert(metadata.tables["capital_scheme"]).values(
                    capital_scheme_id=1,
                    scheme_name="Wirral Package",
                    bid_submitting_authority_id=1,
                )
            )
            connection.execute(
                insert(metadata.tables["scheme_intervention"]).values(
                    capital_scheme_id=1,
                    effective_date_from=date(2020, 1, 1),
                    effective_date_to=date(2020, 1, 31),
                    intervention_type_measure_id=4,
                    intervention_value=None,
                    observation_type_id=1,
                )
            )

        scheme = schemes.get(1)

        assert scheme and scheme.outputs.output_revisions[0].value == Decimal(0)

    def test_get_scheme_that_does_not_exist(
        self, schemes: DatabaseSchemeRepository, engine: Engine, metadata: MetaData
    ) -> None:
        with engine.begin() as connection:
            connection.execute(
                insert(metadata.tables["capital_scheme"]).values(
                    capital_scheme_id=1,
                    scheme_name="Wirral Package",
                    bid_submitting_authority_id=1,
                )
            )

        assert schemes.get(2) is None

    def test_get_all_schemes_by_authority(
        self, schemes: DatabaseSchemeRepository, engine: Engine, metadata: MetaData
    ) -> None:
        capital_scheme_table = metadata.tables["capital_scheme"]
        with engine.begin() as connection:
            connection.execute(
                insert(capital_scheme_table).values(
                    capital_scheme_id=1,
                    scheme_name="Wirral Package",
                    bid_submitting_authority_id=1,
                    scheme_type_id=1,
                    funding_programme_id=2,
                )
            )
            connection.execute(
                insert(capital_scheme_table).values(
                    capital_scheme_id=2, scheme_name="School Streets", bid_submitting_authority_id=1
                )
            )
            connection.execute(
                insert(capital_scheme_table).values(
                    capital_scheme_id=3, scheme_name="Hospital Fields Road", bid_submitting_authority_id=2
                )
            )

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
        self, schemes: DatabaseSchemeRepository, engine: Engine, metadata: MetaData
    ) -> None:
        with engine.begin() as connection:
            connection.execute(
                insert(metadata.tables["capital_scheme"]).values(
                    capital_scheme_id=1, scheme_name="Wirral Package", bid_submitting_authority_id=1
                )
            )
            connection.execute(
                insert(metadata.tables["capital_scheme_financial"]).values(
                    capital_scheme_id=1,
                    effective_date_from=date(2020, 1, 1),
                    effective_date_to=None,
                    financial_type_id=3,
                    amount=Decimal(100000),
                    data_source_id=3,
                )
            )
            connection.execute(
                insert(metadata.tables["capital_scheme"]).values(
                    capital_scheme_id=2, scheme_name="School Streets", bid_submitting_authority_id=2
                )
            )
            connection.execute(
                insert(metadata.tables["capital_scheme_financial"]).values(
                    capital_scheme_id=2,
                    effective_date_from=date(2020, 2, 1),
                    effective_date_to=None,
                    financial_type_id=3,
                    amount=Decimal(200000),
                    data_source_id=3,
                )
            )

        scheme1: Scheme
        (scheme1,) = schemes.get_by_authority(1)

        assert scheme1.id == 1 and scheme1.funding.financial_revisions == [
            FinancialRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Decimal(100000),
                source=DataSource.ATF4_BID,
            )
        ]

    def test_get_all_schemes_milestone_revisions_by_authority(
        self, schemes: DatabaseSchemeRepository, engine: Engine, metadata: MetaData
    ) -> None:
        with engine.begin() as connection:
            connection.execute(
                insert(metadata.tables["capital_scheme"]).values(
                    capital_scheme_id=1, scheme_name="Wirral Package", bid_submitting_authority_id=1
                )
            )
            connection.execute(
                insert(metadata.tables["scheme_milestone"]).values(
                    capital_scheme_id=1,
                    effective_date_from=date(2020, 1, 1),
                    effective_date_to=None,
                    milestone_id=5,
                    observation_type_id=1,
                    status_date=date(2020, 2, 1),
                )
            )
            connection.execute(
                insert(metadata.tables["capital_scheme"]).values(
                    capital_scheme_id=2, scheme_name="School Streets", bid_submitting_authority_id=1
                )
            )
            connection.execute(
                insert(metadata.tables["scheme_milestone"]).values(
                    capital_scheme_id=2,
                    effective_date_from=date(2020, 2, 1),
                    effective_date_to=None,
                    milestone_id=5,
                    observation_type_id=1,
                    status_date=date(2020, 3, 1),
                )
            )
            connection.execute(
                insert(metadata.tables["capital_scheme"]).values(
                    capital_scheme_id=3, scheme_name="Hospital Fields Road", bid_submitting_authority_id=2
                )
            )
            connection.execute(
                insert(metadata.tables["scheme_milestone"]).values(
                    capital_scheme_id=3,
                    effective_date_from=date(2020, 3, 1),
                    effective_date_to=None,
                    milestone_id=5,
                    observation_type_id=1,
                    status_date=date(2020, 4, 1),
                )
            )

        scheme1: Scheme
        scheme2: Scheme
        scheme1, scheme2 = schemes.get_by_authority(1)

        assert scheme1.id == 1 and scheme1.milestones.milestone_revisions == [
            MilestoneRevision(
                effective=DateRange(date(2020, 1, 1), None),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.PLANNED,
                status_date=date(2020, 2, 1),
            )
        ]
        assert scheme2.id == 2 and scheme2.milestones.milestone_revisions == [
            MilestoneRevision(
                effective=DateRange(date(2020, 2, 1), None),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.PLANNED,
                status_date=date(2020, 3, 1),
            )
        ]

    def test_get_all_schemes_output_revisions_by_authority(
        self, schemes: DatabaseSchemeRepository, engine: Engine, metadata: MetaData
    ) -> None:
        with engine.begin() as connection:
            connection.execute(
                insert(metadata.tables["capital_scheme"]).values(
                    capital_scheme_id=1, scheme_name="Wirral Package", bid_submitting_authority_id=1
                )
            )
            connection.execute(
                insert(metadata.tables["scheme_intervention"]).values(
                    capital_scheme_id=1,
                    effective_date_from=date(2020, 1, 1),
                    effective_date_to=None,
                    intervention_type_measure_id=4,
                    intervention_value=Decimal(10),
                    observation_type_id=1,
                )
            )
            connection.execute(
                insert(metadata.tables["capital_scheme"]).values(
                    capital_scheme_id=2, scheme_name="School Streets", bid_submitting_authority_id=1
                )
            )
            connection.execute(
                insert(metadata.tables["scheme_intervention"]).values(
                    capital_scheme_id=2,
                    effective_date_from=date(2020, 2, 1),
                    effective_date_to=None,
                    intervention_type_measure_id=4,
                    intervention_value=Decimal(20),
                    observation_type_id=1,
                )
            )
            connection.execute(
                insert(metadata.tables["capital_scheme"]).values(
                    capital_scheme_id=3, scheme_name="Hospital Fields Road", bid_submitting_authority_id=2
                )
            )
            connection.execute(
                insert(metadata.tables["scheme_intervention"]).values(
                    capital_scheme_id=3,
                    effective_date_from=date(2020, 3, 1),
                    effective_date_to=None,
                    intervention_type_measure_id=4,
                    intervention_value=Decimal(30),
                    observation_type_id=1,
                )
            )

        scheme1: Scheme
        scheme2: Scheme
        scheme1, scheme2 = schemes.get_by_authority(1)

        assert scheme1.id == 1 and scheme1.outputs.output_revisions == [
            OutputRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type_measure=OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES,
                value=Decimal(10),
                observation_type=ObservationType.PLANNED,
            ),
        ]
        assert scheme2.id == 2 and scheme2.outputs.output_revisions == [
            OutputRevision(
                effective=DateRange(date(2020, 2, 1), None),
                type_measure=OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES,
                value=Decimal(20),
                observation_type=ObservationType.PLANNED,
            ),
        ]

    def test_clear_all_schemes(self, schemes: DatabaseSchemeRepository, engine: Engine, metadata: MetaData) -> None:
        capital_scheme_table = metadata.tables["capital_scheme"]
        with engine.begin() as connection:
            connection.execute(
                insert(capital_scheme_table).values(
                    capital_scheme_id=1, scheme_name="Wirral Package", bid_submitting_authority_id=1
                )
            )
            connection.execute(
                insert(metadata.tables["capital_scheme_financial"]).values(
                    capital_scheme_id=1,
                    effective_date_from=date(2020, 1, 1),
                    effective_date_to=None,
                    financial_type_id=3,
                    amount=Decimal(100000),
                    data_source_id=3,
                )
            )
            connection.execute(
                insert(metadata.tables["scheme_milestone"]).values(
                    capital_scheme_id=1,
                    effective_date_from=date(2020, 1, 1),
                    effective_date_to=None,
                    milestone_id=5,
                    observation_type_id=1,
                    status_date=date(2020, 2, 1),
                )
            )
            connection.execute(
                insert(metadata.tables["scheme_intervention"]).values(
                    capital_scheme_id=1,
                    effective_date_from=date(2020, 1, 1),
                    effective_date_to=None,
                    intervention_type_measure_id=4,
                    intervention_value=Decimal(10),
                    observation_type_id=1,
                )
            )
            connection.execute(
                insert(capital_scheme_table).values(
                    capital_scheme_id=2, scheme_name="School Streets", bid_submitting_authority_id=1
                )
            )

        schemes.clear()

        with engine.connect() as connection:
            count = connection.execute(select(func.count("*")).select_from(capital_scheme_table)).scalar()
        assert count == 0


class TestSchemeTypeMapper:
    @pytest.mark.parametrize("type_, id_", [(SchemeType.DEVELOPMENT, 1), (SchemeType.CONSTRUCTION, 2), (None, None)])
    def test_mapper(self, type_: SchemeType | None, id_: int | None) -> None:
        mapper = SchemeTypeMapper()
        assert mapper.to_id(type_) == id_ and mapper.to_domain(id_) == type_


class TestFundingProgrammeMapper:
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
    def test_mapper(self, funding_programme: FundingProgramme | None, id_: int | None) -> None:
        mapper = FundingProgrammeMapper()
        assert mapper.to_id(funding_programme) == id_ and mapper.to_domain(id_) == funding_programme
