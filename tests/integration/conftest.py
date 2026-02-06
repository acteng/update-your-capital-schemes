from typing import Any, AsyncGenerator, Callable, Generator, Mapping

import inject
import pytest
from asgiref.sync import sync_to_async
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat, PublicFormat
from flask import Flask, session
from flask.testing import FlaskClient
from flask_wtf.csrf import generate_csrf
from inject import Binder
from werkzeug.test import TestResponse

from schemes import bindings, create_app, destroy_app
from schemes.annotations import Migrated
from schemes.domain.authorities import AuthorityRepository
from schemes.domain.schemes.schemes import SchemeRepository
from schemes.domain.users import UserRepository
from schemes.infrastructure.clock import Clock
from tests.integration.fakes import MemoryAuthorityRepository, MemorySchemeRepository, MemoryUserRepository


class AsyncFlaskClient:
    def __init__(self, client: FlaskClient):
        self._client = client

    @sync_to_async
    def get(self, *args: Any, **kwargs: Any) -> TestResponse:
        return self._client.get(*args, **kwargs)

    @sync_to_async
    def post(self, *args: Any, **kwargs: Any) -> TestResponse:
        return self._client.post(*args, **kwargs)

    @sync_to_async
    def delete(self, *args: Any, **kwargs: Any) -> TestResponse:
        return self._client.delete(*args, **kwargs)


@pytest.fixture(name="config", scope="class")
def config_fixture() -> Mapping[str, Any]:
    private_key, public_key = _generate_key_pair()

    return {
        "TESTING": True,
        "SECRET_KEY": b"secret_key",
        "GOVUK_CLIENT_ID": "test",
        "GOVUK_CLIENT_SECRET": private_key.decode(),
        "GOVUK_SERVER_METADATA_URL": "test",
        "GOVUK_PROFILE_URL": "test",
        "GOVUK_END_SESSION_ENDPOINT": "test",
    }


@pytest.fixture(name="app", scope="class")
def app_fixture(config: Mapping[str, Any]) -> Generator[Flask]:
    app = create_app(config)
    inject.clear_and_configure(_test_bindings(app), bind_in_runtime=False, allow_override=True)
    yield app
    destroy_app(app)


@pytest.fixture(name="client")
def client_fixture(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture(name="async_client")
def async_client_fixture(client: FlaskClient) -> AsyncFlaskClient:
    return AsyncFlaskClient(client)


@pytest.fixture(name="csrf_token")
def csrf_token_fixture(client: FlaskClient) -> str:
    with client.session_transaction() as client_session:
        csrf_token: str = generate_csrf()
        client_session["csrf_token"] = session["csrf_token"]
    return csrf_token


@pytest.fixture(name="clock")
def clock_fixture(app: Flask) -> Clock:
    return inject.instance(Clock)


@pytest.fixture(name="authorities")
async def authorities_fixture(app: Flask) -> AsyncGenerator[AuthorityRepository]:
    authorities = inject.instance(AuthorityRepository)
    yield authorities
    await authorities.clear()


@pytest.fixture(name="users")
def users_fixture(app: Flask) -> Generator[UserRepository]:
    users = inject.instance(UserRepository)
    yield users
    users.clear()


@pytest.fixture(name="schemes")
async def schemes_fixture(app: Flask) -> AsyncGenerator[SchemeRepository]:
    schemes = inject.instance(SchemeRepository)
    yield schemes
    await schemes.clear()


def _test_bindings(app: Flask) -> Callable[[Binder], None]:
    def _bindings(binder: Binder) -> None:
        binder.install(bindings(app))
        authority_repository = MemoryAuthorityRepository()
        binder.bind(AuthorityRepository, authority_repository)
        binder.bind((AuthorityRepository, Migrated), authority_repository)
        binder.bind(UserRepository, MemoryUserRepository())
        scheme_repository = MemorySchemeRepository()
        binder.bind(SchemeRepository, scheme_repository)
        binder.bind((SchemeRepository, Migrated), scheme_repository)

    return _bindings


def _generate_key_pair() -> tuple[bytes, bytes]:
    key_pair = rsa.generate_private_key(backend=default_backend(), public_exponent=65537, key_size=2048)
    private_key = key_pair.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())
    public_key = key_pair.public_key().public_bytes(Encoding.OpenSSH, PublicFormat.OpenSSH)
    return private_key, public_key
