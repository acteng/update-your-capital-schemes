from datetime import date

import pytest

from schemes.schemes.domain import (
    FundingProgramme,
    Milestone,
    MilestoneRevision,
    ObservationType,
    Scheme,
    SchemeType,
)
from schemes.schemes.views import (
    MilestoneRevisionRepr,
    SchemeContext,
    SchemeOverviewContext,
    SchemeRepr,
)


class TestSchemeContext:
    def test_create_from_domain(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)

        context = SchemeContext.for_domain(scheme)

        assert context == SchemeContext(
            reference="ATE00001", name="Wirral Package", overview=SchemeOverviewContext.for_domain(scheme)
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

    @pytest.mark.parametrize(
        "funding_programme, expected_funding_programme",
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
    def test_set_funding_programme(
        self, funding_programme: FundingProgramme | None, expected_funding_programme: str | None
    ) -> None:
        scheme = Scheme(id_=0, name="", authority_id=0)
        scheme.funding_programme = funding_programme

        context = SchemeOverviewContext.for_domain(scheme)

        assert context.funding_programme == expected_funding_programme

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
