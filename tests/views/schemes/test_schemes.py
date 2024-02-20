from datetime import date, datetime
from decimal import Decimal

import pytest

from schemes.domain.authorities import Authority
from schemes.domain.reporting_window import ReportingWindow
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
from schemes.views.schemes import SchemeRepr
from schemes.views.schemes.funding import (
    DataSourceRepr,
    FinancialRevisionRepr,
    FinancialTypeRepr,
)
from schemes.views.schemes.milestones import (
    MilestoneContext,
    MilestoneRepr,
    MilestoneRevisionRepr,
)
from schemes.views.schemes.observations import ObservationTypeRepr
from schemes.views.schemes.outputs import (
    OutputMeasureRepr,
    OutputRevisionRepr,
    OutputTypeRepr,
)
from schemes.views.schemes.schemes import (
    FundingProgrammeContext,
    FundingProgrammeRepr,
    SchemeContext,
    SchemeOverviewContext,
    SchemeRowContext,
    SchemesContext,
    SchemeTypeContext,
    SchemeTypeRepr,
)


class TestSchemesContext:
    def test_from_domain(self) -> None:
        authority = Authority(id_=1, name="Liverpool City Region Combined Authority")
        schemes = [
            Scheme(id_=1, name="Wirral Package", authority_id=1),
            Scheme(id_=2, name="School Streets", authority_id=1),
        ]

        context = SchemesContext.from_domain(datetime(1970, 1, 1), None, authority, schemes)

        assert (
            context.reporting_window_days_left is None
            and context.authority_name == "Liverpool City Region Combined Authority"
            and context.schemes[0].reference == "ATE00001"
            and context.schemes[1].reference == "ATE00002"
        )

    def test_from_domain_sets_reporting_window_days_left(self) -> None:
        reporting_window = ReportingWindow(DateRange(datetime(2020, 4, 1), datetime(2020, 5, 1)))

        context = SchemesContext.from_domain(datetime(2020, 4, 24, 12), reporting_window, Authority(id_=0, name=""), [])

        assert context.reporting_window_days_left == 7


class TestSchemeRowContext:
    def test_from_domain(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=1)
        scheme.funding_programme = FundingProgramme.ATF4

        context = SchemeRowContext.from_domain(scheme)

        assert context == SchemeRowContext(
            id=1,
            reference="ATE00001",
            funding_programme=FundingProgrammeContext(name="ATF4"),
            name="Wirral Package",
        )


class TestSchemeContext:
    def test_from_domain(self) -> None:
        authority = Authority(id_=2, name="Liverpool City Region Combined Authority")
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.funding.update_financial(
            FinancialRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_=FinancialType.FUNDING_ALLOCATION,
                amount=100_000,
                source=DataSource.ATF4_BID,
            )
        )
        scheme.milestones.update_milestones(
            MilestoneRevision(
                id_=1,
                effective=DateRange(datetime(2020, 2, 1), None),
                milestone=Milestone.FEASIBILITY_DESIGN_COMPLETED,
                observation_type=ObservationType.PLANNED,
                status_date=date(2020, 2, 1),
                source=DataSource.ATF4_BID,
            ),
        )
        scheme.outputs.update_outputs(
            OutputRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), datetime(2020, 1, 31)),
                type_measure=OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES,
                value=Decimal(10),
                observation_type=ObservationType.PLANNED,
            ),
            OutputRevision(
                id_=2,
                effective=DateRange(datetime(2020, 2, 1), None),
                type_measure=OutputTypeMeasure.RESTRICTION_OR_REDUCTION_OF_CAR_PARKING_AVAILABILITY_NUMBER_OF_PARKING_SPACES,
                value=Decimal(20),
                observation_type=ObservationType.PLANNED,
            ),
        )

        context = SchemeContext.from_domain(authority, scheme)

        assert (
            context.id == 1
            and context.authority_name == "Liverpool City Region Combined Authority"
            and context.name == "Wirral Package"
            and context.overview.reference == "ATE00001"
            and context.funding.funding_allocation == 100_000
            and context.milestones.milestones[0].planned == date(2020, 2, 1)
            and context.outputs.outputs[0].planned == Decimal(20)
        )


class TestSchemeOverviewContext:
    def test_from_domain_sets_reference(self) -> None:
        scheme = Scheme(id_=1, name="", authority_id=0)

        context = SchemeOverviewContext.from_domain(scheme)

        assert context.reference == "ATE00001"

    def test_from_domain_sets_type(self) -> None:
        scheme = Scheme(id_=0, name="", authority_id=0)
        scheme.type = SchemeType.CONSTRUCTION

        context = SchemeOverviewContext.from_domain(scheme)

        assert context.type == SchemeTypeContext(name="Construction")

    def test_from_domain_sets_funding_programme(self) -> None:
        scheme = Scheme(id_=0, name="", authority_id=0)
        scheme.funding_programme = FundingProgramme.ATF4

        context = SchemeOverviewContext.from_domain(scheme)

        assert context.funding_programme == FundingProgrammeContext(name="ATF4")

    def test_from_domain_sets_current_milestone(self) -> None:
        scheme = Scheme(id_=0, name="", authority_id=0)
        scheme.milestones.update_milestones(
            MilestoneRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 1),
                source=DataSource.ATF4_BID,
            ),
            MilestoneRevision(
                id_=2,
                effective=DateRange(datetime(2020, 1, 1), None),
                milestone=Milestone.CONSTRUCTION_STARTED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 1),
                source=DataSource.ATF4_BID,
            ),
        )

        context = SchemeOverviewContext.from_domain(scheme)

        assert context.current_milestone == MilestoneContext(name="Construction started")

    def test_from_domain_sets_current_milestone_when_no_revisions(self) -> None:
        scheme = Scheme(id_=0, name="", authority_id=0)

        context = SchemeOverviewContext.from_domain(scheme)

        assert context.current_milestone == MilestoneContext(name=None)


class TestSchemeTypeContext:
    @pytest.mark.parametrize(
        "type_, expected_name",
        [(SchemeType.DEVELOPMENT, "Development"), (SchemeType.CONSTRUCTION, "Construction"), (None, None)],
    )
    def test_from_domain(self, type_: SchemeType | None, expected_name: str | None) -> None:
        context = SchemeTypeContext.from_domain(type_)

        assert context == SchemeTypeContext(name=expected_name)


class TestFundingProgrammeContext:
    @pytest.mark.parametrize(
        "funding_programme, expected_name",
        [
            (FundingProgramme.ATF2, "ATF2"),
            (FundingProgramme.ATF3, "ATF3"),
            (FundingProgramme.ATF4, "ATF4"),
            (FundingProgramme.ATF4E, "ATF4e"),
            (FundingProgramme.ATF5, "ATF5"),
            (FundingProgramme.MRN, "MRN"),
            (FundingProgramme.LUF, "LUF"),
            (FundingProgramme.CRSTS, "CRSTS"),
            (None, None),
        ],
    )
    def test_from_domain(self, funding_programme: FundingProgramme | None, expected_name: str | None) -> None:
        context = FundingProgrammeContext.from_domain(funding_programme)

        assert context == FundingProgrammeContext(name=expected_name)


class TestSchemeRepr:
    def test_from_domain(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.type = SchemeType.CONSTRUCTION
        scheme.funding_programme = FundingProgramme.ATF4

        scheme_repr = SchemeRepr.from_domain(scheme)

        assert scheme_repr == SchemeRepr(
            id=1, name="Wirral Package", type=SchemeTypeRepr.CONSTRUCTION, funding_programme=FundingProgrammeRepr.ATF4
        )

    def test_from_domain_when_minimal(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)

        scheme_repr = SchemeRepr.from_domain(scheme)

        assert scheme_repr == SchemeRepr(id=1, name="Wirral Package", type=None, funding_programme=None)

    def test_from_domain_sets_financial_revisions(self) -> None:
        scheme = Scheme(id_=0, name="", authority_id=0)
        scheme.funding.update_financials(
            FinancialRevision(
                id_=2,
                effective=DateRange(datetime(2020, 1, 1, 12), None),
                type_=FinancialType.FUNDING_ALLOCATION,
                amount=100_000,
                source=DataSource.ATF4_BID,
            ),
            FinancialRevision(
                id_=3,
                effective=DateRange(datetime(2020, 1, 1, 12), None),
                type_=FinancialType.EXPECTED_COST,
                amount=200_000,
                source=DataSource.PULSE_6,
            ),
        )

        scheme_repr = SchemeRepr.from_domain(scheme)

        assert scheme_repr.financial_revisions == [
            FinancialRevisionRepr(
                id=2,
                effective_date_from="2020-01-01T12:00:00",
                effective_date_to=None,
                type=FinancialTypeRepr.FUNDING_ALLOCATION,
                amount=100_000,
                source=DataSourceRepr.ATF4_BID,
            ),
            FinancialRevisionRepr(
                id=3,
                effective_date_from="2020-01-01T12:00:00",
                effective_date_to=None,
                type=FinancialTypeRepr.EXPECTED_COST,
                amount=200_000,
                source=DataSourceRepr.PULSE_6,
            ),
        ]

    def test_from_domain_sets_milestone_revisions(self) -> None:
        scheme = Scheme(id_=0, name="", authority_id=0)
        scheme.milestones.update_milestones(
            MilestoneRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1, 12), None),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 1),
                source=DataSource.ATF4_BID,
            ),
            MilestoneRevision(
                id_=2,
                effective=DateRange(datetime(2020, 1, 1, 12), None),
                milestone=Milestone.CONSTRUCTION_STARTED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 2, 1),
                source=DataSource.ATF4_BID,
            ),
        )

        scheme_repr = SchemeRepr.from_domain(scheme)

        assert scheme_repr.milestone_revisions == [
            MilestoneRevisionRepr(
                id=1,
                effective_date_from="2020-01-01T12:00:00",
                effective_date_to=None,
                milestone=MilestoneRepr.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationTypeRepr.ACTUAL,
                status_date="2020-01-01",
                source=DataSourceRepr.ATF4_BID,
            ),
            MilestoneRevisionRepr(
                id=2,
                effective_date_from="2020-01-01T12:00:00",
                effective_date_to=None,
                milestone=MilestoneRepr.CONSTRUCTION_STARTED,
                observation_type=ObservationTypeRepr.ACTUAL,
                status_date="2020-02-01",
                source=DataSourceRepr.ATF4_BID,
            ),
        ]

    def test_from_domain_sets_output_revisions(self) -> None:
        scheme = Scheme(id_=0, name="", authority_id=0)
        scheme.outputs.update_outputs(
            OutputRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1, 12), None),
                type_measure=OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES,
                value=Decimal(10),
                observation_type=ObservationType.ACTUAL,
            ),
            OutputRevision(
                id_=2,
                effective=DateRange(datetime(2020, 1, 1, 12), None),
                type_measure=OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_NUMBER_OF_JUNCTIONS,
                value=Decimal(3),
                observation_type=ObservationType.ACTUAL,
            ),
        )

        scheme_repr = SchemeRepr.from_domain(scheme)

        assert scheme_repr.output_revisions == [
            OutputRevisionRepr(
                id=1,
                effective_date_from="2020-01-01T12:00:00",
                effective_date_to=None,
                type=OutputTypeRepr.IMPROVEMENTS_TO_EXISTING_ROUTE,
                measure=OutputMeasureRepr.MILES,
                value="10",
                observation_type=ObservationTypeRepr.ACTUAL,
            ),
            OutputRevisionRepr(
                id=2,
                effective_date_from="2020-01-01T12:00:00",
                effective_date_to=None,
                type=OutputTypeRepr.IMPROVEMENTS_TO_EXISTING_ROUTE,
                measure=OutputMeasureRepr.NUMBER_OF_JUNCTIONS,
                value="3",
                observation_type=ObservationTypeRepr.ACTUAL,
            ),
        ]

    def test_to_domain(self) -> None:
        scheme_repr = SchemeRepr(
            id=1, name="Wirral Package", type=SchemeTypeRepr.CONSTRUCTION, funding_programme=FundingProgrammeRepr.ATF4
        )

        scheme = scheme_repr.to_domain(2)

        assert (
            scheme.id == 1
            and scheme.name == "Wirral Package"
            and scheme.authority_id == 2
            and scheme.type == SchemeType.CONSTRUCTION
            and scheme.funding_programme == FundingProgramme.ATF4
        )

    def test_to_domain_when_minimal(self) -> None:
        scheme_repr = SchemeRepr(id=1, name="Wirral Package")

        scheme = scheme_repr.to_domain(2)

        assert (
            scheme.id == 1
            and scheme.name == "Wirral Package"
            and scheme.authority_id == 2
            and scheme.type is None
            and scheme.funding_programme is None
        )

    def test_to_domain_sets_financial_revisions(self) -> None:
        scheme_repr = SchemeRepr(
            id=0,
            name="",
            financial_revisions=[
                FinancialRevisionRepr(
                    id=2,
                    effective_date_from="2020-01-01T12:00:00",
                    effective_date_to=None,
                    type=FinancialTypeRepr.FUNDING_ALLOCATION,
                    amount=100_000,
                    source=DataSourceRepr.ATF4_BID,
                ),
                FinancialRevisionRepr(
                    id=3,
                    effective_date_from="2020-01-01T12:00:00",
                    effective_date_to=None,
                    type=FinancialTypeRepr.EXPECTED_COST,
                    amount=200_000,
                    source=DataSourceRepr.PULSE_6,
                ),
            ],
        )

        scheme = scheme_repr.to_domain(0)

        financial_revision1: FinancialRevision
        financial_revision2: FinancialRevision
        financial_revision1, financial_revision2 = scheme.funding.financial_revisions
        assert (
            financial_revision1.id == 2
            and financial_revision1.effective == DateRange(datetime(2020, 1, 1, 12), None)
            and financial_revision1.type == FinancialType.FUNDING_ALLOCATION
            and financial_revision1.amount == 100_000
            and financial_revision1.source == DataSource.ATF4_BID
        )
        assert (
            financial_revision2.id == 3
            and financial_revision2.effective == DateRange(datetime(2020, 1, 1, 12), None)
            and financial_revision2.type == FinancialType.EXPECTED_COST
            and financial_revision2.amount == 200_000
            and financial_revision2.source == DataSource.PULSE_6
        )

    def test_to_domain_sets_milestone_revisions(self) -> None:
        scheme_repr = SchemeRepr(
            id=0,
            name="",
            milestone_revisions=[
                MilestoneRevisionRepr(
                    id=1,
                    effective_date_from="2020-01-01T12:00:00",
                    effective_date_to=None,
                    milestone=MilestoneRepr.DETAILED_DESIGN_COMPLETED,
                    observation_type=ObservationTypeRepr.ACTUAL,
                    status_date="2020-01-01",
                    source=DataSourceRepr.ATF4_BID,
                ),
                MilestoneRevisionRepr(
                    id=2,
                    effective_date_from="2020-01-01T12:00:00",
                    effective_date_to=None,
                    milestone=MilestoneRepr.CONSTRUCTION_STARTED,
                    observation_type=ObservationTypeRepr.ACTUAL,
                    status_date="2020-02-01",
                    source=DataSourceRepr.ATF4_BID,
                ),
            ],
        )

        scheme = scheme_repr.to_domain(0)

        milestone_revision1: MilestoneRevision
        milestone_revision2: MilestoneRevision
        milestone_revision1, milestone_revision2 = scheme.milestones.milestone_revisions
        assert (
            milestone_revision1.id == 1
            and milestone_revision1.effective == DateRange(datetime(2020, 1, 1, 12), None)
            and milestone_revision1.milestone == Milestone.DETAILED_DESIGN_COMPLETED
            and milestone_revision1.observation_type == ObservationType.ACTUAL
            and milestone_revision1.status_date == date(2020, 1, 1)
            and milestone_revision1.source == DataSource.ATF4_BID
        )
        assert (
            milestone_revision2.id == 2
            and milestone_revision2.effective == DateRange(datetime(2020, 1, 1, 12), None)
            and milestone_revision2.milestone == Milestone.CONSTRUCTION_STARTED
            and milestone_revision2.observation_type == ObservationType.ACTUAL
            and milestone_revision2.status_date == date(2020, 2, 1)
            and milestone_revision2.source == DataSource.ATF4_BID
        )

    def test_to_domain_sets_output_revisions(self) -> None:
        scheme_repr = SchemeRepr(
            id=0,
            name="",
            output_revisions=[
                OutputRevisionRepr(
                    id=1,
                    effective_date_from="2020-01-01T12:00:00",
                    effective_date_to=None,
                    type=OutputTypeRepr.IMPROVEMENTS_TO_EXISTING_ROUTE,
                    measure=OutputMeasureRepr.MILES,
                    value="10",
                    observation_type=ObservationTypeRepr.ACTUAL,
                ),
                OutputRevisionRepr(
                    id=2,
                    effective_date_from="2020-01-01T12:00:00",
                    effective_date_to=None,
                    type=OutputTypeRepr.IMPROVEMENTS_TO_EXISTING_ROUTE,
                    measure=OutputMeasureRepr.NUMBER_OF_JUNCTIONS,
                    value="3",
                    observation_type=ObservationTypeRepr.ACTUAL,
                ),
            ],
        )

        scheme = scheme_repr.to_domain(0)

        output_revision1: OutputRevision
        output_revision2: OutputRevision
        output_revision1, output_revision2 = scheme.outputs.output_revisions
        assert (
            output_revision1.id == 1
            and output_revision1.effective == DateRange(datetime(2020, 1, 1, 12), None)
            and output_revision1.type_measure == OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES
            and output_revision1.value == Decimal(10)
            and output_revision1.observation_type == ObservationType.ACTUAL
        )
        assert (
            output_revision2.id == 2
            and output_revision2.effective == DateRange(datetime(2020, 1, 1, 12), None)
            and output_revision2.type_measure == OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_NUMBER_OF_JUNCTIONS
            and output_revision2.value == Decimal(3)
            and output_revision2.observation_type == ObservationType.ACTUAL
        )


@pytest.mark.parametrize(
    "type_, type_repr",
    [(SchemeType.DEVELOPMENT, "development"), (SchemeType.CONSTRUCTION, "construction")],
)
class TestSchemeTypeRepr:
    def test_from_domain(self, type_: SchemeType, type_repr: str) -> None:
        assert SchemeTypeRepr.from_domain(type_).value == type_repr

    def test_to_domain(self, type_: SchemeType, type_repr: str) -> None:
        assert SchemeTypeRepr(type_repr).to_domain() == type_


@pytest.mark.parametrize(
    "funding_programme, funding_programme_repr",
    [
        (FundingProgramme.ATF2, "ATF2"),
        (FundingProgramme.ATF3, "ATF3"),
        (FundingProgramme.ATF4, "ATF4"),
        (FundingProgramme.ATF4E, "ATF4e"),
        (FundingProgramme.ATF5, "ATF5"),
        (FundingProgramme.MRN, "MRN"),
        (FundingProgramme.LUF, "LUF"),
        (FundingProgramme.CRSTS, "CRSTS"),
    ],
)
class TestFundingProgrammeRepr:
    def test_from_domain(self, funding_programme: FundingProgramme, funding_programme_repr: str) -> None:
        assert FundingProgrammeRepr.from_domain(funding_programme).value == funding_programme_repr

    def test_to_domain(self, funding_programme: FundingProgramme, funding_programme_repr: str) -> None:
        assert FundingProgrammeRepr(funding_programme_repr).to_domain() == funding_programme
