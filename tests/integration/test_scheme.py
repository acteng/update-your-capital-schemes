import inject
import pytest
from flask import Flask
from flask.testing import FlaskClient

from schemes.authorities.domain import Authority
from schemes.authorities.services import AuthorityRepository
from schemes.schemes.domain import Scheme
from schemes.schemes.services import SchemeRepository
from schemes.users.domain import User
from schemes.users.services import UserRepository
from tests.integration.pages import SchemePage


@pytest.fixture(name="users")
def users_fixture(app: Flask) -> UserRepository:  # pylint: disable=unused-argument
    return inject.instance(UserRepository)


@pytest.fixture(name="authorities")
def authorities_fixture(app: Flask) -> AuthorityRepository:  # pylint: disable=unused-argument
    return inject.instance(AuthorityRepository)


@pytest.fixture(name="schemes")
def schemes_fixture(app: Flask) -> SchemeRepository:  # pylint: disable=unused-argument
    return inject.instance(SchemeRepository)


def test_scheme_shows_name(
    authorities: AuthorityRepository, users: UserRepository, schemes: SchemeRepository, client: FlaskClient
) -> None:
    authorities.add(Authority(id_=1, name="Liverpool City Region Combined Authority"))
    users.add(User(email="boardman@example.com", authority_id=1))
    schemes.add(Scheme(id_=1, name="Wirral Package", authority_id=1))
    with client.session_transaction() as session:
        session["user"] = {"email": "boardman@example.com"}

    scheme_page = SchemePage(client).open(1)

    assert scheme_page.name == "ATE00001 - Wirral Package"
