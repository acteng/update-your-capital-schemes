from datetime import datetime
from decimal import Decimal

import pytest
from flask.testing import FlaskClient

from schemes.domain.authorities import Authority, AuthorityRepository
from schemes.domain.dates import DateRange
from schemes.domain.schemes import (
    ObservationType,
    OutputRevision,
    OutputTypeMeasure,
    SchemeRepository,
)
from schemes.domain.users import User, UserRepository
from tests.builders import build_scheme
from tests.integration.pages import SchemePage


class TestSchemeOutputs:
    @pytest.fixture(name="auth", autouse=True)
    def auth_fixture(self, authorities: AuthorityRepository, users: UserRepository, client: FlaskClient) -> None:
        authorities.add(Authority(id_=1, name="Liverpool City Region Combined Authority"))
        users.add(User(email="boardman@example.com", authority_id=1))
        with client.session_transaction() as session:
            session["user"] = {"email": "boardman@example.com"}

    def test_scheme_shows_minimal_outputs(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        scheme = build_scheme(id_=1, name="Wirral Package", authority_id=1)
        scheme.outputs.update_outputs(
            OutputRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_measure=OutputTypeMeasure.NEW_SEGREGATED_CYCLING_FACILITY_NUMBER_OF_JUNCTIONS,
                value=Decimal(1),
                observation_type=ObservationType.ACTUAL,
            )
        )
        schemes.add(scheme)

        scheme_page = SchemePage.open(client, id_=1)

        assert scheme_page.outputs.outputs
        outputs = list(scheme_page.outputs.outputs)
        assert outputs[0].planned == ""

    def test_scheme_shows_outputs(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        scheme = build_scheme(id_=1, name="Wirral Package", authority_id=1)
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
        schemes.add(scheme)

        scheme_page = SchemePage.open(client, id_=1)

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

    def test_scheme_shows_zero_outputs(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        scheme = build_scheme(id_=1, name="Wirral Package", authority_id=1)
        scheme.outputs.update_outputs(
            OutputRevision(
                id_=1,
                effective=DateRange(datetime(2020, 1, 1), None),
                type_measure=OutputTypeMeasure.NEW_SEGREGATED_CYCLING_FACILITY_NUMBER_OF_JUNCTIONS,
                value=Decimal("0.000000"),
                observation_type=ObservationType.PLANNED,
            )
        )
        schemes.add(scheme)

        scheme_page = SchemePage.open(client, id_=1)

        assert scheme_page.outputs.outputs
        outputs = list(scheme_page.outputs.outputs)
        assert outputs[0].planned == "0"

    def test_scheme_shows_message_when_no_outputs(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(build_scheme(id_=1, name="Wirral Package", authority_id=1))

        scheme_page = SchemePage.open(client, id_=1)

        assert not scheme_page.outputs.outputs
        assert scheme_page.outputs.is_no_outputs_message_visible
