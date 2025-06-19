from datetime import date, datetime
from decimal import Decimal

import pytest

from schemes.domain.authorities import Authority
from schemes.domain.dates import DateRange
from schemes.domain.reporting_window import ReportingWindow
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
from schemes.views.schemes import SchemeRepr
from schemes.views.schemes.data_sources import DataSourceRepr
from schemes.views.schemes.funding import BidStatusRepr, BidStatusRevisionRepr, FinancialRevisionRepr, FinancialTypeRepr
from schemes.views.schemes.milestones import MilestoneContext, MilestoneRepr, MilestoneRevisionRepr
from schemes.views.schemes.observations import ObservationTypeRepr
from schemes.views.schemes.outputs import OutputMeasureRepr, OutputRevisionRepr, OutputTypeRepr
from schemes.views.schemes.overview import FundingProgrammeRepr, OverviewRevisionRepr, SchemeTypeRepr
from schemes.views.schemes.reviews import AuthorityReviewRepr
from schemes.views.schemes.schemes import (
    FundingProgrammeContext,
    SchemeContext,
    SchemeOverviewContext,
    SchemeRowContext,
    SchemesContext,
    SchemeTypeContext,
)
from tests.builders import build_scheme


class TestSchemesContext:
    def test_from_domain(self) -> None:
        authority = Authority(abbreviation="LIV", name="Liverpool City Region Combined Authority")
        schemes = [
            build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_abbreviation="LIV"),
            build_scheme(id_=2, reference="ATE00002", name="School Streets", authority_abbreviation="LIV"),
        ]

        context = SchemesContext.from_domain(datetime.min, dummy_reporting_window(), authority, schemes)

        assert (
            context.authority_name == "Liverpool City Region Combined Authority"
            and context.schemes[0].reference == "ATE00001"
            and context.schemes[1].reference == "ATE00002"
        )

    def test_from_domain_sets_reporting_window_days_left(self) -> None:
        reporting_window = ReportingWindow(DateRange(datetime(2020, 4, 1), datetime(2020, 5, 1)))
        authority = Authority(abbreviation="LIV", name="")
        scheme = build_scheme(id_=1, reference="", name="", authority_abbreviation="LIV")
        scheme.reviews.update_authority_review(
            AuthorityReview(id_=1, review_date=datetime(2020, 1, 2), source=DataSource.ATF4_BID)
        )

        context = SchemesContext.from_domain(datetime(2020, 4, 24, 12), reporting_window, authority, [scheme])

        assert context.reporting_window_days_left == 7

    def test_from_domain_does_not_set_reporting_window_days_left_when_up_to_date(self) -> None:
        reporting_window = ReportingWindow(DateRange(datetime(2020, 4, 1), datetime(2020, 5, 1)))
        authority = Authority(abbreviation="LIV", name="")
        scheme = build_scheme(id_=1, reference="", name="", authority_abbreviation="LIV")
        scheme.reviews.update_authority_review(
            AuthorityReview(id_=1, review_date=datetime(2020, 4, 1), source=DataSource.ATF4_BID)
        )

        context = SchemesContext.from_domain(datetime(2020, 4, 24, 12), reporting_window, authority, [scheme])

        assert context.reporting_window_days_left is None

    def test_from_domain_does_not_set_reporting_window_days_left_when_no_schemes(self) -> None:
        reporting_window = ReportingWindow(DateRange(datetime(2020, 4, 1), datetime(2020, 5, 1)))

        context = SchemesContext.from_domain(
            datetime(2020, 4, 24, 12), reporting_window, Authority(abbreviation="", name=""), []
        )

        assert context.reporting_window_days_left is None

    def test_from_domain_sets_scheme_needs_review(self) -> None:
        reporting_window = ReportingWindow(DateRange(datetime(2020, 4, 1), datetime(2020, 5, 1)))
        authority = Authority(abbreviation="LIV", name="")
        scheme = build_scheme(id_=1, reference="", name="", authority_abbreviation="LIV")
        scheme.reviews.update_authority_review(
            AuthorityReview(id_=1, review_date=datetime(2020, 1, 2), source=DataSource.ATF4_BID)
        )

        context = SchemesContext.from_domain(datetime.min, reporting_window, authority, [scheme])

        assert context.schemes[0].needs_review


class TestSchemeRowContext:
    def test_from_domain(self) -> None:
        scheme = build_scheme(
            id_=1, reference="ATE00001", name="Wirral Package", funding_programme=FundingProgrammes.ATF4
        )

        context = SchemeRowContext.from_domain(dummy_reporting_window(), scheme)

        assert context == SchemeRowContext(
            id=1,
            reference="ATE00001",
            funding_programme=FundingProgrammeContext(name="ATF4"),
            name="Wirral Package",
            needs_review=True,
            last_reviewed=None,
        )

    @pytest.mark.parametrize(
        "review_date, expected_needs_review",
        [
            (datetime(2020, 1, 2), True),
            (datetime(2020, 4, 2), False),
        ],
    )
    def test_from_domain_sets_needs_review(self, review_date: datetime, expected_needs_review: bool) -> None:
        reporting_window = ReportingWindow(DateRange(datetime(2020, 4, 1), datetime(2020, 5, 1)))
        scheme = build_scheme(id_=1, reference="ATE00001", name="Wirral Package")
        scheme.reviews.update_authority_review(
            AuthorityReview(id_=1, review_date=review_date, source=DataSource.ATF4_BID)
        )

        context = SchemeRowContext.from_domain(reporting_window, scheme)

        assert context.needs_review == expected_needs_review

    def test_from_domain_sets_last_reviewed(self) -> None:
        scheme = build_scheme(id_=1, reference="ATE00001", name="Wirral Package")
        scheme.reviews.update_authority_reviews(
            AuthorityReview(id_=1, review_date=datetime(2020, 1, 2, 12), source=DataSource.ATF4_BID),
            AuthorityReview(id_=2, review_date=datetime(2020, 1, 3, 12), source=DataSource.ATF4_BID),
        )

        context = SchemeRowContext.from_domain(dummy_reporting_window(), scheme)

        assert context.last_reviewed == datetime(2020, 1, 3, 12)


@pytest.mark.usefixtures("app")
class TestSchemeContext:
    def test_from_domain(self) -> None:
        authority = Authority(abbreviation="LIV", name="Liverpool City Region Combined Authority")
        scheme = build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_abbreviation="LIV")

        context = SchemeContext.from_domain(dummy_reporting_window(), authority, scheme)

        assert (
            context.id == 1
            and context.authority_name == "Liverpool City Region Combined Authority"
            and context.name == "Wirral Package"
            and context.needs_review
            and context.overview.reference == "ATE00001"
            and not context.review.last_reviewed
        )

    @pytest.mark.parametrize(
        "review_date, expected_needs_review",
        [
            pytest.param(datetime(2023, 1, 2), True, id="review before reporting window"),
            pytest.param(datetime(2023, 4, 1), False, id="review during reporting window"),
        ],
    )
    def test_from_domain_sets_needs_review(self, review_date: datetime, expected_needs_review: bool) -> None:
        reporting_window = ReportingWindow(DateRange(datetime(2023, 4, 1), datetime(2023, 5, 1)))
        authority = Authority(abbreviation="LIV", name="")
        scheme = build_scheme(id_=1, reference="", name="", authority_abbreviation="LIV")
        scheme.reviews.update_authority_review(
            AuthorityReview(id_=1, review_date=review_date, source=DataSource.ATF4_BID)
        )

        context = SchemeContext.from_domain(reporting_window, authority, scheme)

        assert context.needs_review == expected_needs_review

    def test_from_domain_sets_funding(self) -> None:
        authority = Authority(abbreviation="LIV", name="")
        scheme = build_scheme(id_=1, reference="", name="", authority_abbreviation="LIV")
        scheme.funding.update_financial(
            FinancialRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_=FinancialType.FUNDING_ALLOCATION,
                amount=100_000,
                source=DataSource.ATF4_BID,
            )
        )

        context = SchemeContext.from_domain(dummy_reporting_window(), authority, scheme)

        assert context.funding.funding_allocation == 100_000

    def test_from_domain_sets_milestones(self) -> None:
        authority = Authority(abbreviation="LIV", name="")
        scheme = build_scheme(id_=1, reference="", name="", authority_abbreviation="LIV")
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

        context = SchemeContext.from_domain(dummy_reporting_window(), authority, scheme)

        assert context.milestones.milestones[0].planned == date(2020, 2, 1)

    def test_from_domain_sets_outputs(self) -> None:
        authority = Authority(abbreviation="LIV", name="")
        scheme = build_scheme(id_=1, reference="", name="", authority_abbreviation="LIV")
        scheme.outputs.update_outputs(
            OutputRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), datetime(2020, 2, 1)),
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

        context = SchemeContext.from_domain(dummy_reporting_window(), authority, scheme)

        assert context.outputs.outputs[0].planned == Decimal(20)

    def test_from_domain_sets_review(self) -> None:
        authority = Authority(abbreviation="LIV", name="")
        scheme = build_scheme(id_=1, reference="", name="", authority_abbreviation="LIV")
        scheme.reviews.update_authority_review(
            AuthorityReview(id_=1, review_date=datetime(2020, 1, 1), source=DataSource.ATF4_BID)
        )

        context = SchemeContext.from_domain(dummy_reporting_window(), authority, scheme)

        assert context.review.last_reviewed == datetime(2020, 1, 1)


class TestSchemeOverviewContext:
    def test_from_domain_sets_reference(self) -> None:
        scheme = build_scheme(id_=0, reference="ATE00001", name="")

        context = SchemeOverviewContext.from_domain(scheme)

        assert context.reference == "ATE00001"

    def test_from_domain_sets_type(self) -> None:
        scheme = build_scheme(id_=0, reference="", name="", type_=SchemeType.CONSTRUCTION)

        context = SchemeOverviewContext.from_domain(scheme)

        assert context.type == SchemeTypeContext(name="Construction")

    def test_from_domain_sets_funding_programme(self) -> None:
        scheme = build_scheme(id_=0, reference="", name="", funding_programme=FundingProgrammes.ATF4)

        context = SchemeOverviewContext.from_domain(scheme)

        assert context.funding_programme == FundingProgrammeContext(name="ATF4")

    def test_from_domain_sets_current_milestone(self) -> None:
        scheme = build_scheme(id_=0, reference="", name="")
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
        scheme = build_scheme(id_=0, reference="", name="")

        context = SchemeOverviewContext.from_domain(scheme)

        assert context.current_milestone == MilestoneContext(name=None)


class TestSchemeTypeContext:
    @pytest.mark.parametrize(
        "type_, expected_name",
        [(SchemeType.DEVELOPMENT, "Development"), (SchemeType.CONSTRUCTION, "Construction")],
    )
    def test_from_domain(self, type_: SchemeType, expected_name: str) -> None:
        context = SchemeTypeContext.from_domain(type_)

        assert context == SchemeTypeContext(name=expected_name)


class TestFundingProgrammeContext:
    @pytest.mark.parametrize(
        "funding_programme, expected_name",
        [
            (FundingProgrammes.ATF2, "ATF2"),
            (FundingProgrammes.ATF3, "ATF3"),
            (FundingProgrammes.ATF4, "ATF4"),
            (FundingProgrammes.ATF4E, "ATF4e"),
            (FundingProgrammes.ATF5, "ATF5"),
            (FundingProgrammes.CRSTS, "CRSTS"),
            (FundingProgrammes.LUF1, "LUF1"),
            (FundingProgrammes.LUF2, "LUF2"),
            (FundingProgrammes.LUF3, "LUF3"),
            (FundingProgrammes.MRN, "MRN"),
        ],
    )
    def test_from_domain(self, funding_programme: FundingProgramme, expected_name: str) -> None:
        context = FundingProgrammeContext.from_domain(funding_programme)

        assert context == FundingProgrammeContext(name=expected_name)


class TestSchemeRepr:
    def test_from_domain(self) -> None:
        scheme = Scheme(id_=1, reference="ATE00001")

        scheme_repr = SchemeRepr.from_domain(scheme)

        assert scheme_repr == SchemeRepr(id=1, reference="ATE00001")

    def test_from_domain_sets_overview_revisions(self) -> None:
        scheme = build_scheme(
            id_=0,
            reference="",
            overview_revisions=[
                OverviewRevision(
                    id_=1,
                    effective=DateRange(datetime(2020, 1, 1, 12), datetime(2020, 2, 1, 13)),
                    name="Wirral Package",
                    authority_abbreviation="LIV",
                    type_=SchemeType.DEVELOPMENT,
                    funding_programme=FundingProgrammes.ATF3,
                ),
                OverviewRevision(
                    id_=2,
                    effective=DateRange(datetime(2020, 2, 1, 13), None),
                    name="School Streets",
                    authority_abbreviation="WYO",
                    type_=SchemeType.CONSTRUCTION,
                    funding_programme=FundingProgrammes.ATF4,
                ),
            ],
        )

        scheme_repr = SchemeRepr.from_domain(scheme)

        assert scheme_repr.overview_revisions == [
            OverviewRevisionRepr(
                id=1,
                effective_date_from="2020-01-01T12:00:00",
                effective_date_to="2020-02-01T13:00:00",
                name="Wirral Package",
                authority_abbreviation="LIV",
                type=SchemeTypeRepr.DEVELOPMENT,
                funding_programme=FundingProgrammeRepr.ATF3,
            ),
            OverviewRevisionRepr(
                id=2,
                effective_date_from="2020-02-01T13:00:00",
                effective_date_to=None,
                name="School Streets",
                authority_abbreviation="WYO",
                type=SchemeTypeRepr.CONSTRUCTION,
                funding_programme=FundingProgrammeRepr.ATF4,
            ),
        ]

    def test_from_domain_sets_bid_status_revisions(self) -> None:
        scheme = build_scheme(
            id_=0,
            reference="",
            name="",
            bid_status_revisions=[
                BidStatusRevision(
                    id_=2,
                    effective=DateRange(datetime(2020, 1, 1, 12), datetime(2020, 2, 1, 13)),
                    status=BidStatus.SUBMITTED,
                ),
                BidStatusRevision(id_=3, effective=DateRange(datetime(2020, 2, 1, 13), None), status=BidStatus.FUNDED),
            ],
        )

        scheme_repr = SchemeRepr.from_domain(scheme)

        assert scheme_repr.bid_status_revisions == [
            BidStatusRevisionRepr(
                id=2,
                effective_date_from="2020-01-01T12:00:00",
                effective_date_to="2020-02-01T13:00:00",
                status=BidStatusRepr.SUBMITTED,
            ),
            BidStatusRevisionRepr(
                id=3,
                effective_date_from="2020-02-01T13:00:00",
                effective_date_to=None,
                status=BidStatusRepr.FUNDED,
            ),
        ]

    def test_from_domain_sets_financial_revisions(self) -> None:
        scheme = build_scheme(id_=0, reference="", name="")
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
        scheme = build_scheme(id_=0, reference="", name="")
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
        scheme = build_scheme(id_=0, reference="", name="")
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

    def test_from_domain_sets_authority_reviews(self) -> None:
        scheme = build_scheme(id_=0, reference="", name="")
        scheme.reviews.update_authority_reviews(
            AuthorityReview(id_=1, review_date=datetime(2020, 1, 2, 12), source=DataSource.ATF4_BID),
            AuthorityReview(id_=2, review_date=datetime(2020, 1, 3, 12), source=DataSource.PULSE_6),
        )

        scheme_repr = SchemeRepr.from_domain(scheme)

        assert scheme_repr.authority_reviews == [
            AuthorityReviewRepr(
                id=1,
                review_date="2020-01-02T12:00:00",
                source=DataSourceRepr.ATF4_BID,
            ),
            AuthorityReviewRepr(
                id=2,
                review_date="2020-01-03T12:00:00",
                source=DataSourceRepr.PULSE_6,
            ),
        ]

    def test_to_domain(self) -> None:
        scheme_repr = SchemeRepr(id=1, reference="ATE00001")

        scheme = scheme_repr.to_domain()

        assert scheme.id == 1 and scheme.reference == "ATE00001"

    def test_to_domain_sets_overview_revisions(self) -> None:
        scheme_repr = SchemeRepr(
            id=0,
            reference="",
            overview_revisions=[
                OverviewRevisionRepr(
                    id=1,
                    effective_date_from="2020-01-01T12:00:00",
                    effective_date_to="2020-02-01T13:00:00",
                    name="Wirral Package",
                    authority_abbreviation="LIV",
                    type=SchemeTypeRepr.DEVELOPMENT,
                    funding_programme=FundingProgrammeRepr.ATF3,
                ),
                OverviewRevisionRepr(
                    id=2,
                    effective_date_from="2020-02-01T13:00:00",
                    effective_date_to=None,
                    name="School Streets",
                    authority_abbreviation="WYO",
                    type=SchemeTypeRepr.CONSTRUCTION,
                    funding_programme=FundingProgrammeRepr.ATF4,
                ),
            ],
        )

        scheme = scheme_repr.to_domain()

        overview_revision1: OverviewRevision
        overview_revision2: OverviewRevision
        overview_revision1, overview_revision2 = scheme.overview.overview_revisions
        assert (
            overview_revision1.id == 1
            and overview_revision1.effective == DateRange(datetime(2020, 1, 1, 12), datetime(2020, 2, 1, 13))
            and overview_revision1.name == "Wirral Package"
            and overview_revision1.authority_abbreviation == "LIV"
            and overview_revision1.type == SchemeType.DEVELOPMENT
            and overview_revision1.funding_programme == FundingProgrammes.ATF3
        )
        assert (
            overview_revision2.id == 2
            and overview_revision2.effective == DateRange(datetime(2020, 2, 1, 13), None)
            and overview_revision2.name == "School Streets"
            and overview_revision2.authority_abbreviation == "WYO"
            and overview_revision2.type == SchemeType.CONSTRUCTION
            and overview_revision2.funding_programme == FundingProgrammes.ATF4
        )

    def test_to_domain_sets_bid_status_revisions(self) -> None:
        scheme_repr = SchemeRepr(
            id=0,
            reference="",
            bid_status_revisions=[
                BidStatusRevisionRepr(
                    id=2,
                    effective_date_from="2020-01-01T12:00:00",
                    effective_date_to="2020-02-01T13:00:00",
                    status=BidStatusRepr.SUBMITTED,
                ),
                BidStatusRevisionRepr(
                    id=3, effective_date_from="2020-02-01T13:00:00", effective_date_to=None, status=BidStatusRepr.FUNDED
                ),
            ],
        )

        scheme = scheme_repr.to_domain()

        bid_status_revision1: BidStatusRevision
        bid_status_revision2: BidStatusRevision
        bid_status_revision1, bid_status_revision2 = scheme.funding.bid_status_revisions
        assert (
            bid_status_revision1.id == 2
            and bid_status_revision1.effective == DateRange(datetime(2020, 1, 1, 12), datetime(2020, 2, 1, 13))
            and bid_status_revision1.status == BidStatus.SUBMITTED
        )
        assert (
            bid_status_revision2.id == 3
            and bid_status_revision2.effective == DateRange(datetime(2020, 2, 1, 13), None)
            and bid_status_revision2.status == BidStatus.FUNDED
        )

    def test_to_domain_sets_financial_revisions(self) -> None:
        scheme_repr = SchemeRepr(
            id=0,
            reference="",
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

        scheme = scheme_repr.to_domain()

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
            reference="",
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

        scheme = scheme_repr.to_domain()

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
            reference="",
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

        scheme = scheme_repr.to_domain()

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

    def test_to_domain_sets_authority_reviews(self) -> None:
        scheme_repr = SchemeRepr(
            id=0,
            reference="",
            authority_reviews=[
                AuthorityReviewRepr(
                    id=2,
                    review_date="2020-01-01T12:00:00",
                    source=DataSourceRepr.ATF4_BID,
                ),
                AuthorityReviewRepr(
                    id=3,
                    review_date="2020-01-02T12:00:00",
                    source=DataSourceRepr.PULSE_6,
                ),
            ],
        )

        scheme = scheme_repr.to_domain()

        authority_review1: AuthorityReview
        authority_review2: AuthorityReview
        authority_review1, authority_review2 = scheme.reviews.authority_reviews
        assert (
            authority_review1.id == 2
            and authority_review1.review_date == datetime(2020, 1, 1, 12)
            and authority_review1.source == DataSource.ATF4_BID
        )
        assert (
            authority_review2.id == 3
            and authority_review2.review_date == datetime(2020, 1, 2, 12)
            and authority_review2.source == DataSource.PULSE_6
        )


def dummy_reporting_window() -> ReportingWindow:
    return ReportingWindow(DateRange(datetime.min, datetime.min))
