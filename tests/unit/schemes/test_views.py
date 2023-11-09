from schemes.schemes.domain import Scheme
from schemes.schemes.views import SchemeContext


def test_create_context_from_domain() -> None:
    scheme = Scheme(id_=1, name="Wirral Package", authority_id=2)

    context = SchemeContext.for_domain(scheme)

    assert context == SchemeContext(reference="ATE00001", name="Wirral Package")
