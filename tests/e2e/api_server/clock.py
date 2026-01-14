from datetime import UTC, datetime

from flask import Blueprint, Response, request

from tests.e2e.api_server.auth import require_oauth

bp = Blueprint("clock", __name__)
_now = datetime(1970, 1, 1, tzinfo=UTC)


def now() -> datetime:
    return _now


@bp.put("")
@require_oauth("tests")
def set_clock() -> Response:
    global _now
    _now = datetime.fromisoformat(request.json)
    return Response(status=204)
