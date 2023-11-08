from schemes.schemes.domain import Scheme


def test_get_reference() -> None:
    scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)

    assert scheme.reference == "ATE00001"
