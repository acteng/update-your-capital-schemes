from datetime import date

import pytest
from sqlalchemy import Engine, MetaData, func, insert, select

from schemes.authorities.domain import Authority
from schemes.authorities.services import DatabaseAuthorityRepository
from schemes.authorities.services import add_tables as authorities_add_tables
from schemes.schemes.domain import (
    FundingProgramme,
    Milestone,
    MilestoneRevision,
    ObservationType,
    Scheme,
    SchemeType,
)
from schemes.schemes.services import (
    DatabaseSchemeRepository,
    FundingProgrammeMapper,
    MilestoneMapper,
    ObservationTypeMapper,
    SchemeTypeMapper,
)
from schemes.schemes.services import add_tables as schemes_add_tables


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

    def test_add_schemes_milestone_revisions(
        self, schemes: DatabaseSchemeRepository, engine: Engine, metadata: MetaData
    ) -> None:
        scheme1 = Scheme(id_=1, name="Wirral Package", authority_id=1)
        scheme1.update_milestone(
            MilestoneRevision(
                effective_date_from=date(2020, 1, 1),
                effective_date_to=date(2020, 1, 31),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.PLANNED,
                status_date=date(2020, 2, 1),
            )
        )
        scheme1.update_milestone(
            MilestoneRevision(
                effective_date_from=date(2020, 2, 1),
                effective_date_to=None,
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.PLANNED,
                status_date=date(2020, 3, 1),
            )
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

        actual = schemes.get(1)

        assert (
            actual
            and actual.id == 1
            and actual.name == "Wirral Package"
            and actual.authority_id == 1
            and actual.type == SchemeType.DEVELOPMENT
            and actual.funding_programme == FundingProgramme.ATF3
        )

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

        actual = schemes.get(1)

        assert actual
        milestone_revision1: MilestoneRevision
        milestone_revision2: MilestoneRevision
        milestone_revision1, milestone_revision2 = actual.milestone_revisions
        assert (
            milestone_revision1.effective_date_from == date(2020, 1, 1)
            and milestone_revision1.effective_date_to == date(2020, 1, 31)
            and milestone_revision1.milestone == Milestone.DETAILED_DESIGN_COMPLETED
            and milestone_revision1.observation_type == ObservationType.PLANNED
            and milestone_revision1.status_date == date(2020, 2, 1)
        )
        assert (
            milestone_revision2.effective_date_from == date(2020, 2, 1)
            and milestone_revision2.effective_date_to is None
            and milestone_revision2.milestone == Milestone.DETAILED_DESIGN_COMPLETED
            and milestone_revision2.observation_type == ObservationType.PLANNED
            and milestone_revision2.status_date == date(2020, 3, 1)
        )

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

        actual1: Scheme
        actual2: Scheme
        actual1, actual2 = schemes.get_by_authority(1)

        assert (
            actual1.id == 1
            and actual1.name == "Wirral Package"
            and actual1.authority_id == 1
            and actual1.type == SchemeType.DEVELOPMENT
            and actual1.funding_programme == FundingProgramme.ATF3
        )
        assert actual2.id == 2 and actual2.name == "School Streets" and actual1.authority_id == 1

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
                    capital_scheme_id=2, scheme_name="School Streets", bid_submitting_authority_id=2
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

        actual1: Scheme
        (actual1,) = schemes.get_by_authority(1)

        assert actual1.id == 1
        milestone_revision1: MilestoneRevision
        (milestone_revision1,) = actual1.milestone_revisions
        assert (
            milestone_revision1.effective_date_from == date(2020, 1, 1)
            and milestone_revision1.effective_date_to is None
            and milestone_revision1.milestone == Milestone.DETAILED_DESIGN_COMPLETED
            and milestone_revision1.observation_type == ObservationType.PLANNED
            and milestone_revision1.status_date == date(2020, 2, 1)
        )

    def test_get_all_schemes_milestone_revisions_by_authority_has_correct_order(
        self, schemes: DatabaseSchemeRepository, engine: Engine, metadata: MetaData
    ) -> None:
        with engine.begin() as connection:
            connection.execute(
                insert(metadata.tables["capital_scheme"]).values(
                    capital_scheme_id=1, scheme_name="Wirral Package", bid_submitting_authority_id=1
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
                    effective_date_from=date(2020, 1, 1),
                    effective_date_to=None,
                    milestone_id=5,
                    observation_type_id=1,
                    status_date=date(2020, 2, 1),
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
                insert(metadata.tables["capital_scheme"]).values(
                    capital_scheme_id=3, scheme_name="School Streets", bid_submitting_authority_id=2
                )
            )
            connection.execute(
                insert(metadata.tables["scheme_milestone"]).values(
                    capital_scheme_id=3,
                    effective_date_from=date(2020, 2, 1),
                    effective_date_to=None,
                    milestone_id=5,
                    observation_type_id=1,
                    status_date=date(2020, 3, 1),
                )
            )

        actual1: Scheme
        actual2: Scheme
        (actual1, actual2) = schemes.get_by_authority(1)

        assert actual1.id == 1
        milestone_revision1: MilestoneRevision
        milestone_revision2: MilestoneRevision
        (milestone_revision1,) = actual1.milestone_revisions
        (milestone_revision2,) = actual2.milestone_revisions
        assert (
            milestone_revision1.effective_date_from == date(2020, 1, 1)
            and milestone_revision1.effective_date_to == date(2020, 1, 31)
            and milestone_revision1.milestone == Milestone.DETAILED_DESIGN_COMPLETED
            and milestone_revision1.observation_type == ObservationType.PLANNED
            and milestone_revision1.status_date == date(2020, 2, 1)
        )
        assert (
            milestone_revision2.effective_date_from == date(2020, 1, 1)
            and milestone_revision2.effective_date_to is None
            and milestone_revision2.milestone == Milestone.DETAILED_DESIGN_COMPLETED
            and milestone_revision2.observation_type == ObservationType.PLANNED
            and milestone_revision2.status_date == date(2020, 2, 1)
        )

    def test_get_all_schemes(self, schemes: DatabaseSchemeRepository, engine: Engine, metadata: MetaData) -> None:
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

        actual1: Scheme
        actual2: Scheme
        actual1, actual2 = schemes.get_all()

        assert (
            actual1.id == 1
            and actual1.name == "Wirral Package"
            and actual1.authority_id == 1
            and actual1.type == SchemeType.DEVELOPMENT
            and actual1.funding_programme == FundingProgramme.ATF3
        )
        assert actual2.id == 2 and actual2.name == "School Streets" and actual1.authority_id == 1

    def test_get_all_schemes_milestone_revisions(
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

        actual1: Scheme
        actual2: Scheme
        actual1, actual2 = schemes.get_all()

        assert actual1.id == 1
        milestone_revision1: MilestoneRevision
        (milestone_revision1,) = actual1.milestone_revisions
        assert (
            milestone_revision1.effective_date_from == date(2020, 1, 1)
            and milestone_revision1.effective_date_to is None
            and milestone_revision1.milestone == Milestone.DETAILED_DESIGN_COMPLETED
            and milestone_revision1.observation_type == ObservationType.PLANNED
            and milestone_revision1.status_date == date(2020, 2, 1)
        )
        assert actual2.id == 2
        milestone_revision2: MilestoneRevision
        (milestone_revision2,) = actual2.milestone_revisions
        assert (
            milestone_revision2.effective_date_from == date(2020, 2, 1)
            and milestone_revision2.effective_date_to is None
            and milestone_revision2.milestone == Milestone.DETAILED_DESIGN_COMPLETED
            and milestone_revision2.observation_type == ObservationType.PLANNED
            and milestone_revision2.status_date == date(2020, 3, 1)
        )

    def test_clear_all_schemes(self, schemes: DatabaseSchemeRepository, engine: Engine, metadata: MetaData) -> None:
        capital_scheme_table = metadata.tables["capital_scheme"]
        with engine.begin() as connection:
            connection.execute(
                insert(capital_scheme_table).values(
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
                insert(capital_scheme_table).values(
                    capital_scheme_id=2, scheme_name="School Streets", bid_submitting_authority_id=1
                )
            )

        schemes.clear()

        with engine.connect() as connection:
            # pylint:disable=not-callable
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


class TestMilestoneMapper:
    @pytest.mark.parametrize(
        "milestone, id_",
        [
            (Milestone.PUBLIC_CONSULTATION_COMPLETED, 1),
            (Milestone.FEASIBILITY_DESIGN_COMPLETED, 2),
            (Milestone.PRELIMINARY_DESIGN_COMPLETED, 3),
            (Milestone.OUTLINE_DESIGN_COMPLETED, 4),
            (Milestone.DETAILED_DESIGN_COMPLETED, 5),
            (Milestone.CONSTRUCTION_STARTED, 6),
            (Milestone.CONSTRUCTION_COMPLETED, 7),
            (Milestone.INSPECTION, 8),
            (Milestone.NOT_PROGRESSED, 9),
            (Milestone.SUPERSEDED, 10),
            (Milestone.REMOVED, 11),
        ],
    )
    def test_mapper(self, milestone: Milestone, id_: int) -> None:
        mapper = MilestoneMapper()
        assert mapper.to_id(milestone) == id_ and mapper.to_domain(id_) == milestone


class TestObservationTypeMapper:
    @pytest.mark.parametrize("observation_type, id_", [(ObservationType.PLANNED, 1), (ObservationType.ACTUAL, 2)])
    def test_mapper(self, observation_type: ObservationType, id_: int) -> None:
        mapper = ObservationTypeMapper()
        assert mapper.to_id(observation_type) == id_ and mapper.to_domain(id_) == observation_type
