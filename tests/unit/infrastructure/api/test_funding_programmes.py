from pydantic import AnyUrl

from schemes.domain.schemes.overview import FundingProgrammes
from schemes.infrastructure.api.funding_programmes import FundingProgrammeModel


class TestFundingProgrammeModel:
    def test_to_domain(self) -> None:
        funding_programme_model = FundingProgrammeModel(
            id=AnyUrl("https://api.example/funding-programmes/ATF4"), code="ATF4"
        )

        funding_programme = funding_programme_model.to_domain()

        assert funding_programme == FundingProgrammes.ATF4
