from schemes.domain.schemes import (
    Scheme,
    SchemeFunding,
    SchemeMilestones,
    SchemeOutputs,
)


class TestScheme:
    def test_create(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)

        assert (
            scheme.id == 1
            and scheme.name == "Wirral Package"
            and scheme.authority_id == 2
            and scheme.type is None
            and scheme.funding_programme is None
        )

    def test_get_reference(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)

        assert scheme.reference == "ATE00001"

    def test_get_funding(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)

        assert isinstance(scheme.funding, SchemeFunding)

    def test_get_milestones(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)

        assert isinstance(scheme.milestones, SchemeMilestones)

    def test_get_outputs(self) -> None:
        scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)

        assert isinstance(scheme.outputs, SchemeOutputs)
