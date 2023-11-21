from datetime import date
from decimal import Decimal

import pytest

from schemes.authorities.domain import Authority
from schemes.schemes.domain import (
    DataSource,
    FinancialRevision,
    FinancialType,
    FundingProgramme,
    Milestone,
    MilestoneRevision,
    ObservationType,
    Scheme,
    SchemeType,
)
from schemes.schemes.views import (
    FinancialRevisionRepr,
    FundingProgrammeContext,
    MilestoneRevisionRepr,
    SchemeContext,
    SchemeFundingContext,
    SchemeOverviewContext,
    SchemeRepr,
    SchemeRowContext,
    SchemesContext,
)


class TestSchemesContext:
    def test_create_from_domain(self) -> None:
        authority = Authority(id_=1, name="Liverpool City Region Combined Authority")
        schemes = [
            Scheme(id_=1, name="Wirral Package", authority_id=1),
            Scheme(id_=2, name="School Streets", authority_id=1),
        ]

        context = SchemesContext.for_domain(authority, schemes)

        assert context == SchemesContext(
            authority_name="Liverpool City Region Combined Authority",
            schemes=[
                SchemeRowContext.for_domain(Scheme(id_=1, name="Wirral Package", authority_id=1)),
                SchemeRowContext.for_domain(Scheme(id_=2, name="School Streets", authority_id=1)),
            ],
        )


class TestSchemesRowContext:
    def test_create_from_domain(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=1)
        scheme.funding_programme = FundingProgramme.ATF4

        context = SchemeRowContext.for_domain(scheme)

        assert context == SchemeRowContext(
            id=1,
            reference="ATE00001",
            funding_programme=FundingProgrammeContext.for_domain(FundingProgramme.ATF4),
            name="Wirral Package",
        )


class TestSchemeContext:
    def test_create_from_domain(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)

        context = SchemeContext.for_domain(scheme)

        assert context == SchemeContext(
            reference="ATE00001",
            name="Wirral Package",
            overview=SchemeOverviewContext.for_domain(scheme),
            funding=SchemeFundingContext.for_domain(scheme),
        )


class TestSchemeOverviewContext:
    @pytest.mark.parametrize(
        "type_, expected_type",
        [(SchemeType.DEVELOPMENT, "Development"), (SchemeType.CONSTRUCTION, "Construction"), (None, None)],
    )
    def test_set_type(self, type_: SchemeType | None, expected_type: str | None) -> None:
        scheme = Scheme(id_=0, name="", authority_id=0)
        scheme.type = type_

        context = SchemeOverviewContext.for_domain(scheme)

        assert context.type == expected_type

    def test_set_funding_programme(self) -> None:
        scheme = Scheme(id_=0, name="", authority_id=0)
        scheme.funding_programme = FundingProgramme.ATF4

        context = SchemeOverviewContext.for_domain(scheme)

        assert context.funding_programme == FundingProgrammeContext.for_domain(FundingProgramme.ATF4)

    @pytest.mark.parametrize(
        "milestone, expected_milestone",
        [
            (Milestone.PUBLIC_CONSULTATION_COMPLETED, "Public consultation completed"),
            (Milestone.FEASIBILITY_DESIGN_COMPLETED, "Feasibility design completed"),
            (Milestone.PRELIMINARY_DESIGN_COMPLETED, "Preliminary design completed"),
            (Milestone.OUTLINE_DESIGN_COMPLETED, "Outline design completed"),
            (Milestone.DETAILED_DESIGN_COMPLETED, "Detailed design completed"),
            (Milestone.CONSTRUCTION_STARTED, "Construction started"),
            (Milestone.CONSTRUCTION_COMPLETED, "Construction completed"),
            (Milestone.INSPECTION, "Inspection"),
            (Milestone.NOT_PROGRESSED, "Not progressed"),
            (Milestone.SUPERSEDED, "Superseded"),
            (Milestone.REMOVED, "Removed"),
        ],
    )
    def test_set_current_milestone(self, milestone: Milestone, expected_milestone: str) -> None:
        scheme = Scheme(id_=0, name="", authority_id=0)
        scheme.update_milestone(
            MilestoneRevision(
                effective_date_from=date(2020, 1, 1),
                effective_date_to=None,
                milestone=milestone,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 1),
            )
        )

        context = SchemeOverviewContext.for_domain(scheme)

        assert context.current_milestone == expected_milestone

    def test_set_current_milestone_when_no_revisions(self) -> None:
        scheme = Scheme(id_=0, name="", authority_id=0)

        context = SchemeOverviewContext.for_domain(scheme)

        assert context.current_milestone is None


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
    def test_set_name(self, funding_programme: FundingProgramme | None, expected_name: str | None) -> None:
        context = FundingProgrammeContext.for_domain(funding_programme)

        assert context.name == expected_name


class TestSchemeFundingContext:
    def test_set_funding_allocation(self) -> None:
        scheme = Scheme(id_=0, name="", authority_id=0)
        scheme.update_financial(
            FinancialRevision(
                effective_date_from=date(2020, 1, 1),
                effective_date_to=None,
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Decimal("100000"),
                source=DataSource.ATF4_BID,
            )
        )

        context = SchemeFundingContext.for_domain(scheme)

        assert context.funding_allocation == Decimal("100000")

    def test_set_spend_to_date(self) -> None:
        scheme = Scheme(id_=0, name="", authority_id=0)
        scheme.update_financial(
            FinancialRevision(
                effective_date_from=date(2020, 1, 1),
                effective_date_to=None,
                type=FinancialType.SPENT_TO_DATE,
                amount=Decimal("50000"),
                source=DataSource.ATF4_BID,
            )
        )

        context = SchemeFundingContext.for_domain(scheme)

        assert context.spend_to_date == Decimal("50000")

    def test_set_change_control_adjustment(self) -> None:
        scheme = Scheme(id_=0, name="", authority_id=0)
        scheme.update_financial(
            FinancialRevision(
                effective_date_from=date(2020, 1, 1),
                effective_date_to=None,
                type=FinancialType.CHANGE_CONTROL_FUNDING_REALLOCATION,
                amount=Decimal("10000"),
                source=DataSource.CHANGE_CONTROL,
            )
        )

        context = SchemeFundingContext.for_domain(scheme)

        assert context.change_control_adjustment == Decimal("10000")

    def test_set_allocation_still_to_spend(self) -> None:
        scheme = Scheme(id_=0, name="", authority_id=0)
        scheme.update_financial(
            FinancialRevision(
                effective_date_from=date(2020, 1, 1),
                effective_date_to=None,
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Decimal("110000"),
                source=DataSource.ATF4_BID,
            )
        )
        scheme.update_financial(
            FinancialRevision(
                effective_date_from=date(2020, 1, 1),
                effective_date_to=None,
                type=FinancialType.SPENT_TO_DATE,
                amount=Decimal("50000"),
                source=DataSource.ATF4_BID,
            )
        )

        context = SchemeFundingContext.for_domain(scheme)

        assert context.allocation_still_to_spend == Decimal("60000")


class TestSchemeRepr:
    def test_create_domain(self) -> None:
        scheme_repr = SchemeRepr(id=1, name="Wirral Package")

        scheme = scheme_repr.to_domain(2)

        assert scheme.id == 1 and scheme.name == "Wirral Package" and scheme.authority_id == 2

    @pytest.mark.parametrize(
        "type_, expected_type",
        [("development", SchemeType.DEVELOPMENT), ("construction", SchemeType.CONSTRUCTION), (None, None)],
    )
    def test_set_type(self, type_: str | None, expected_type: SchemeType | None) -> None:
        scheme_repr = SchemeRepr(id=0, name="", type=type_)

        scheme = scheme_repr.to_domain(0)

        assert scheme.type == expected_type

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
            (None, None),
        ],
    )
    def test_set_funding_programme(
        self, funding_programme: str | None, expected_funding_programme: FundingProgramme | None
    ) -> None:
        scheme_repr = SchemeRepr(id=0, name="", funding_programme=funding_programme)

        scheme = scheme_repr.to_domain(0)

        assert scheme.funding_programme == expected_funding_programme

    def test_set_milestone_revisions(self) -> None:
        scheme_repr = SchemeRepr(
            id=0,
            name="",
            milestone_revisions=[
                MilestoneRevisionRepr(
                    effective_date_from="2020-01-01",
                    effective_date_to=None,
                    milestone="detailed design completed",
                    observation_type="Actual",
                    status_date="2020-01-01",
                ),
                MilestoneRevisionRepr(
                    effective_date_from="2020-01-01",
                    effective_date_to=None,
                    milestone="construction started",
                    observation_type="Actual",
                    status_date="2020-02-01",
                ),
            ],
        )

        scheme = scheme_repr.to_domain(0)

        assert scheme.milestone_revisions == [
            MilestoneRevision(
                effective_date_from=date(2020, 1, 1),
                effective_date_to=None,
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 1, 1),
            ),
            MilestoneRevision(
                effective_date_from=date(2020, 1, 1),
                effective_date_to=None,
                milestone=Milestone.CONSTRUCTION_STARTED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 2, 1),
            ),
        ]

    def test_set_financial_revisions(self) -> None:
        scheme_repr = SchemeRepr(
            id=0,
            name="",
            financial_revisions=[
                FinancialRevisionRepr(
                    effective_date_from="2020-01-01",
                    effective_date_to=None,
                    type="funding allocation",
                    amount="100000",
                    source="ATF4 Bid",
                ),
                FinancialRevisionRepr(
                    effective_date_from="2020-01-01",
                    effective_date_to=None,
                    type="expected cost",
                    amount="200000",
                    source="Pulse 6",
                ),
            ],
        )

        scheme = scheme_repr.to_domain(0)

        assert scheme.financial_revisions == [
            FinancialRevision(
                effective_date_from=date(2020, 1, 1),
                effective_date_to=None,
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Decimal("100000"),
                source=DataSource.ATF4_BID,
            ),
            FinancialRevision(
                effective_date_from=date(2020, 1, 1),
                effective_date_to=None,
                type=FinancialType.EXPECTED_COST,
                amount=Decimal("200000"),
                source=DataSource.PULSE_6,
            ),
        ]


class TestMilestoneRevisionRepr:
    def test_create_domain(self) -> None:
        milestone_revision_repr = MilestoneRevisionRepr(
            effective_date_from="2020-01-01",
            effective_date_to="2020-01-31",
            milestone="detailed design completed",
            observation_type="Actual",
            status_date="2020-01-01",
        )

        milestone_revision = milestone_revision_repr.to_domain()

        assert milestone_revision == MilestoneRevision(
            effective_date_from=date(2020, 1, 1),
            effective_date_to=date(2020, 1, 31),
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 1, 1),
        )

    def test_set_effective_date_to_when_missing(self) -> None:
        milestone_revision_repr = MilestoneRevisionRepr(
            effective_date_from="2020-01-01",
            effective_date_to=None,
            milestone="detailed design completed",
            observation_type="Actual",
            status_date="2020-01-01",
        )

        milestone_revision = milestone_revision_repr.to_domain()

        assert milestone_revision.effective_date_to is None

    @pytest.mark.parametrize(
        "milestone, expected_milestone",
        [
            ("public consultation completed", Milestone.PUBLIC_CONSULTATION_COMPLETED),
            ("feasibility design completed", Milestone.FEASIBILITY_DESIGN_COMPLETED),
            ("preliminary design completed", Milestone.PRELIMINARY_DESIGN_COMPLETED),
            ("outline design completed", Milestone.OUTLINE_DESIGN_COMPLETED),
            ("detailed design completed", Milestone.DETAILED_DESIGN_COMPLETED),
            ("construction started", Milestone.CONSTRUCTION_STARTED),
            ("construction completed", Milestone.CONSTRUCTION_COMPLETED),
            ("inspection", Milestone.INSPECTION),
            ("not progressed", Milestone.NOT_PROGRESSED),
            ("superseded", Milestone.SUPERSEDED),
            ("removed", Milestone.REMOVED),
        ],
    )
    def test_set_milestone(self, milestone: str, expected_milestone: Milestone) -> None:
        milestone_revision_repr = MilestoneRevisionRepr(
            effective_date_from="2020-01-01",
            effective_date_to="2020-01-31",
            milestone=milestone,
            observation_type="Actual",
            status_date="2020-01-01",
        )

        milestone_revision = milestone_revision_repr.to_domain()

        assert milestone_revision.milestone == expected_milestone

    @pytest.mark.parametrize(
        "observation_type, expected_observation_type",
        [
            ("Planned", ObservationType.PLANNED),
            ("Actual", ObservationType.ACTUAL),
        ],
    )
    def test_set_observation_type(self, observation_type: str, expected_observation_type: ObservationType) -> None:
        milestone_revision_repr = MilestoneRevisionRepr(
            effective_date_from="2020-01-01",
            effective_date_to="2020-01-31",
            milestone="detailed design completed",
            observation_type=observation_type,
            status_date="2020-01-01",
        )

        milestone_revision = milestone_revision_repr.to_domain()

        assert milestone_revision.observation_type == expected_observation_type


class TestFinancialRevisionRepr:
    def test_create_domain(self) -> None:
        financial_revision_repr = FinancialRevisionRepr(
            effective_date_from="2020-01-01",
            effective_date_to="2020-01-31",
            type="funding allocation",
            amount="100000",
            source="ATF4 Bid",
        )

        financial_revision = financial_revision_repr.to_domain()

        assert financial_revision == FinancialRevision(
            effective_date_from=date(2020, 1, 1),
            effective_date_to=date(2020, 1, 31),
            type=FinancialType.FUNDING_ALLOCATION,
            amount=Decimal("100000"),
            source=DataSource.ATF4_BID,
        )

    def test_set_effective_date_to_when_missing(self) -> None:
        financial_revision_repr = FinancialRevisionRepr(
            effective_date_from="2020-01-01",
            effective_date_to=None,
            type="funding allocation",
            amount="100000",
            source="ATF4 Bid",
        )

        financial_revision = financial_revision_repr.to_domain()

        assert financial_revision.effective_date_to is None

    @pytest.mark.parametrize(
        "financial_type, expected_financial_type",
        [
            ("expected cost", FinancialType.EXPECTED_COST),
            ("actual cost", FinancialType.ACTUAL_COST),
            ("funding allocation", FinancialType.FUNDING_ALLOCATION),
            ("change control funding reallocation", FinancialType.CHANGE_CONTROL_FUNDING_REALLOCATION),
            ("spent to date", FinancialType.SPENT_TO_DATE),
            ("funding request", FinancialType.FUNDING_REQUEST),
        ],
    )
    def test_set_financial_type(self, financial_type: str, expected_financial_type: FinancialType) -> None:
        financial_revision_repr = FinancialRevisionRepr(
            effective_date_from="2020-01-01",
            effective_date_to="2020-01-31",
            type=financial_type,
            amount="100000",
            source="ATF4 Bid",
        )

        financial_revision = financial_revision_repr.to_domain()

        assert financial_revision.type == expected_financial_type

    @pytest.mark.parametrize(
        "data_source, expected_data_source",
        [
            ("Pulse 5", DataSource.PULSE_5),
            ("Pulse 6", DataSource.PULSE_6),
            ("ATF4 Bid", DataSource.ATF4_BID),
            ("ATF3 Bid", DataSource.ATF3_BID),
            ("Inspectorate review", DataSource.INSPECTORATE_REVIEW),
            ("Regional Engagement Manager review", DataSource.REGIONAL_ENGAGEMENT_MANAGER_REVIEW),
            ("ATE published data", DataSource.ATE_PUBLISHED_DATA),
            ("change control", DataSource.CHANGE_CONTROL),
            ("ATF4e Bid", DataSource.ATF4E_BID),
            ("Pulse 2023/24 Q2", DataSource.PULSE_2023_24_Q2),
            ("Initial Scheme List", DataSource.INITIAL_SCHEME_LIST),
        ],
    )
    def test_set_data_source(self, data_source: str, expected_data_source: DataSource) -> None:
        financial_revision_repr = FinancialRevisionRepr(
            effective_date_from="2020-01-01",
            effective_date_to="2020-01-31",
            type="funding allocation",
            amount="100000",
            source=data_source,
        )

        financial_revision = financial_revision_repr.to_domain()

        assert financial_revision.source == expected_data_source
