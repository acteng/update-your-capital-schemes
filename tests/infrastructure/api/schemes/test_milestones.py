from datetime import date

import pytest

from schemes.domain.schemes.data_sources import DataSource
from schemes.domain.schemes.milestones import Milestone
from schemes.domain.schemes.observations import ObservationType
from schemes.infrastructure.api.data_sources import DataSourceModel
from schemes.infrastructure.api.observation_types import ObservationTypeModel
from schemes.infrastructure.api.schemes.milestones import CapitalSchemeMilestoneModel, MilestoneModel


class TestMilestoneModel:
    @pytest.mark.parametrize(
        "milestone_model, expected_milestone",
        [
            (MilestoneModel.PUBLIC_CONSULTATION_COMPLETED, Milestone.PUBLIC_CONSULTATION_COMPLETED),
            (MilestoneModel.FEASIBILITY_DESIGN_STARTED, Milestone.FEASIBILITY_DESIGN_STARTED),
            (MilestoneModel.FEASIBILITY_DESIGN_COMPLETED, Milestone.FEASIBILITY_DESIGN_COMPLETED),
            (MilestoneModel.PRELIMINARY_DESIGN_COMPLETED, Milestone.PRELIMINARY_DESIGN_COMPLETED),
            (MilestoneModel.OUTLINE_DESIGN_COMPLETED, Milestone.OUTLINE_DESIGN_COMPLETED),
            (MilestoneModel.DETAILED_DESIGN_COMPLETED, Milestone.DETAILED_DESIGN_COMPLETED),
            (MilestoneModel.CONSTRUCTION_STARTED, Milestone.CONSTRUCTION_STARTED),
            (MilestoneModel.CONSTRUCTION_COMPLETED, Milestone.CONSTRUCTION_COMPLETED),
            (MilestoneModel.FUNDING_COMPLETED, Milestone.FUNDING_COMPLETED),
            (MilestoneModel.NOT_PROGRESSED, Milestone.NOT_PROGRESSED),
            (MilestoneModel.SUPERSEDED, Milestone.SUPERSEDED),
            (MilestoneModel.REMOVED, Milestone.REMOVED),
        ],
    )
    def test_to_domain(self, milestone_model: MilestoneModel, expected_milestone: Milestone) -> None:
        assert milestone_model.to_domain() == expected_milestone


class TestCapitalSchemeMilestoneModel:
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
