from typing import Any, Mapping

import pytest
from flask.testing import FlaskClient

from schemes.domain.authorities import Authority, AuthorityRepository
from schemes.domain.users import UserRepository
from tests.integration.conftest import AsyncFlaskClient


class TestAuthoritiesApi:
    @pytest.fixture(name="config", scope="class")
    def config_fixture(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        return dict(config) | {"API_KEY": "boardman"}

    async def test_add_authorities(self, authorities: AuthorityRepository, async_client: AsyncFlaskClient) -> None:
        response = await async_client.post(
            "/authorities",
            headers={"Authorization": "API-Key boardman"},
            json=[
                {"abbreviation": "LIV", "name": "Liverpool City Region Combined Authority"},
                {"abbreviation": "WYO", "name": "West Yorkshire Combined Authority"},
            ],
        )

        assert response.status_code == 201
        authority1 = await authorities.get("LIV")
        authority2 = await authorities.get("WYO")
        assert (
            authority1
            and authority1.abbreviation == "LIV"
            and authority1.name == "Liverpool City Region Combined Authority"
        )
        assert (
            authority2 and authority2.abbreviation == "WYO" and authority2.name == "West Yorkshire Combined Authority"
        )

    async def test_cannot_add_authorities_when_no_credentials(
        self, authorities: AuthorityRepository, async_client: AsyncFlaskClient
    ) -> None:
        response = await async_client.post(
            "/authorities", json=[{"abbreviation": "LIV", "name": "Liverpool City Region Combined Authority"}]
        )

        assert response.status_code == 401
        assert not await authorities.get("LIV")

    async def test_cannot_add_authorities_when_incorrect_credentials(
        self, authorities: AuthorityRepository, async_client: AsyncFlaskClient
    ) -> None:
        response = await async_client.post(
            "/authorities",
            headers={"Authorization": "API-Key obree"},
            json=[{"abbreviation": "LIV", "name": "Liverpool City Region Combined Authority"}],
        )

        assert response.status_code == 401
        assert not await authorities.get("LIV")

    async def test_cannot_add_authorities_with_invalid_repr(
        self, authorities: AuthorityRepository, async_client: AsyncFlaskClient
    ) -> None:
        response = await async_client.post(
            "/authorities",
            headers={"Authorization": "API-Key boardman"},
            json=[{"abbreviation": "LIV", "name": "Liverpool City Region Combined Authority", "foo": "bar"}],
        )

        assert response.status_code == 400
        assert not await authorities.get("LIV")

    def test_add_users(self, users: UserRepository, client: FlaskClient) -> None:
        response = client.post(
            "/authorities/LIV/users",
            headers={"Authorization": "API-Key boardman"},
            json=[{"email": "boardman@example.com"}, {"email": "obree@example.com"}],
        )

        assert response.status_code == 201
        user1 = users.get("boardman@example.com")
        user2 = users.get("obree@example.com")
        assert user1 and user1.email == "boardman@example.com" and user1.authority_abbreviation == "LIV"
        assert user2 and user2.email == "obree@example.com" and user2.authority_abbreviation == "LIV"

    def test_cannot_add_users_when_no_credentials(self, users: UserRepository, client: FlaskClient) -> None:
        response = client.post("/authorities/1/users", json=[{"email": "boardman@example.com"}])

        assert response.status_code == 401
        assert not users.get("boardman@example.com")

    def test_cannot_add_users_when_incorrect_credentials(self, users: UserRepository, client: FlaskClient) -> None:
        response = client.post(
            "/authorities/1/users", headers={"Authorization": "API-Key obree"}, json=[{"email": "boardman@example.com"}]
        )

        assert response.status_code == 401
        assert not users.get("boardman@example.com")

    def test_cannot_add_users_with_invalid_repr(self, users: UserRepository, client: FlaskClient) -> None:
        response = client.post(
            "/authorities/1/users",
            headers={"Authorization": "API-Key boardman"},
            json=[{"email": "boardman@example.com", "foo": "bar"}],
        )

        assert response.status_code == 400
        assert not users.get("boardman@example.com")

    async def test_clear_authorities(self, authorities: AuthorityRepository, async_client: AsyncFlaskClient) -> None:
        await authorities.add(Authority(abbreviation="LIV", name="Liverpool City Region Combined Authority"))

        response = await async_client.delete("/authorities", headers={"Authorization": "API-Key boardman"})

        assert response.status_code == 204
        assert not await authorities.get("LIV")

    async def test_cannot_clear_authorities_when_no_credentials(
        self, authorities: AuthorityRepository, async_client: AsyncFlaskClient
    ) -> None:
        await authorities.add(Authority(abbreviation="LIV", name="Liverpool City Region Combined Authority"))

        response = await async_client.delete("/authorities")

        assert response.status_code == 401
        assert await authorities.get("LIV")

    async def test_cannot_clear_authorities_when_incorrect_credentials(
        self, authorities: AuthorityRepository, async_client: AsyncFlaskClient
    ) -> None:
        await authorities.add(Authority(abbreviation="LIV", name="Liverpool City Region Combined Authority"))

        response = await async_client.delete("/authorities", headers={"Authorization": "API-Key obree"})

        assert response.status_code == 401
        assert await authorities.get("LIV")


class TestAuthoritiesApiWhenDisabled:
    async def test_cannot_add_authorities(
        self, authorities: AuthorityRepository, async_client: AsyncFlaskClient
    ) -> None:
        response = await async_client.post(
            "/authorities",
            headers={"Authorization": "API-Key boardman"},
            json=[{"abbreviation": "LIV", "name": "Liverpool City Region Combined Authority"}],
        )

        assert response.status_code == 401
        assert not await authorities.get("LIV")

    def test_cannot_add_users(self, users: UserRepository, client: FlaskClient) -> None:
        response = client.post(
            "/authorities/1/users",
            headers={"Authorization": "API-Key boardman"},
            json=[{"email": "boardman@example.com"}],
        )

        assert response.status_code == 401
        assert not users.get("boardman@example.com")

    async def test_cannot_clear_authorities(
        self, authorities: AuthorityRepository, async_client: AsyncFlaskClient
    ) -> None:
        await authorities.add(Authority(abbreviation="LIV", name="Liverpool City Region Combined Authority"))

        response = await async_client.delete("/authorities", headers={"Authorization": "API-Key boardman"})

        assert response.status_code == 401
        assert await authorities.get("LIV")
