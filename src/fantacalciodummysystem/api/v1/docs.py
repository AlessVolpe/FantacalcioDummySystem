# SPDX-License-Identifier: AGPL-3.0-only

from collections.abc import Callable
from typing import cast

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from ..problems import problem


def docs_only(
    view: Callable[..., HttpResponse],
) -> Callable[[HttpRequest], HttpResponse]:
    def wrapped(request: HttpRequest) -> HttpResponse:
        if not settings.FDS_API_DOCS_ENABLED:
            return problem("not_found", 404)
        return view(request)

    return wrapped


schema = docs_only(cast(Callable[..., HttpResponse], SpectacularAPIView.as_view()))
swagger = docs_only(
    cast(
        Callable[..., HttpResponse],
        SpectacularSwaggerView.as_view(url_name="api-schema"),
    )
)
redoc = docs_only(
    cast(
        Callable[..., HttpResponse], SpectacularRedocView.as_view(url_name="api-schema")
    )
)
