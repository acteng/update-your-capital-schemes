from typing import Any

import inject
from sqlalchemy import Engine, Row, delete, insert, select

from schemes.domain.schemes import (
    DateRange,
    FinancialRevision,
    FundingProgramme,
    MilestoneRevision,
    OutputRevision,
    Scheme,
    SchemeRepository,
    SchemeType,
)
from schemes.infrastructure import (
    capital_scheme_financial_table,
    capital_scheme_table,
    scheme_intervention_table,
    scheme_milestone_table,
)
from schemes.infrastructure.schemes.funding import DataSourceMapper, FinancialTypeMapper
from schemes.infrastructure.schemes.milestones import MilestoneMapper
from schemes.infrastructure.schemes.observations import ObservationTypeMapper
from schemes.infrastructure.schemes.outputs import OutputTypeMeasureMapper


class DatabaseSchemeRepository(SchemeRepository):
    @inject.autoparams()
    def __init__(self, engine: Engine):
        self._engine = engine
        self._scheme_type_mapper = SchemeTypeMapper()
        self._funding_programme_mapper = FundingProgrammeMapper()
        self._milestone_mapper = MilestoneMapper()
        self._observation_type_mapper = ObservationTypeMapper()
        self._financial_type_mapper = FinancialTypeMapper()
        self._data_source_mapper = DataSourceMapper()
        self._output_type_measure_mapper = OutputTypeMeasureMapper()

    def add(self, *schemes: Scheme) -> None:
        with self._engine.begin() as connection:
            for scheme in schemes:
                connection.execute(
                    insert(capital_scheme_table).values(
                        capital_scheme_id=scheme.id,
                        scheme_name=scheme.name,
                        bid_submitting_authority_id=scheme.authority_id,
                        scheme_type_id=self._scheme_type_mapper.to_id(scheme.type),
                        funding_programme_id=self._funding_programme_mapper.to_id(scheme.funding_programme),
                    )
                )
                for financial_revision in scheme.funding.financial_revisions:
                    connection.execute(
                        insert(capital_scheme_financial_table).values(
                            capital_scheme_id=scheme.id,
                            effective_date_from=financial_revision.effective.date_from,
                            effective_date_to=financial_revision.effective.date_to,
                            financial_type_id=self._financial_type_mapper.to_id(financial_revision.type),
                            amount=financial_revision.amount,
                            data_source_id=self._data_source_mapper.to_id(financial_revision.source),
                        )
                    )
                for milestone_revision in scheme.milestones.milestone_revisions:
                    connection.execute(
                        insert(scheme_milestone_table).values(
                            capital_scheme_id=scheme.id,
                            effective_date_from=milestone_revision.effective.date_from,
                            effective_date_to=milestone_revision.effective.date_to,
                            milestone_id=self._milestone_mapper.to_id(milestone_revision.milestone),
                            observation_type_id=self._observation_type_mapper.to_id(
                                milestone_revision.observation_type
                            ),
                            status_date=milestone_revision.status_date,
                        )
                    )
                for output_revision in scheme.outputs.output_revisions:
                    connection.execute(
                        insert(scheme_intervention_table).values(
                            capital_scheme_id=scheme.id,
                            effective_date_from=output_revision.effective.date_from,
                            effective_date_to=output_revision.effective.date_to,
                            intervention_type_measure_id=self._output_type_measure_mapper.to_id(
                                output_revision.type_measure
                            ),
                            intervention_value=output_revision.value,
                            observation_type_id=self._observation_type_mapper.to_id(output_revision.observation_type),
                        )
                    )

    def clear(self) -> None:
        with self._engine.begin() as connection:
            connection.execute(delete(scheme_intervention_table))
            connection.execute(delete(scheme_milestone_table))
            connection.execute(delete(capital_scheme_financial_table))
            connection.execute(delete(capital_scheme_table))

    def get(self, id_: int) -> Scheme | None:
        with self._engine.connect() as connection:
            result = connection.execute(
                select(capital_scheme_table).where(capital_scheme_table.c.capital_scheme_id == id_)
            )
            row = result.one_or_none()
            scheme = self._capital_scheme_to_domain(row) if row else None

            if scheme:
                result = connection.execute(
                    select(capital_scheme_financial_table).where(
                        capital_scheme_financial_table.c.capital_scheme_id == id_
                    )
                )
                for row in result:
                    scheme.funding.update_financial(self._capital_scheme_financial_to_domain(row))

                result = connection.execute(
                    select(scheme_milestone_table).where(scheme_milestone_table.c.capital_scheme_id == id_)
                )
                for row in result:
                    scheme.milestones.update_milestone(self._scheme_milestone_to_domain(row))

                result = connection.execute(
                    select(scheme_intervention_table).where(scheme_intervention_table.c.capital_scheme_id == id_)
                )
                for row in result:
                    scheme.outputs.update_output(self._scheme_intervention_to_domain(row))

            return scheme

    def get_by_authority(self, authority_id: int) -> list[Scheme]:
        with self._engine.connect() as connection:
            result = connection.execute(
                select(capital_scheme_table)
                .where(capital_scheme_table.c.bid_submitting_authority_id == authority_id)
                .order_by(capital_scheme_table.c.capital_scheme_id)
            )
            schemes = [self._capital_scheme_to_domain(row) for row in result]

            result = connection.execute(
                select(capital_scheme_financial_table)
                .join(capital_scheme_table)
                .where(capital_scheme_table.c.bid_submitting_authority_id == authority_id)
            )
            for row in result:
                scheme = next((scheme for scheme in schemes if scheme.id == row.capital_scheme_id))
                scheme.funding.update_financial(self._capital_scheme_financial_to_domain(row))

            result = connection.execute(
                select(scheme_milestone_table)
                .join(capital_scheme_table)
                .where(capital_scheme_table.c.bid_submitting_authority_id == authority_id)
            )
            for row in result:
                scheme = next((scheme for scheme in schemes if scheme.id == row.capital_scheme_id))
                scheme.milestones.update_milestone(self._scheme_milestone_to_domain(row))

            result = connection.execute(
                select(scheme_intervention_table)
                .join(capital_scheme_table)
                .where(capital_scheme_table.c.bid_submitting_authority_id == authority_id)
            )
            for row in result:
                scheme = next((scheme for scheme in schemes if scheme.id == row.capital_scheme_id))
                scheme.outputs.update_output(self._scheme_intervention_to_domain(row))

            return schemes

    def _capital_scheme_to_domain(self, row: Row[Any]) -> Scheme:
        scheme = Scheme(id_=row.capital_scheme_id, name=row.scheme_name, authority_id=row.bid_submitting_authority_id)
        scheme.type = self._scheme_type_mapper.to_domain(row.scheme_type_id)
        scheme.funding_programme = self._funding_programme_mapper.to_domain(row.funding_programme_id)
        return scheme

    def _capital_scheme_financial_to_domain(self, row: Row[Any]) -> FinancialRevision:
        return FinancialRevision(
            effective=DateRange(row.effective_date_from, row.effective_date_to),
            type=self._financial_type_mapper.to_domain(row.financial_type_id),
            amount=row.amount,
            source=self._data_source_mapper.to_domain(row.data_source_id),
        )

    def _scheme_milestone_to_domain(self, row: Row[Any]) -> MilestoneRevision:
        return MilestoneRevision(
            effective=DateRange(row.effective_date_from, row.effective_date_to),
            milestone=self._milestone_mapper.to_domain(row.milestone_id),
            observation_type=self._observation_type_mapper.to_domain(row.observation_type_id),
            status_date=row.status_date,
        )

    def _scheme_intervention_to_domain(self, row: Row[Any]) -> OutputRevision:
        return OutputRevision(
            effective=DateRange(row.effective_date_from, row.effective_date_to),
            type_measure=self._output_type_measure_mapper.to_domain(row.intervention_type_measure_id),
            value=row.intervention_value,
            observation_type=self._observation_type_mapper.to_domain(row.observation_type_id),
        )


class SchemeTypeMapper:
    _IDS = {
        SchemeType.DEVELOPMENT: 1,
        SchemeType.CONSTRUCTION: 2,
    }

    def to_id(self, type_: SchemeType | None) -> int | None:
        return self._IDS[type_] if type_ else None

    def to_domain(self, id_: int | None) -> SchemeType | None:
        return {value: key for key, value in self._IDS.items()}[id_] if id_ else None


class FundingProgrammeMapper:
    _IDS = {
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
        return self._IDS[funding_programme] if funding_programme else None

    def to_domain(self, id_: int | None) -> FundingProgramme | None:
        return {value: key for key, value in self._IDS.items()}[id_] if id_ else None
