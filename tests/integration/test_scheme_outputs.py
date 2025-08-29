from datetime import datetime
from decimal import Decimal

import pytest
from flask.testing import FlaskClient

from schemes.domain.authorities import Authority, AuthorityRepository
from schemes.domain.dates import DateRange
from schemes.domain.schemes.observations import ObservationType
from schemes.domain.schemes.outputs import OutputRevision, OutputTypeMeasure
from schemes.domain.schemes.schemes import SchemeRepository
from schemes.domain.users import User, UserRepository
from tests.builders import build_scheme
from tests.integration.conftest import AsyncFlaskClient
from tests.integration.pages import SchemePage


class TestSchemeOutputs:
    @pytest.fixture(name="auth", autouse=True)
    async def auth_fixture(self, authorities: AuthorityRepository, users: UserRepository, client: FlaskClient) -> None:
        await authorities.add(Authority(abbreviation="LIV", name="Liverpool City Region Combined Authority"))
        users.add(User(email="boardman@example.com", authority_abbreviation="LIV"))
        with client.session_transaction() as session:
            session["user"] = {"email": "boardman@example.com"}

    async def test_scheme_shows_minimal_outputs(
        self, schemes: SchemeRepository, async_client: AsyncFlaskClient
    ) -> None:
        scheme = build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_abbreviation="LIV")
        scheme.outputs.update_outputs(
            OutputRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_measure=OutputTypeMeasure.NEW_SEGREGATED_CYCLING_FACILITY_NUMBER_OF_JUNCTIONS,
                value=Decimal(1),
                observation_type=ObservationType.ACTUAL,
            )
        )
        await schemes.add(scheme)

        scheme_page = await SchemePage.open(async_client, reference="ATE00001")

        assert scheme_page.outputs.outputs
        outputs = list(scheme_page.outputs.outputs)
        assert outputs[0].planned == ""

    async def test_scheme_shows_outputs(self, schemes: SchemeRepository, async_client: AsyncFlaskClient) -> None:
        scheme = build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_abbreviation="LIV")
        scheme.outputs.update_outputs(
            OutputRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_measure=OutputTypeMeasure.NEW_SEGREGATED_CYCLING_FACILITY_MILES,
                value=Decimal("3.000000"),
                observation_type=ObservationType.PLANNED,
            ),
            OutputRevision(
                id_=2,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_measure=OutputTypeMeasure.IMPROVEMENTS_TO_EXISTING_ROUTE_NUMBER_OF_JUNCTIONS,
                value=Decimal("2.600000"),
                observation_type=ObservationType.PLANNED,
            ),
        )
        await schemes.add(scheme)

        scheme_page = await SchemePage.open(async_client, reference="ATE00001")

        assert scheme_page.outputs.outputs
        assert scheme_page.outputs.outputs.to_dicts() == [
            {
                "infrastructure": "New segregated cycling facility",
                "measurement": "Miles",
                "planned": "3",
            },
            {
                "infrastructure": "Improvements to make an existing walking/cycle route safer",
                "measurement": "Number of junctions",
                "planned": "2.6",
            },
        ]

    async def test_scheme_shows_zero_outputs(self, schemes: SchemeRepository, async_client: AsyncFlaskClient) -> None:
        scheme = build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_abbreviation="LIV")
        scheme.outputs.update_outputs(
            OutputRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_measure=OutputTypeMeasure.NEW_SEGREGATED_CYCLING_FACILITY_NUMBER_OF_JUNCTIONS,
                value=Decimal("0.000000"),
                observation_type=ObservationType.PLANNED,
            )
        )
        await schemes.add(scheme)

        scheme_page = await SchemePage.open(async_client, reference="ATE00001")

        assert scheme_page.outputs.outputs
        outputs = list(scheme_page.outputs.outputs)
        assert outputs[0].planned == "0"

    async def test_scheme_shows_message_when_no_outputs(
        self, schemes: SchemeRepository, async_client: AsyncFlaskClient
    ) -> None:
        await schemes.add(
            build_scheme(id_=1, reference="ATE00001", name="Wirral Package", authority_abbreviation="LIV")
        )

        scheme_page = await SchemePage.open(async_client, reference="ATE00001")

        assert not scheme_page.outputs.outputs
        assert scheme_page.outputs.is_no_outputs_message_visible
