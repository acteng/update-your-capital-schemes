from datetime import date, datetime

import pytest

from schemes.domain.dates import DateRange
from schemes.domain.schemes.data_sources import DataSource
from schemes.domain.schemes.funding import BidStatus, SchemeFunding
from schemes.domain.schemes.milestones import Milestone, MilestoneRevision, SchemeMilestones
from schemes.domain.schemes.observations import ObservationType
from schemes.domain.schemes.outputs import SchemeOutputs
from schemes.domain.schemes.overview import FundingProgramme, FundingProgrammes, SchemeOverview, SchemeType
from schemes.domain.schemes.reviews import SchemeReviews
from schemes.domain.schemes.schemes import Scheme
from tests.builders import build_scheme


class TestScheme:
    def test_create(self) -> None:
        scheme = Scheme(id_=1, reference="ATE00001")

        assert scheme.id == 1 and scheme.reference == "ATE00001"

    def test_get_overview(self) -> None:
        scheme = build_scheme(id_=1, reference="ATE00001", name="Wirral Package")

        assert isinstance(scheme.overview, SchemeOverview)

    def test_get_funding(self) -> None:
        scheme = build_scheme(id_=1, reference="ATE00001", name="Wirral Package")

        assert isinstance(scheme.funding, SchemeFunding)

    def test_get_milestones(self) -> None:
        scheme = build_scheme(id_=1, reference="ATE00001", name="Wirral Package")

        assert isinstance(scheme.milestones, SchemeMilestones)

    def test_get_outputs(self) -> None:
        scheme = build_scheme(id_=1, reference="ATE00001", name="Wirral Package")

        assert isinstance(scheme.outputs, SchemeOutputs)

    def test_get_reviews(self) -> None:
        scheme = build_scheme(id_=1, reference="ATE00001", name="Wirral Package")

        assert isinstance(scheme.reviews, SchemeReviews)

    @pytest.mark.parametrize(
        "bid_status, expected_updateable",
        [
            (BidStatus.SUBMITTED, False),
            (BidStatus.FUNDED, True),
            (BidStatus.NOT_FUNDED, False),
            (BidStatus.SPLIT, False),
            (BidStatus.DELETED, False),
        ],
    )
    def test_is_updateable_when_funded(self, bid_status: BidStatus, expected_updateable: bool) -> None:
        scheme = build_scheme(
            id_=1,
            reference="ATE00001",
            name="Wirral Package",
            funding_programme=FundingProgrammes.ATF4,
            bid_status=bid_status,
        )
        scheme.milestones.update_milestone(
            MilestoneRevision(
                id_=3,
                effective=DateRange(datetime(2000, 1, 2), None),
                milestone=Milestone.PUBLIC_CONSULTATION_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2000, 1, 2),
                source=DataSource.ATF4_BID,
            )
        )

        assert scheme.is_updateable == expected_updateable

    @pytest.mark.parametrize(
        "milestone, expected_updateable",
        [
            pytest.param(Milestone.PUBLIC_CONSULTATION_COMPLETED, True, id="active and incomplete"),
            pytest.param(Milestone.FUNDING_COMPLETED, False, id="complete"),
            pytest.param(Milestone.NOT_PROGRESSED, False, id="inactive"),
        ],
    )
    def test_is_updateable_when_active_and_incomplete(self, milestone: Milestone, expected_updateable: bool) -> None:
        scheme = build_scheme(
            id_=1,
            reference="ATE00001",
            name="Wirral Package",
            funding_programme=FundingProgrammes.ATF4,
            bid_status=BidStatus.FUNDED,
        )
        scheme.milestones.update_milestone(
            MilestoneRevision(
                id_=3,
                effective=DateRange(datetime(2000, 1, 2), None),
                milestone=milestone,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2000, 1, 2),
                source=DataSource.ATF4_BID,
            )
        )

        assert scheme.is_updateable == expected_updateable

    @pytest.mark.parametrize(
        "funding_programme, expected_updateable",
        [
            (FundingProgrammes.ATF4, True),
            (FundingProgramme("ATF100", True, False), False),
        ],
    )
    def test_is_updateable_when_not_under_embargo(
        self, funding_programme: FundingProgramme, expected_updateable: bool
    ) -> None:
        scheme = build_scheme(
            id_=1,
            reference="ATE00001",
            name="Wirral Package",
            funding_programme=funding_programme,
            bid_status=BidStatus.FUNDED,
        )
        scheme.milestones.update_milestone(
            MilestoneRevision(
                id_=3,
                effective=DateRange(datetime(2000, 1, 2), None),
                milestone=Milestone.PUBLIC_CONSULTATION_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2000, 1, 2),
                source=DataSource.ATF4_BID,
            )
        )

        assert scheme.is_updateable == expected_updateable

    @pytest.mark.parametrize(
        "funding_programme, expected_updateable",
        [
            (FundingProgrammes.ATF4, True),
            (FundingProgramme("ATF100", False, False), False),
        ],
    )
    def test_is_updateable_when_eligible_for_authority_update(
        self, funding_programme: FundingProgramme, expected_updateable: bool
    ) -> None:
        scheme = build_scheme(
            id_=1,
            reference="ATE00001",
            name="Wirral Package",
            funding_programme=funding_programme,
            bid_status=BidStatus.FUNDED,
        )
        scheme.milestones.update_milestone(
            MilestoneRevision(
                id_=3,
                effective=DateRange(datetime(2000, 1, 2), None),
                milestone=Milestone.PUBLIC_CONSULTATION_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2000, 1, 2),
                source=DataSource.ATF4_BID,
            )
        )

        assert scheme.is_updateable == expected_updateable

    def test_is_updateable_when_no_bid_status_revision(self) -> None:
        scheme = build_scheme(
            id_=1,
            reference="ATE00001",
            name="Wirral Package",
            funding_programme=FundingProgrammes.ATF4,
            bid_status_revisions=[],
        )
        scheme.milestones.update_milestone(
            MilestoneRevision(
                id_=3,
                effective=DateRange(datetime(2000, 1, 2), None),
                milestone=Milestone.PUBLIC_CONSULTATION_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2000, 1, 2),
                source=DataSource.ATF4_BID,
            )
        )

        assert scheme.is_updateable is False

    def test_is_updateable_when_no_milestone_revision(self) -> None:
        scheme = build_scheme(
            id_=1,
            reference="ATE00001",
            name="Wirral Package",
            funding_programme=FundingProgrammes.ATF4,
            bid_status=BidStatus.FUNDED,
        )

        assert scheme.is_updateable is True

    def test_is_updateable_uses_latest_milestone_revision(self) -> None:
        scheme = build_scheme(
            id_=1,
            reference="ATE00001",
            name="Wirral Package",
            funding_programme=FundingProgrammes.ATF4,
            bid_status=BidStatus.FUNDED,
        )
        scheme.milestones.update_milestones(
            MilestoneRevision(
                id_=3,
                effective=DateRange(datetime(2000, 1, 1), datetime(2000, 2, 1)),
                milestone=Milestone.CONSTRUCTION_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2000, 1, 1),
                source=DataSource.ATF4_BID,
            ),
            MilestoneRevision(
                id_=4,
                effective=DateRange(datetime(2000, 2, 1), None),
                milestone=Milestone.FUNDING_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2000, 2, 1),
                source=DataSource.ATF4_BID,
            ),
        )

        assert scheme.is_updateable is False

    def test_is_updateable_when_no_overview_revision(self) -> None:
        scheme = build_scheme(id_=1, reference="ATE00001", bid_status=BidStatus.FUNDED, overview_revisions=[])

        assert scheme.is_updateable is True

    def test_milestones_eligible_for_authority_update_when_development(self) -> None:
        scheme = build_scheme(id_=1, reference="ATE00001", name="Wirral Package", type_=SchemeType.DEVELOPMENT)

        assert scheme.milestones_eligible_for_authority_update == {
            Milestone.FEASIBILITY_DESIGN_COMPLETED,
            Milestone.PRELIMINARY_DESIGN_COMPLETED,
            Milestone.DETAILED_DESIGN_COMPLETED,
        }

    def test_milestones_eligible_for_authority_update_when_construction(self) -> None:
        scheme = build_scheme(id_=1, reference="ATE00001", name="Wirral Package", type_=SchemeType.CONSTRUCTION)

        assert scheme.milestones_eligible_for_authority_update == {
            Milestone.FEASIBILITY_DESIGN_COMPLETED,
            Milestone.PRELIMINARY_DESIGN_COMPLETED,
            Milestone.DETAILED_DESIGN_COMPLETED,
            Milestone.CONSTRUCTION_STARTED,
            Milestone.CONSTRUCTION_COMPLETED,
        }


class TestFundingProgrammes:
    @pytest.mark.parametrize(
        "funding_programme, expected_code",
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
        ],
    )
    def test_code(self, funding_programme: FundingProgramme, expected_code: str) -> None:
        assert funding_programme.code == expected_code

    @pytest.mark.parametrize(
        "funding_programme, expected_is_under_embargo",
        [
            (FundingProgrammes.ATF2, False),
            (FundingProgrammes.ATF3, False),
            (FundingProgrammes.ATF4, False),
            (FundingProgrammes.ATF4E, False),
            (FundingProgrammes.ATF5, False),
            (FundingProgrammes.CATF, False),
            (FundingProgrammes.CRSTS, False),
            (FundingProgrammes.IST, False),
            (FundingProgrammes.LUF1, False),
            (FundingProgrammes.LUF2, False),
            (FundingProgrammes.LUF3, False),
            (FundingProgrammes.MRN, False),
        ],
    )
    def test_is_under_embargo(self, funding_programme: FundingProgramme, expected_is_under_embargo: bool) -> None:
        assert funding_programme.is_under_embargo == expected_is_under_embargo

    @pytest.mark.parametrize(
        "funding_programme, expected_is_eligible_for_authority_update",
        [
            (FundingProgrammes.ATF2, True),
            (FundingProgrammes.ATF3, True),
            (FundingProgrammes.ATF4, True),
            (FundingProgrammes.ATF4E, True),
            (FundingProgrammes.ATF5, True),
            (FundingProgrammes.CATF, True),
            (FundingProgrammes.CRSTS, False),
            (FundingProgrammes.IST, True),
            (FundingProgrammes.LUF1, False),
            (FundingProgrammes.LUF2, False),
            (FundingProgrammes.LUF3, False),
            (FundingProgrammes.MRN, False),
        ],
    )
    def test_is_eligible_for_authority_update(
        self, funding_programme: FundingProgramme, expected_is_eligible_for_authority_update: bool
    ) -> None:
        assert funding_programme.is_eligible_for_authority_update == expected_is_eligible_for_authority_update
