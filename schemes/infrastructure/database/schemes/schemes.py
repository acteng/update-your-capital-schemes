import inject
from sqlalchemy import Engine, delete, select
from sqlalchemy.orm import Session, selectinload

from schemes.dicts import inverse_dict
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
from schemes.infrastructure.database import (
    CapitalSchemeEntity,
    CapitalSchemeFinancialEntity,
    SchemeInterventionEntity,
    SchemeMilestoneEntity,
)
from schemes.infrastructure.database.schemes.funding import (
    DataSourceMapper,
    FinancialTypeMapper,
)
from schemes.infrastructure.database.schemes.milestones import MilestoneMapper
from schemes.infrastructure.database.schemes.observations import ObservationTypeMapper
from schemes.infrastructure.database.schemes.outputs import OutputTypeMeasureMapper


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
        with Session(self._engine) as session:
            session.add_all(self._capital_scheme_from_domain(scheme) for scheme in schemes)
            session.commit()

    def clear(self) -> None:
        with Session(self._engine) as session:
            session.execute(delete(SchemeInterventionEntity))
            session.execute(delete(SchemeMilestoneEntity))
            session.execute(delete(CapitalSchemeFinancialEntity))
            session.execute(delete(CapitalSchemeEntity))
            session.commit()

    def get(self, id_: int) -> Scheme | None:
        with Session(self._engine) as session:
            result = session.scalars(
                select(CapitalSchemeEntity)
                .options(selectinload("*"))
                .where(CapitalSchemeEntity.capital_scheme_id == id_)
            )
            row = result.one_or_none()
            return self._capital_scheme_to_domain(row) if row else None

    def get_by_authority(self, authority_id: int) -> list[Scheme]:
        with Session(self._engine) as session:
            result = session.scalars(
                select(CapitalSchemeEntity)
                .options(selectinload("*"))
                .where(CapitalSchemeEntity.bid_submitting_authority_id == authority_id)
                .order_by(CapitalSchemeEntity.capital_scheme_id)
            )
            return [self._capital_scheme_to_domain(row) for row in result]

    def update(self, scheme: Scheme) -> None:
        with Session(self._engine) as session:
            session.merge(self._capital_scheme_from_domain(scheme))
            session.commit()

    def _capital_scheme_from_domain(self, scheme: Scheme) -> CapitalSchemeEntity:
        return CapitalSchemeEntity(
            capital_scheme_id=scheme.id,
            scheme_name=scheme.name,
            bid_submitting_authority_id=scheme.authority_id,
            scheme_type_id=self._scheme_type_mapper.to_id(scheme.type),
            funding_programme_id=self._funding_programme_mapper.to_id(scheme.funding_programme),
            capital_scheme_financials=[
                self._capital_scheme_financial_from_domain(financial_revision)
                for financial_revision in scheme.funding.financial_revisions
            ],
            scheme_milestones=[
                self._scheme_milestone_from_domain(milestone_revision)
                for milestone_revision in scheme.milestones.milestone_revisions
            ],
            scheme_interventions=[
                self._scheme_intervention_from_domain(output_revision)
                for output_revision in scheme.outputs.output_revisions
            ],
        )

    def _capital_scheme_to_domain(self, capital_scheme: CapitalSchemeEntity) -> Scheme:
        scheme = Scheme(
            id_=capital_scheme.capital_scheme_id,
            name=capital_scheme.scheme_name,
            authority_id=capital_scheme.bid_submitting_authority_id,
        )
        scheme.type = self._scheme_type_mapper.to_domain(capital_scheme.scheme_type_id)
        scheme.funding_programme = self._funding_programme_mapper.to_domain(capital_scheme.funding_programme_id)

        for capital_scheme_financial in capital_scheme.capital_scheme_financials:
            scheme.funding.update_financial(self._capital_scheme_financial_to_domain(capital_scheme_financial))

        for scheme_milestone in capital_scheme.scheme_milestones:
            scheme.milestones.update_milestone(self._scheme_milestone_to_domain(scheme_milestone))

        for scheme_intervention in capital_scheme.scheme_interventions:
            scheme.outputs.update_output(self._scheme_intervention_to_domain(scheme_intervention))

        return scheme

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

    def _scheme_milestone_from_domain(self, milestone_revision: MilestoneRevision) -> SchemeMilestoneEntity:
        return SchemeMilestoneEntity(
            scheme_milestone_id=milestone_revision.id,
            effective_date_from=milestone_revision.effective.date_from,
            effective_date_to=milestone_revision.effective.date_to,
            milestone_id=self._milestone_mapper.to_id(milestone_revision.milestone),
            observation_type_id=self._observation_type_mapper.to_id(milestone_revision.observation_type),
            status_date=milestone_revision.status_date,
        )

    def _scheme_milestone_to_domain(self, scheme_milestone: SchemeMilestoneEntity) -> MilestoneRevision:
        return MilestoneRevision(
            id_=scheme_milestone.scheme_milestone_id,
            effective=DateRange(scheme_milestone.effective_date_from, scheme_milestone.effective_date_to),
            milestone=self._milestone_mapper.to_domain(scheme_milestone.milestone_id),
            observation_type=self._observation_type_mapper.to_domain(scheme_milestone.observation_type_id),
            status_date=scheme_milestone.status_date,
        )

    def _scheme_intervention_from_domain(self, output_revision: OutputRevision) -> SchemeInterventionEntity:
        return SchemeInterventionEntity(
            scheme_intervention_id=output_revision.id,
            effective_date_from=output_revision.effective.date_from,
            effective_date_to=output_revision.effective.date_to,
            intervention_type_measure_id=self._output_type_measure_mapper.to_id(output_revision.type_measure),
            intervention_value=output_revision.value,
            observation_type_id=self._observation_type_mapper.to_id(output_revision.observation_type),
        )

    def _scheme_intervention_to_domain(self, scheme_intervention: SchemeInterventionEntity) -> OutputRevision:
        return OutputRevision(
            id_=scheme_intervention.scheme_intervention_id,
            effective=DateRange(scheme_intervention.effective_date_from, scheme_intervention.effective_date_to),
            type_measure=self._output_type_measure_mapper.to_domain(scheme_intervention.intervention_type_measure_id),
            value=scheme_intervention.intervention_value,
            observation_type=self._observation_type_mapper.to_domain(scheme_intervention.observation_type_id),
        )


class SchemeTypeMapper:
    _IDS = {
        SchemeType.DEVELOPMENT: 1,
        SchemeType.CONSTRUCTION: 2,
    }

    def to_id(self, type_: SchemeType | None) -> int | None:
        return self._IDS[type_] if type_ else None

    def to_domain(self, id_: int | None) -> SchemeType | None:
        return inverse_dict(self._IDS)[id_] if id_ else None


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
        return inverse_dict(self._IDS)[id_] if id_ else None