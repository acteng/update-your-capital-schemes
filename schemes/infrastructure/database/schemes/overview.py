from schemes.dicts import inverse_dict
from schemes.domain.schemes import SchemeType


class SchemeTypeMapper:
    _IDS = {
        SchemeType.DEVELOPMENT: 1,
        SchemeType.CONSTRUCTION: 2,
    }

    def to_id(self, type_: SchemeType) -> int:
        return self._IDS[type_]

    def to_domain(self, id_: int) -> SchemeType:
        return inverse_dict(self._IDS)[id_]
