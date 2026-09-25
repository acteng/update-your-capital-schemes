from typing import Annotated, Any

from flask import Blueprint, Response, abort, request, url_for
from pydantic import AnyUrl, Field

from tests.e2e.api_server.auth import require_oauth
from tests.e2e.api_server.base import BaseModel


class ImprovementOverviewModel(BaseModel):
    name: str
    description: str | None
    funding_managed_by: AnyUrl
    source: str


class ImprovementModel(BaseModel):
    id: Annotated[AnyUrl | None, Field(alias="@id")] = None
    reference: str
    overview: ImprovementOverviewModel


bp = Blueprint("improvements", __name__)
improvements: dict[AnyUrl, ImprovementModel] = {}


@bp.post("")
@require_oauth("tests")
def add_improvements() -> Response:
    for element in request.json:
        improvement = ImprovementModel.model_validate(element)

        if not improvement.id:
            improvement.id = _get_improvement_url(improvement.reference)

        improvements[improvement.id] = improvement

    return Response(status=201)


@bp.get("<reference>")
@require_oauth()
def get_improvement(reference: str) -> dict[str, Any]:
    improvement_url = _get_improvement_url(reference)
    improvement = improvements.get(improvement_url)

    if not improvement:
        abort(404)

    return improvement.to_json()


def _get_improvement_url(reference: str) -> AnyUrl:
    return AnyUrl(url_for("improvements.get_improvement", reference=reference, _external=True))
