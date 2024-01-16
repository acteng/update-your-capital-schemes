from datetime import date
from decimal import Decimal

import pytest

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

        context = SchemesContext.from_domain(authority, schemes)

        assert (
            context.authority_name == "Liverpool City Region Combined Authority"
            and context.schemes[0].reference == "ATE00001"
            and context.schemes[1].reference == "ATE00002"
        )


class TestSchemesRowContext:
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
                effective=DateRange(date(2020, 1, 1), None),
                type=FinancialType.FUNDING_ALLOCATION,
                amount=100_000,
                source=DataSource.ATF4_BID,
            )
        )
        scheme.milestones.update_milestones(
            MilestoneRevision(
                effective=DateRange(date(2020, 1, 1), date(2020, 1, 31)),
                milestone=Milestone.FEASIBILITY_DESIGN_COMPLETED,
                observation_type=ObservationType.PLANNED,
                status_date=date(2020, 1, 1),
            ),
            MilestoneRevision(
                effective=DateRange(date(2020, 2, 1), None),
                milestone=Milestone.FEASIBILITY_DESIGN_COMPLETED,
                observation_type=ObservationType.PLANNED,
                status_date=date(2020, 2, 1),
            ),
        )
        scheme.outputs.update_outputs(
            OutputRevision(
                effective=DateRange(date(2020, 1, 1), date(2020, 1, 31)),
                type_measure=OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES,
                value=Decimal(10),
                observation_type=ObservationType.PLANNED,
            ),
            OutputRevision(
                effective=DateRange(date(2020, 2, 1), None),
                type_measure=OutputTypeMeasure.RESTRICTION_OR_REDUCTION_OF_CAR_PARKING_AVAILABILITY_NUMBER_OF_PARKING_SPACES,
                value=Decimal(20),
                observation_type=ObservationType.PLANNED,
            ),
        )

        context = SchemeContext.from_domain(authority, scheme)

        assert (
            context.authority_name == "Liverpool City Region Combined Authority"
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
        scheme.milestones.update_milestone(
            MilestoneRevision(
                effective=DateRange(date(2020, 1, 1), None),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 1),
            )
        )

        context = SchemeOverviewContext.from_domain(scheme)

        assert context.current_milestone == MilestoneContext(name="Detailed design completed")

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
                    effective_date_from="2020-01-01",
                    effective_date_to=None,
                    type=FinancialTypeRepr.FUNDING_ALLOCATION,
                    amount=100_000,
                    source=DataSourceRepr.ATF4_BID,
                ),
                FinancialRevisionRepr(
                    effective_date_from="2020-01-01",
                    effective_date_to=None,
                    type=FinancialTypeRepr.EXPECTED_COST,
                    amount=200_000,
                    source=DataSourceRepr.PULSE_6,
                ),
            ],
        )

        scheme = scheme_repr.to_domain(0)

        assert scheme.funding.financial_revisions == [
            FinancialRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type=FinancialType.FUNDING_ALLOCATION,
                amount=100_000,
                source=DataSource.ATF4_BID,
            ),
            FinancialRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type=FinancialType.EXPECTED_COST,
                amount=200_000,
                source=DataSource.PULSE_6,
            ),
        ]

    def test_to_domain_sets_milestone_revisions(self) -> None:
        scheme_repr = SchemeRepr(
            id=0,
            name="",
            milestone_revisions=[
                MilestoneRevisionRepr(
                    effective_date_from="2020-01-01",
                    effective_date_to=None,
                    milestone=MilestoneRepr.DETAILED_DESIGN_COMPLETED,
                    observation_type=ObservationTypeRepr.ACTUAL,
                    status_date="2020-01-01",
                ),
                MilestoneRevisionRepr(
                    effective_date_from="2020-01-01",
                    effective_date_to=None,
                    milestone=MilestoneRepr.CONSTRUCTION_STARTED,
                    observation_type=ObservationTypeRepr.ACTUAL,
                    status_date="2020-02-01",
                ),
            ],
        )

        scheme = scheme_repr.to_domain(0)

        assert scheme.milestones.milestone_revisions == [
            MilestoneRevision(
                effective=DateRange(date(2020, 1, 1), None),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 1),
            ),
            MilestoneRevision(
                effective=DateRange(date(2020, 1, 1), None),
                milestone=Milestone.CONSTRUCTION_STARTED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 2, 1),
            ),
        ]

    def test_to_domain_sets_output_revisions(self) -> None:
        scheme_repr = SchemeRepr(
            id=0,
            name="",
            output_revisions=[
                OutputRevisionRepr(
                    effective_date_from="2020-01-01",
                    effective_date_to=None,
                    type=OutputTypeRepr.IMPROVEMENTS_TO_EXISTING_ROUTE,
                    measure=OutputMeasureRepr.MILES,
                    value="10",
                    observation_type=ObservationTypeRepr.ACTUAL,
                ),
                OutputRevisionRepr(
                    effective_date_from="2020-01-01",
                    effective_date_to=None,
                    type=OutputTypeRepr.IMPROVEMENTS_TO_EXISTING_ROUTE,
                    measure=OutputMeasureRepr.NUMBER_OF_JUNCTIONS,
                    value="3",
                    observation_type=ObservationTypeRepr.ACTUAL,
                ),
            ],
        )

        scheme = scheme_repr.to_domain(0)

        assert scheme.outputs.output_revisions == [
            OutputRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type_measure=OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_MILES,
                value=Decimal(10),
                observation_type=ObservationType.ACTUAL,
            ),
            OutputRevision(
                effective=DateRange(date(2020, 1, 1), None),
                type_measure=OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_NUMBER_OF_JUNCTIONS,
                value=Decimal(3),
                observation_type=ObservationType.ACTUAL,
            ),
        ]


class TestSchemeTypeRepr:
    @pytest.mark.parametrize(
        "type_, expected_type",
        [("development", SchemeType.DEVELOPMENT), ("construction", SchemeType.CONSTRUCTION)],
    )
    def test_to_domain(self, type_: str, expected_type: SchemeType) -> None:
        assert SchemeTypeRepr(type_).to_domain() == expected_type


class TestFundingProgrammeRepr:
    @pytest.mark.parametrize(
        "funding_programme, expected_funding_programme",
        [
            ("ATF2", FundingProgramme.ATF2),
            ("ATF3", FundingProgramme.ATF3),
            ("ATF4", FundingProgramme.ATF4),
            ("ATF4e", FundingProgramme.ATF4E),
            ("ATF5", FundingProgramme.ATF5),
            ("MRN", FundingProgramme.MRN),
            ("LUF", FundingProgramme.LUF),
            ("CRSTS", FundingProgramme.CRSTS),
        ],
    )
    def test_to_domain(self, funding_programme: str, expected_funding_programme: FundingProgramme) -> None:
        assert FundingProgrammeRepr(funding_programme).to_domain() == expected_funding_programme
