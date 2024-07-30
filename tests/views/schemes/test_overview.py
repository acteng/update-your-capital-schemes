from datetime import datetime

import pytest

from schemes.domain.dates import DateRange
from schemes.domain.schemes import (
    FundingProgramme,
    FundingProgrammes,
    OverviewRevision,
    SchemeType,
)
from schemes.views.schemes.overview import (
    FundingProgrammeRepr,
    OverviewRevisionRepr,
    SchemeTypeRepr,
)


class TestOverviewRevisionRepr:
    def test_from_domain(self) -> None:
        overview_revision = OverviewRevision(
            id_=1,
            effective=DateRange(datetime(2020, 1, 1, 12), datetime(2020, 2, 1, 13)),
            name="Wirral Package",
            authority_id=2,
            type_=SchemeType.CONSTRUCTION,
            funding_programme=FundingProgrammes.ATF4,
        )

        overview_revision_repr = OverviewRevisionRepr.from_domain(overview_revision)

        assert overview_revision_repr == OverviewRevisionRepr(
            id=1,
            effective_date_from="2020-01-01T12:00:00",
            effective_date_to="2020-02-01T13:00:00",
            name="Wirral Package",
            authority_id=2,
            type=SchemeTypeRepr.CONSTRUCTION,
            funding_programme=FundingProgrammeRepr.ATF4,
        )

    def test_from_domain_when_no_effective_date_to(self) -> None:
        overview_revision = OverviewRevision(
            id_=1,
            effective=DateRange(datetime(2020, 1, 1), None),
            name="Wirral Package",
            authority_id=2,
            type_=SchemeType.CONSTRUCTION,
            funding_programme=FundingProgrammes.ATF4,
        )

        overview_revision_repr = OverviewRevisionRepr.from_domain(overview_revision)

        assert overview_revision_repr.effective_date_to is None

    def test_to_domain(self) -> None:
        overview_revision_repr = OverviewRevisionRepr(
            id=1,
            effective_date_from="2020-01-01T12:00:00",
            effective_date_to="2020-02-01T13:00:00",
            name="Wirral Package",
            authority_id=2,
            type=SchemeTypeRepr.CONSTRUCTION,
            funding_programme=FundingProgrammeRepr.ATF4,
        )

        overview_revision = overview_revision_repr.to_domain()

        assert (
            overview_revision.id == 1
            and overview_revision.effective == DateRange(datetime(2020, 1, 1, 12), datetime(2020, 2, 1, 13))
            and overview_revision.name == "Wirral Package"
            and overview_revision.authority_id == 2
            and overview_revision.type == SchemeType.CONSTRUCTION
            and overview_revision.funding_programme == FundingProgrammes.ATF4
        )

    def test_to_domain_when_no_effective_date_to(self) -> None:
        overview_revision_repr = OverviewRevisionRepr(
            id=1,
            effective_date_from="2020-01-01T12:00:00",
            effective_date_to=None,
            name="Wirral Package",
            authority_id=2,
            type=SchemeTypeRepr.CONSTRUCTION,
            funding_programme=FundingProgrammeRepr.ATF4,
        )

        overview_revision = overview_revision_repr.to_domain()

        assert overview_revision.effective.date_to is None


@pytest.mark.parametrize(
    "type_, type_repr",
    [(SchemeType.DEVELOPMENT, "development"), (SchemeType.CONSTRUCTION, "construction")],
)
class TestSchemeTypeRepr:
    def test_from_domain(self, type_: SchemeType, type_repr: str) -> None:
        assert SchemeTypeRepr.from_domain(type_).value == type_repr

    def test_to_domain(self, type_: SchemeType, type_repr: str) -> None:
        assert SchemeTypeRepr(type_repr).to_domain() == type_


@pytest.mark.parametrize(
    "funding_programme, funding_programme_repr",
    [
        (FundingProgrammes.ATF2, "ATF2"),
        (FundingProgrammes.ATF3, "ATF3"),
        (FundingProgrammes.ATF4, "ATF4"),
        (FundingProgrammes.ATF4E, "ATF4e"),
    ],
)
class TestFundingProgrammeRepr:
    def test_from_domain(self, funding_programme: FundingProgramme, funding_programme_repr: str) -> None:
        assert FundingProgrammeRepr.from_domain(funding_programme).value == funding_programme_repr

    def test_to_domain(self, funding_programme: FundingProgramme, funding_programme_repr: str) -> None:
        assert FundingProgrammeRepr(funding_programme_repr).to_domain() == funding_programme
