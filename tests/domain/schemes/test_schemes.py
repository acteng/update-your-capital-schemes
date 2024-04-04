from datetime import date, datetime

import pytest

from schemes.domain.dates import DateRange
from schemes.domain.schemes import (
    BidStatus,
    BidStatusRevision,
    DataSource,
    Milestone,
    MilestoneRevision,
    ObservationType,
    Scheme,
    SchemeFunding,
    SchemeMilestones,
    SchemeOutputs,
    SchemeReviews,
)


class TestScheme:
    def test_create(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)

        assert (
            scheme.id == 1
            and scheme.name == "Wirral Package"
            and scheme.authority_id == 2
            and scheme.type is None
            and scheme.funding_programme is None
        )

    def test_get_reference(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)

        assert scheme.reference == "ATE00001"

    def test_get_funding(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)

        assert isinstance(scheme.funding, SchemeFunding)

    def test_get_milestones(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)

        assert isinstance(scheme.milestones, SchemeMilestones)

    def test_get_outputs(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)

        assert isinstance(scheme.outputs, SchemeOutputs)

    def test_get_reviews(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)

        assert isinstance(scheme.reviews, SchemeReviews)

    @pytest.mark.parametrize(
        "bid_status, milestone, expected_updateable",
        [
            pytest.param(BidStatus.SUBMITTED, Milestone.PUBLIC_CONSULTATION_COMPLETED, False, id="not funded"),
            pytest.param(BidStatus.FUNDED, Milestone.PUBLIC_CONSULTATION_COMPLETED, True, id="updateable"),
            pytest.param(BidStatus.FUNDED, Milestone.FEASIBILITY_DESIGN_STARTED, True, id="updateable"),
            pytest.param(BidStatus.FUNDED, Milestone.FEASIBILITY_DESIGN_COMPLETED, True, id="updateable"),
            pytest.param(BidStatus.FUNDED, Milestone.PRELIMINARY_DESIGN_COMPLETED, True, id="updateable"),
            pytest.param(BidStatus.FUNDED, Milestone.OUTLINE_DESIGN_COMPLETED, True, id="updateable"),
            pytest.param(BidStatus.FUNDED, Milestone.DETAILED_DESIGN_COMPLETED, True, id="updateable"),
            pytest.param(BidStatus.FUNDED, Milestone.CONSTRUCTION_STARTED, True, id="updateable"),
            pytest.param(BidStatus.FUNDED, Milestone.CONSTRUCTION_COMPLETED, False, id="complete"),
            pytest.param(BidStatus.FUNDED, Milestone.INSPECTION, False, id="complete"),
            pytest.param(BidStatus.FUNDED, Milestone.NOT_PROGRESSED, False, id="inactive"),
            pytest.param(BidStatus.FUNDED, Milestone.SUPERSEDED, False, id="inactive"),
            pytest.param(BidStatus.FUNDED, Milestone.REMOVED, False, id="inactive"),
            pytest.param(BidStatus.NOT_FUNDED, Milestone.PUBLIC_CONSULTATION_COMPLETED, False, id="not funded"),
            pytest.param(BidStatus.SPLIT, Milestone.PUBLIC_CONSULTATION_COMPLETED, False, id="not funded"),
            pytest.param(BidStatus.DELETED, Milestone.PUBLIC_CONSULTATION_COMPLETED, False, id="not funded"),
        ],
    )
    def test_is_updateable(self, bid_status: BidStatus, milestone: Milestone, expected_updateable: bool) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.funding.update_bid_status(
            BidStatusRevision(id_=3, effective=DateRange(datetime(2000, 1, 2), None), status=bid_status)
        )
        scheme.milestones.update_milestone(
            MilestoneRevision(
                id_=4,
                effective=DateRange(datetime(2000, 1, 2), None),
                milestone=milestone,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2000, 1, 2),
                source=DataSource.ATF4_BID,
            )
        )

        assert scheme.is_updateable == expected_updateable

    def test_is_updateable_when_no_milestone_revision(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.funding.update_bid_status(
            BidStatusRevision(id_=3, effective=DateRange(datetime(2000, 1, 2), None), status=BidStatus.FUNDED)
        )

        assert scheme.is_updateable is True

    def test_is_updateable_uses_latest_milestone_revision(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)
        scheme.funding.update_bid_status(
            BidStatusRevision(id_=3, effective=DateRange(datetime(2000, 1, 2), None), status=BidStatus.FUNDED)
        )
        scheme.milestones.update_milestones(
            MilestoneRevision(
                id_=4,
                effective=DateRange(datetime(2000, 1, 1), datetime(2000, 2, 1)),
                milestone=Milestone.CONSTRUCTION_STARTED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2000, 1, 1),
                source=DataSource.ATF4_BID,
            ),
            MilestoneRevision(
                id_=5,
                effective=DateRange(datetime(2000, 2, 1), None),
                milestone=Milestone.CONSTRUCTION_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2000, 2, 1),
                source=DataSource.ATF4_BID,
            ),
        )

        assert scheme.is_updateable is False
