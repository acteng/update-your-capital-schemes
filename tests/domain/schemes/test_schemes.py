import pytest

from schemes.domain.schemes.funding import SchemeFunding
from schemes.domain.schemes.milestones import Milestone, SchemeMilestones
from schemes.domain.schemes.outputs import SchemeOutputs
from schemes.domain.schemes.overview import FundingProgramme, FundingProgrammes, SchemeOverview, SchemeType
from schemes.domain.schemes.reviews import SchemeReviews
from schemes.domain.schemes.schemes import Scheme, Status
from tests.domain.builders import build_scheme


class TestScheme:
    def test_create(self) -> None:
        scheme = Scheme(reference="ATE00001", status=Status.ACTIVE)

        assert scheme.reference == "ATE00001" and scheme.status == Status.ACTIVE

    def test_get_overview(self) -> None:
        scheme = build_scheme(reference="ATE00001", name="Wirral Package")

        assert isinstance(scheme.overview, SchemeOverview)

    def test_get_funding(self) -> None:
        scheme = build_scheme(reference="ATE00001", name="Wirral Package")

        assert isinstance(scheme.funding, SchemeFunding)

    def test_get_milestones(self) -> None:
        scheme = build_scheme(reference="ATE00001", name="Wirral Package")

        assert isinstance(scheme.milestones, SchemeMilestones)

    def test_get_outputs(self) -> None:
        scheme = build_scheme(reference="ATE00001", name="Wirral Package")

        assert isinstance(scheme.outputs, SchemeOutputs)

    def test_get_reviews(self) -> None:
        scheme = build_scheme(reference="ATE00001", name="Wirral Package")

        assert isinstance(scheme.reviews, SchemeReviews)

    @pytest.mark.parametrize(
        "status, expected_updateable",
        [
            (Status.PIPELINE, False),
            (Status.ACTIVE, True),
            (Status.PAUSED, False),
            (Status.CONCLUDED, False),
            (Status.DELETED, False),
        ],
    )
    def test_is_updateable_when_active(self, status: Status, expected_updateable: bool) -> None:
        scheme = build_scheme(
            reference="ATE00001",
            name="Wirral Package",
            funding_programme=FundingProgrammes.ATF4,
            status=status,
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
            reference="ATE00001",
            name="Wirral Package",
            funding_programme=funding_programme,
            status=Status.ACTIVE,
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
            reference="ATE00001",
            name="Wirral Package",
            funding_programme=funding_programme,
            status=Status.ACTIVE,
        )

        assert scheme.is_updateable == expected_updateable

    def test_is_updateable_when_no_overview_revision(self) -> None:
        scheme = build_scheme(reference="ATE00001", status=Status.ACTIVE, overview_revisions=[])

        assert scheme.is_updateable is True

    def test_milestones_eligible_for_authority_update_when_development(self) -> None:
        scheme = build_scheme(reference="ATE00001", name="Wirral Package", type_=SchemeType.DEVELOPMENT)

        assert scheme.milestones_eligible_for_authority_update == {
            Milestone.FEASIBILITY_DESIGN_COMPLETED,
            Milestone.PRELIMINARY_DESIGN_COMPLETED,
            Milestone.DETAILED_DESIGN_COMPLETED,
        }

    def test_milestones_eligible_for_authority_update_when_construction(self) -> None:
        scheme = build_scheme(reference="ATE00001", name="Wirral Package", type_=SchemeType.CONSTRUCTION)

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
            (FundingProgrammes.OTH, "OTH"),
            (FundingProgrammes.CON, "CON"),
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
            (FundingProgrammes.OTH, False),
            (FundingProgrammes.CON, False),
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
            (FundingProgrammes.OTH, False),
            (FundingProgrammes.CON, True),
        ],
    )
    def test_is_eligible_for_authority_update(
        self, funding_programme: FundingProgramme, expected_is_eligible_for_authority_update: bool
    ) -> None:
        assert funding_programme.is_eligible_for_authority_update == expected_is_eligible_for_authority_update
