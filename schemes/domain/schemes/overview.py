class SchemeOverview:
    def __init__(self, name: str, authority_abbreviation: str):
        self._name = name
        self._authority_abbreviation = authority_abbreviation

    @property
    def name(self) -> str:
        return self._name

    @property
    def authority_abbreviation(self) -> str:
        return self._authority_abbreviation
