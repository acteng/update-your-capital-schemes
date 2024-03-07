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

        assert scheme_page.review.confirm_url == "/schemes/1"

    def test_review_updates_last_reviewed(
        self, clock: Clock, schemes: SchemeRepository, client: FlaskClient, csrf_token: str
    ) -> None:
        clock.now = datetime(2023, 4, 24, 12)
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=1)
        scheme.reviews.update_authority_review(
            AuthorityReview(id_=1, review_date=datetime(2020, 1, 2), source=DataSource.ATF4_BID)
        )
        schemes.add(scheme)

        client.post("/schemes/1", data={"csrf_token": csrf_token, "up_to_date": "confirmed"})

        actual_scheme = schemes.get(1)
        assert actual_scheme
        authority_review1: AuthorityReview
        authority_review2: AuthorityReview
        authority_review1, authority_review2 = actual_scheme.reviews.authority_reviews
        assert (
            authority_review2.review_date == datetime(2023, 4, 24, 12)
            and authority_review2.source == DataSource.AUTHORITY_UPDATE
        )

    def test_review_shows_schemes(self, schemes: SchemeRepository, client: FlaskClient, csrf_token: str) -> None:
        schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

        response = client.post("/schemes/1", data={"csrf_token": csrf_token, "up_to_date": "confirmed"})

        assert response.status_code == 302 and response.location == "/schemes"

    def test_cannot_review_when_error(self, schemes: SchemeRepository, client: FlaskClient, csrf_token: str) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=1)
        scheme.reviews.update_authority_review(
            AuthorityReview(id_=1, review_date=datetime(2020, 1, 2, 12), source=DataSource.ATF4_BID)
        )
        schemes.add(scheme)

        scheme_page = SchemePage(client.post("/schemes/1", data={"csrf_token": csrf_token}, follow_redirects=True))

        assert scheme_page.title == "Error: Update your capital schemes - Active Travel England - GOV.UK"
        assert scheme_page.errors and list(scheme_page.errors) == [
            "Confirm that the details in this scheme have been reviewed and are all up-to-date"
        ]
        assert (
            scheme_page.review.up_to_date.is_errored
            and scheme_page.review.up_to_date.error
            == "Error: Confirm that the details in this scheme have been reviewed and are all up-to-date"
            and not scheme_page.review.up_to_date.value
        )
        actual_scheme = schemes.get(1)
        assert actual_scheme
        authority_review: AuthorityReview
        (authority_review,) = actual_scheme.reviews.authority_reviews
        assert (
            authority_review.id == 1
            and authority_review.review_date == datetime(2020, 1, 2, 12)
            and authority_review.source == DataSource.ATF4_BID
        )

    def test_cannot_review_when_no_csrf_token(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

        scheme_page = SchemePage(client.post("/schemes/1", data={}, follow_redirects=True))

        assert scheme_page.name == "Wirral Package"
        assert (
            scheme_page.important_notification
            and scheme_page.important_notification.heading
            == "The form you were submitting has expired. Please try again."
        )

    def test_cannot_review_when_incorrect_csrf_token(self, schemes: SchemeRepository, client: FlaskClient) -> None:
        schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))

        scheme_page = SchemePage(client.post("/schemes/1", data={"csrf_token": "x"}, follow_redirects=True))

        assert scheme_page.name == "Wirral Package"
        assert (
            scheme_page.important_notification
            and scheme_page.important_notification.heading
            == "The form you were submitting has expired. Please try again."
        )

    def test_cannot_review_when_different_authority(
        self, authorities: AuthorityRepository, schemes: SchemeRepository, client: FlaskClient, csrf_token: str
    ) -> None:
        authorities.add(Authority(id_=2, name="West Yorkshire Combined Authority"))
        schemes.add(Scheme(id_=2, name="Hospital Fields Road", authority_id=2))

        response = client.post("/schemes/2", data={"csrf_token": csrf_token, "up_to_date": "confirmed"})

        assert response.status_code == 403
