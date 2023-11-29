from typing import Any

import inject
from sqlalchemy import (
    Column,
    Date,
    Engine,
    ForeignKey,
    Integer,
    MetaData,
    Numeric,
    Row,
    Table,
    Text,
    delete,
    insert,
    select,
)

from schemes.domain.schemes import (
    DataSource,
    DateRange,
    FinancialRevision,
    FinancialType,
    FundingProgramme,
    Milestone,
    MilestoneRevision,
    ObservationType,
    Scheme,
    SchemeRepository,
    SchemeType,
)


def add_tables(metadata: MetaData) -> None:
    Table(
        "capital_scheme",
        metadata,
        Column("capital_scheme_id", Integer, primary_key=True),
        Column("scheme_name", Text, nullable=False),
        Column(
            "bid_submitting_authority_id",
            Integer,
            ForeignKey("authority.authority_id", name="capital_scheme_bid_submitting_authority_id_fkey"),
        ),
        Column("scheme_type_id", Integer),
        Column("funding_programme_id", Integer),
    )

    Table(
        "scheme_milestone",
        metadata,
        Column("scheme_milestone_id", Integer, primary_key=True),
        Column(
            "capital_scheme_id",
            Integer,
            ForeignKey("capital_scheme.capital_scheme_id", name="scheme_milestone_capital_scheme_id_fkey"),
            nullable=False,
        ),
        Column("milestone_id", Integer, nullable=False),
        Column("status_date", Date, nullable=False),
        Column("observation_type_id", Integer, nullable=False),
        Column("effective_date_from", Date, nullable=False),
        Column("effective_date_to", Date),
    )

    Table(
        "capital_scheme_financial",
        metadata,
        Column("capital_scheme_financial_id", Integer, primary_key=True),
        Column(
            "capital_scheme_id",
            Integer,
            ForeignKey("capital_scheme.capital_scheme_id", name="capital_scheme_financial_capital_scheme_id_fkey"),
            nullable=False,
        ),
        Column("financial_type_id", Integer, nullable=False),
        Column("amount", Numeric, nullable=False),
        Column("effective_date_from", Date, nullable=False),
        Column("effective_date_to", Date),
        Column("data_source_id", Integer, nullable=False),
    )


class DatabaseSchemeRepository(SchemeRepository):
    @inject.autoparams()
    def __init__(self, engine: Engine):
        self._engine = engine
        metadata = MetaData()
        add_tables(metadata)
        self._capital_scheme_table = metadata.tables["capital_scheme"]
        self._scheme_milestone_table = metadata.tables["scheme_milestone"]
        self._capital_scheme_financial_table = metadata.tables["capital_scheme_financial"]

    def add(self, *schemes: Scheme) -> None:
        with self._engine.begin() as connection:
            for scheme in schemes:
                connection.execute(
                    insert(self._capital_scheme_table).values(
                        capital_scheme_id=scheme.id,
                        scheme_name=scheme.name,
                        bid_submitting_authority_id=scheme.authority_id,
                        scheme_type_id=SCHEME_TYPE_MAPPER.to_id(scheme.type),
                        funding_programme_id=FUNDING_PROGRAMME_MAPPER.to_id(scheme.funding_programme),
                    )
                )
                for milestone_revision in scheme.milestones.milestone_revisions:
                    connection.execute(
                        insert(self._scheme_milestone_table).values(
                            capital_scheme_id=scheme.id,
                            effective_date_from=milestone_revision.effective.date_from,
                            effective_date_to=milestone_revision.effective.date_to,
                            milestone_id=MILESTONE_MAPPER.to_id(milestone_revision.milestone),
                            observation_type_id=OBSERVATION_TYPE_MAPPER.to_id(milestone_revision.observation_type),
                            status_date=milestone_revision.status_date,
                        )
                    )
                for financial_revision in scheme.funding.financial_revisions:
                    connection.execute(
                        insert(self._capital_scheme_financial_table).values(
                            capital_scheme_id=scheme.id,
                            effective_date_from=financial_revision.effective.date_from,
                            effective_date_to=financial_revision.effective.date_to,
                            financial_type_id=FINANCIAL_TYPE_MAPPER.to_id(financial_revision.type),
                            amount=financial_revision.amount,
                            data_source_id=DATA_SOURCE_MAPPER.to_id(financial_revision.source),
                        )
                    )

    def clear(self) -> None:
        with self._engine.begin() as connection:
            connection.execute(delete(self._scheme_milestone_table))
            connection.execute(delete(self._capital_scheme_financial_table))
            connection.execute(delete(self._capital_scheme_table))

    def get(self, id_: int) -> Scheme | None:
        with self._engine.connect() as connection:
            result = connection.execute(
                select(self._capital_scheme_table).where(self._capital_scheme_table.c.capital_scheme_id == id_)
            )
            row = result.one_or_none()
            scheme = self._capital_scheme_to_domain(row) if row else None

            if scheme:
                result = connection.execute(
                    select(self._scheme_milestone_table).where(self._scheme_milestone_table.c.capital_scheme_id == id_)
                )
                for row in result:
                    scheme.milestones.update_milestone(self._scheme_milestone_to_domain(row))

                result = connection.execute(
                    select(self._capital_scheme_financial_table).where(
                        self._capital_scheme_financial_table.c.capital_scheme_id == id_
                    )
                )
                for row in result:
                    scheme.funding.update_financial(self._capital_scheme_financial_to_domain(row))

            return scheme

    def get_by_authority(self, authority_id: int) -> list[Scheme]:
        with self._engine.connect() as connection:
            result = connection.execute(
                select(self._capital_scheme_table)
                .where(self._capital_scheme_table.c.bid_submitting_authority_id == authority_id)
                .order_by(self._capital_scheme_table.c.capital_scheme_id)
            )
            schemes = [self._capital_scheme_to_domain(row) for row in result]

            result = connection.execute(
                select(self._scheme_milestone_table)
                .join(self._capital_scheme_table)
                .where(self._capital_scheme_table.c.bid_submitting_authority_id == authority_id)
            )
            for row in result:
                scheme = next((scheme for scheme in schemes if scheme.id == row.capital_scheme_id))
                scheme.milestones.update_milestone(self._scheme_milestone_to_domain(row))

            result = connection.execute(
                select(self._capital_scheme_financial_table)
                .join(self._capital_scheme_table)
                .where(self._capital_scheme_table.c.bid_submitting_authority_id == authority_id)
            )
            for row in result:
                scheme = next((scheme for scheme in schemes if scheme.id == row.capital_scheme_id))
                scheme.funding.update_financial(self._capital_scheme_financial_to_domain(row))

            return schemes

    @staticmethod
    def _capital_scheme_to_domain(row: Row[Any]) -> Scheme:
        scheme = Scheme(id_=row.capital_scheme_id, name=row.scheme_name, authority_id=row.bid_submitting_authority_id)
        scheme.type = SCHEME_TYPE_MAPPER.to_domain(row.scheme_type_id)
        scheme.funding_programme = FUNDING_PROGRAMME_MAPPER.to_domain(row.funding_programme_id)
        return scheme

    @staticmethod
    def _scheme_milestone_to_domain(row: Row[Any]) -> MilestoneRevision:
        return MilestoneRevision(
            effective=DateRange(row.effective_date_from, row.effective_date_to),
            milestone=MILESTONE_MAPPER.to_domain(row.milestone_id),
            observation_type=OBSERVATION_TYPE_MAPPER.to_domain(row.observation_type_id),
            status_date=row.status_date,
        )

    @staticmethod
    def _capital_scheme_financial_to_domain(row: Row[Any]) -> FinancialRevision:
        return FinancialRevision(
            effective=DateRange(row.effective_date_from, row.effective_date_to),
            type=FINANCIAL_TYPE_MAPPER.to_domain(row.financial_type_id),
            amount=row.amount,
            source=DATA_SOURCE_MAPPER.to_domain(row.data_source_id),
        )


class SchemeTypeMapper:
    _TYPE_IDS = {
        SchemeType.DEVELOPMENT: 1,
        SchemeType.CONSTRUCTION: 2,
    }

    def to_id(self, type_: SchemeType | None) -> int | None:
        return self._TYPE_IDS[type_] if type_ else None

    def to_domain(self, id_: int | None) -> SchemeType | None:
        return next(key for key, value in self._TYPE_IDS.items() if value == id_) if id_ else None


class FundingProgrammeMapper:
    _FUNDING_PROGRAMME_IDS = {
        FundingProgramme.ATF2: 1,
        FundingProgramme.ATF3: 2,
        FundingProgramme.ATF4: 3,
        FundingProgramme.ATF4E: 4,
        FundingProgramme.ATF5: 5,
        FundingProgramme.MRN: 6,
        FundingProgramme.LUF: 7,
        FundingProgramme.CRSTS: 8,
    }

    def to_id(self, funding_programme: FundingProgramme | None) -> int | None:
        return self._FUNDING_PROGRAMME_IDS[funding_programme] if funding_programme else None

    def to_domain(self, id_: int | None) -> FundingProgramme | None:
        return next(key for key, value in self._FUNDING_PROGRAMME_IDS.items() if value == id_) if id_ else None


class MilestoneMapper:
    _MILESTONE_IDS = {
        Milestone.PUBLIC_CONSULTATION_COMPLETED: 1,
        Milestone.FEASIBILITY_DESIGN_COMPLETED: 2,
        Milestone.PRELIMINARY_DESIGN_COMPLETED: 3,
        Milestone.OUTLINE_DESIGN_COMPLETED: 4,
        Milestone.DETAILED_DESIGN_COMPLETED: 5,
        Milestone.CONSTRUCTION_STARTED: 6,
        Milestone.CONSTRUCTION_COMPLETED: 7,
        Milestone.INSPECTION: 8,
        Milestone.NOT_PROGRESSED: 9,
        Milestone.SUPERSEDED: 10,
        Milestone.REMOVED: 11,
    }

    def to_id(self, milestone: Milestone) -> int:
        return self._MILESTONE_IDS[milestone]

    def to_domain(self, id_: int) -> Milestone:
        return next(key for key, value in self._MILESTONE_IDS.items() if value == id_)


class ObservationTypeMapper:
    _OBSERVATION_TYPE_IDS = {
        ObservationType.PLANNED: 1,
        ObservationType.ACTUAL: 2,
    }

    def to_id(self, observation_type: ObservationType) -> int:
        return self._OBSERVATION_TYPE_IDS[observation_type]

    def to_domain(self, id_: int) -> ObservationType:
        return next(key for key, value in self._OBSERVATION_TYPE_IDS.items() if value == id_)


class FinancialTypeMapper:
    _FINANCIAL_TYPE_IDS = {
        FinancialType.EXPECTED_COST: 1,
        FinancialType.ACTUAL_COST: 2,
        FinancialType.FUNDING_ALLOCATION: 3,
        FinancialType.SPENT_TO_DATE: 4,
        FinancialType.FUNDING_REQUEST: 5,
    }

    def to_id(self, financial_type: FinancialType) -> int:
        return self._FINANCIAL_TYPE_IDS[financial_type]

    def to_domain(self, id_: int) -> FinancialType:
        return next(key for key, value in self._FINANCIAL_TYPE_IDS.items() if value == id_)


class DataSourceMapper:
    _DATA_SOURCE_IDS = {
        DataSource.PULSE_5: 1,
        DataSource.PULSE_6: 2,
        DataSource.ATF4_BID: 3,
        DataSource.ATF3_BID: 4,
        DataSource.INSPECTORATE_REVIEW: 5,
        DataSource.REGIONAL_ENGAGEMENT_MANAGER_REVIEW: 6,
        DataSource.ATE_PUBLISHED_DATA: 7,
        DataSource.CHANGE_CONTROL: 8,
        DataSource.ATF4E_BID: 9,
        DataSource.PULSE_2023_24_Q2: 10,
        DataSource.INITIAL_SCHEME_LIST: 11,
    }

    def to_id(self, data_source: DataSource) -> int:
        return self._DATA_SOURCE_IDS[data_source]

    def to_domain(self, id_: int) -> DataSource:
        return next(key for key, value in self._DATA_SOURCE_IDS.items() if value == id_)


SCHEME_TYPE_MAPPER = SchemeTypeMapper()
FUNDING_PROGRAMME_MAPPER = FundingProgrammeMapper()
MILESTONE_MAPPER = MilestoneMapper()
OBSERVATION_TYPE_MAPPER = ObservationTypeMapper()
FINANCIAL_TYPE_MAPPER = FinancialTypeMapper()
DATA_SOURCE_MAPPER = DataSourceMapper()
