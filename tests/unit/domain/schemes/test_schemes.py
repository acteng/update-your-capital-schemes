import pytest

from schemes.domain.schemes.financials import FundingProgramme, FundingProgrammes, SchemeFinancials, SchemeFunding
from schemes.domain.schemes.milestones import SchemeMilestones
from schemes.domain.schemes.outputs import SchemeOutputs
from schemes.domain.schemes.overview import SchemeOverview
from schemes.domain.schemes.reviews import SchemeReviews
from schemes.domain.schemes.schemes import Scheme, Status
from tests.unit.domain.builders import build_scheme, build_scheme_overview


class TestScheme:
    def test_create(self) -> None:
        overview = SchemeOverview(name="Wirral Package", authority_abbreviation="LIV")

        scheme = Scheme(reference="ATE00001", overview=overview, status=Status.ACTIVE)

        assert scheme.reference == "ATE00001" and scheme.overview == overview and scheme.status == Status.ACTIVE

    def test_get_financials(self) -> None:
        scheme = build_scheme(reference="ATE00001", overview=build_scheme_overview(name="Wirral Package"))

        assert isinstance(scheme.financials, SchemeFinancials)

    def test_get_milestones(self) -> None:
        scheme = build_scheme(reference="ATE00001", overview=build_scheme_overview(name="Wirral Package"))

        assert isinstance(scheme.milestones, SchemeMilestones)

    def test_get_outputs(self) -> None:
        scheme = build_scheme(reference="ATE00001", overview=build_scheme_overview(name="Wirral Package"))

        assert isinstance(scheme.outputs, SchemeOutputs)

    def test_get_reviews(self) -> None:
        scheme = build_scheme(reference="ATE00001", overview=build_scheme_overview(name="Wirral Package"))

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
            reference="ATE00001", overview=build_scheme_overview(name="Wirral Package"), status=status
        )
        scheme.financials.update_funding(SchemeFunding(funding_programme=FundingProgrammes.ATF4, amount=100_000))

        assert scheme.is_updateable == expected_updateable

    @pytest.mark.parametrize(
        "funding_programme, expected_updateable",
        [
            (FundingProgrammes.ATF4, True),
            (FundingProgramme("ATF100", False), False),
        ],
    )
    def test_is_updateable_when_eligible_for_authority_update(
        self, funding_programme: FundingProgramme, expected_updateable: bool
    ) -> None:
        scheme = build_scheme(
            reference="ATE00001", overview=build_scheme_overview(name="Wirral Package"), status=Status.ACTIVE
        )
        scheme.financials.update_funding(SchemeFunding(funding_programme=funding_programme, amount=100_000))

        assert scheme.is_updateable == expected_updateable

    def test_is_updateable_when_partially_eligible_for_authority_update(self) -> None:
        scheme = build_scheme(
            reference="ATE00001", overview=build_scheme_overview(name="Wirral Package"), status=Status.ACTIVE
        )
        scheme.financials.update_fundings(
            SchemeFunding(funding_programme=FundingProgramme("ATF100", False), amount=100_000),
            SchemeFunding(funding_programme=FundingProgrammes.CON, amount=20_000),
        )

        assert scheme.is_updateable

    def test_is_updateable_when_no_funding(self) -> None:
        scheme = build_scheme(
            reference="ATE00001", overview=build_scheme_overview(name="Wirral Package"), status=Status.ACTIVE
        )

        assert not scheme.is_updateable
