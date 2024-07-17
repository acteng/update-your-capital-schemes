import pytest

from schemes.domain.schemes import SchemeType
from schemes.infrastructure.database.schemes.overview import SchemeTypeMapper


@pytest.mark.parametrize("type_, id_", [(SchemeType.DEVELOPMENT, 1), (SchemeType.CONSTRUCTION, 2)])
class TestSchemeTypeMapper:
    def test_to_id(self, type_: SchemeType, id_: int) -> None:
        assert SchemeTypeMapper().to_id(type_) == id_

    def test_to_domain(self, type_: SchemeType, id_: int) -> None:
        assert SchemeTypeMapper().to_domain(id_) == type_
