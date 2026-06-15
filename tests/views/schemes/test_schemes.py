from datetime import date, datetime
from decimal import Decimal

import pytest

from schemes.domain.authorities import Authority
from schemes.domain.dates import DateRange
from schemes.domain.reporting_window import ReportingWindow
from schemes.domain.schemes.data_sources import DataSource
from schemes.domain.schemes.funding import FinancialRevision, FinancialType
from schemes.domain.schemes.milestones import Milestone, MilestoneRevision
from schemes.domain.schemes.observations import ObservationType
from schemes.domain.schemes.outputs import OutputRevision, OutputTypeMeasure
from schemes.domain.schemes.overview import FundingProgramme, FundingProgrammes, SchemeType
from schemes.domain.schemes.reviews import AuthorityReview
from schemes.views.schemes.milestones import MilestoneContext
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
            context.reference == "ATE00001"
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
            (FundingProgrammes.CATF, "CATF"),
            (FundingProgrammes.CRSTS, "CRSTS"),
            (FundingProgrammes.IST, "IST"),
            (FundingProgrammes.LUF1, "LUF1"),
            (FundingProgrammes.LUF2, "LUF2"),
            (FundingProgrammes.LUF3, "LUF3"),
            (FundingProgrammes.MRN, "MRN"),
            (FundingProgrammes.OTH, "OTH"),
            (FundingProgrammes.CON, "CON"),
        ],
    )
    def test_from_domain(self, funding_programme: FundingProgramme, expected_name: str) -> None:
        context = FundingProgrammeContext.from_domain(funding_programme)

        assert context == FundingProgrammeContext(name=expected_name)


def dummy_reporting_window() -> ReportingWindow:
    return ReportingWindow(DateRange(datetime.min, datetime.min))
