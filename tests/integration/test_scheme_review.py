from datetime import datetime

import pytest
from flask.testing import FlaskClient

from schemes.domain.authorities import Authority, AuthorityRepository
from schemes.domain.schemes import AuthorityReview, DataSource, Scheme, SchemeRepository
from schemes.domain.users import User, UserRepository
from schemes.infrastructure.clock import Clock
from tests.integration.pages import SchemePage


class TestSchemeReview:
    @pytest.fixture(name="auth", autouse=True)
    def auth_fixture(self, authorities: AuthorityRepository, users: UserRepository, client: FlaskClient) -> None:
        authorities.add(Authority(id_=1, name="Liverpool City Region Combined Authority"))
        users.add(User(email="boardman@example.com", authority_id=1))
        with client.session_transaction() as session:
            session["user"] = {"email": "boardman@example.com"}

    def test_scheme_shows_confirm(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

        scheme_page = SchemePage.open(client, id_=1)

        assert scheme_page.review.confirm_url == "/schemes/1/review"

    def test_review_updates_last_reviewed(self, clock: Clock, schemes: SchemeRepository, client: FlaskClient) -> None:
        clock.now = datetime(2023, 4, 24, 12)
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=1)
        scheme.update_authority_review(
            AuthorityReview(id_=1, review_date=datetime(2020, 1, 2), source=DataSource.ATF4_BID)
        )
        schemes.add(scheme)

        client.post("/schemes/1/review", data={})

        actual_scheme = schemes.get(1)
        assert actual_scheme
        authority_review1: AuthorityReview
        authority_review2: AuthorityReview
        authority_review1, authority_review2 = actual_scheme.authority_reviews
        assert (
            authority_review2.review_date == datetime(2023, 4, 24, 12)
            and authority_review2.source == DataSource.AUTHORITY_UPDATE
        )

    def test_review_shows_schemes(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

        response = client.post("/schemes/1/review", data={})

        assert response.status_code == 302 and response.location == "/schemes"
