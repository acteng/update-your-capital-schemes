from datetime import date, datetime

import pytest

from schemes.domain.dates import DateRange
from schemes.domain.schemes.data_sources import DataSource
from schemes.domain.schemes.milestones import Milestone, MilestoneRevision
from schemes.domain.schemes.observations import ObservationType
from schemes.infrastructure.api.data_sources import DataSourceModel
from schemes.infrastructure.api.observation_types import ObservationTypeModel
from schemes.infrastructure.api.schemes.milestones import CapitalSchemeMilestoneModel, MilestoneModel


@pytest.mark.parametrize(
    "milestone, milestone_model",
    [
        (Milestone.PUBLIC_CONSULTATION_COMPLETED, MilestoneModel.PUBLIC_CONSULTATION_COMPLETED),
        (Milestone.FEASIBILITY_DESIGN_STARTED, MilestoneModel.FEASIBILITY_DESIGN_STARTED),
        (Milestone.FEASIBILITY_DESIGN_COMPLETED, MilestoneModel.FEASIBILITY_DESIGN_COMPLETED),
        (Milestone.PRELIMINARY_DESIGN_COMPLETED, MilestoneModel.PRELIMINARY_DESIGN_COMPLETED),
        (Milestone.OUTLINE_DESIGN_COMPLETED, MilestoneModel.OUTLINE_DESIGN_COMPLETED),
        (Milestone.DETAILED_DESIGN_COMPLETED, MilestoneModel.DETAILED_DESIGN_COMPLETED),
        (Milestone.CONSTRUCTION_STARTED, MilestoneModel.CONSTRUCTION_STARTED),
        (Milestone.CONSTRUCTION_COMPLETED, MilestoneModel.CONSTRUCTION_COMPLETED),
        (Milestone.FUNDING_COMPLETED, MilestoneModel.FUNDING_COMPLETED),
        (Milestone.NOT_PROGRESSED, MilestoneModel.NOT_PROGRESSED),
        (Milestone.SUPERSEDED, MilestoneModel.SUPERSEDED),
        (Milestone.REMOVED, MilestoneModel.REMOVED),
    ],
)
class TestMilestoneModel:
    def test_from_domain(self, milestone: Milestone, milestone_model: MilestoneModel) -> None:
        assert MilestoneModel.from_domain(milestone) == milestone_model

    def test_to_domain(self, milestone: Milestone, milestone_model: MilestoneModel) -> None:
        assert milestone_model.to_domain() == milestone


class TestCapitalSchemeMilestoneModel:
    def test_from_domain(self) -> None:
        milestone_revision = MilestoneRevision(
            id_=1,
            effective=DateRange(datetime(2020, 1, 1), datetime(2020, 2, 1)),
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.PLANNED,
            status_date=date(2020, 2, 1),
            source=DataSource.ATF4_BID,
        )

        milestone_model = CapitalSchemeMilestoneModel.from_domain(milestone_revision)

        assert milestone_model == CapitalSchemeMilestoneModel(
            milestone=MilestoneModel.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationTypeModel.PLANNED,
            status_date=date(2020, 2, 1),
            source=DataSourceModel.ATF4_BID,
        )

    def test_to_domain(self) -> None:
        milestone_model = CapitalSchemeMilestoneModel(
            milestone=MilestoneModel.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationTypeModel.PLANNED,
            status_date=date(2020, 2, 1),
            source=DataSourceModel.ATF4_BID,
        )

        milestone_revision = milestone_model.to_domain()

        assert (
            milestone_revision.id is not None
            and milestone_revision.milestone == Milestone.DETAILED_DESIGN_COMPLETED
            and milestone_revision.observation_type == ObservationType.PLANNED
            and milestone_revision.status_date == date(2020, 2, 1)
            and milestone_revision.source == DataSource.ATF4_BID
        )
