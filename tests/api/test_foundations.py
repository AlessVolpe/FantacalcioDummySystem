# SPDX-License-Identifier: AGPL-3.0-only

from io import BytesIO
from typing import Any, cast

import pytest
from django.db import OperationalError, connection
from django.http import HttpRequest, HttpResponse
from django.test import Client, RequestFactory, override_settings
from drf_spectacular.generators import SchemaGenerator
from rest_framework.exceptions import NotFound, ParseError, ValidationError
from rest_framework.request import Request

from fantacalciodummysystem.api.pagination import BoundedPageNumberPagination
from fantacalciodummysystem.api.parsers import BodyTooLarge, StrictJSONParser
from fantacalciodummysystem.api.problems import (
    MEDIA_TYPE,
    ApiResponseMiddleware,
    problem,
)
from fantacalciodummysystem.api.v1.serializers import DisplayNameSerializer
from fantacalciodummysystem.api.v1.views import ReadinessView

BASE = "/api/v1/"


def test_problem_format() -> None:
    response = problem("invalid_credentials", 403)
    assert response.status_code == 403
    assert response["Content-Type"] == MEDIA_TYPE
    assert b'"type": "about:blank"' in response.content
    assert b'"code": "invalid_credentials"' in response.content


def test_django_failure_is_sanitized() -> None:
    def fail(request: HttpRequest) -> HttpResponse:
        return HttpResponse("private diagnostic", status=500)

    middleware = ApiResponseMiddleware(fail)
    request = RequestFactory().get(BASE + "probe/")
    response = middleware(request)
    assert response.status_code == 500
    assert response["Content-Type"] == MEDIA_TYPE
    assert b"private diagnostic" not in response.content
    assert b'"code": "internal_error"' in response.content
    outside = middleware(RequestFactory().get("/admin/"))
    assert b"private diagnostic" in outside.content


def test_liveness_and_missing_route(client: Client) -> None:
    live = client.get(BASE + "health/live/")
    assert live.status_code == 200
    assert live.json() == {"status": "ok"}
    assert live["Cache-Control"] == "no-store"
    missing = client.get(BASE + "missing/")
    assert missing.status_code == 404
    assert missing["Content-Type"] == MEDIA_TYPE
    assert missing.json()["code"] == "not_found"
    assert client.get(BASE + "health/live").status_code == 404
    bad_method = client.post(BASE + "health/live/")
    assert bad_method.status_code == 405
    assert bad_method["Content-Type"] == MEDIA_TYPE
    assert "GET" in bad_method["Allow"]


def test_readiness_failure_is_generic(
    client: Client, monkeypatch: pytest.MonkeyPatch
) -> None:
    def unavailable() -> Any:
        raise OperationalError("internal database address must not be exposed")

    monkeypatch.setattr(connection, "cursor", unavailable)
    response = client.get(BASE + "health/ready/")
    assert response.status_code == 503
    assert response["Content-Type"] == MEDIA_TYPE
    assert response.json()["code"] == "service_unavailable"
    assert b"internal database address" not in response.content
    assert ReadinessView.unavailable().status_code == 503


def test_authentication_and_csrf_errors(client: Client) -> None:
    response = client.get(BASE + "auth/me/")
    assert response.status_code == 403
    assert response.json()["code"] == "authentication_required"
    assert response["Content-Type"] == MEDIA_TYPE
    malformed = client.post(
        BASE + "auth/login/",
        '{"email":"first@example.com","email":"second@example.com","password":"x"}',
        content_type="application/json",
    )
    assert malformed.status_code == 400
    assert malformed.json()["code"] == "invalid_input"
    browser = Client(enforce_csrf_checks=True)
    for endpoint, method in (("auth/login/", "post"), ("auth/me/", "patch")):
        response = getattr(browser, method)(
            BASE + endpoint, {}, content_type="application/json"
        )
        assert response.status_code == 403
        assert response.json()["code"] == "csrf_failed"
        assert response["Content-Type"] == MEDIA_TYPE


def test_json_only_and_docs_gate(client: Client) -> None:
    response = client.get(BASE + "health/live/", HTTP_ACCEPT="text/html")
    assert response.status_code == 406
    assert response["Content-Type"] == MEDIA_TYPE
    with override_settings(FDS_API_DOCS_ENABLED=False):
        for route in ("schema/", "docs/", "redoc/"):
            assert client.get(BASE + route).status_code == 404
    with override_settings(FDS_API_DOCS_ENABLED=True):
        for route in ("schema/", "docs/", "redoc/"):
            assert client.get(BASE + route).status_code == 200


@pytest.mark.parametrize("raw", [b'{"a": 1, "a": 2}', b'{"a": NaN}', b"\xff", b"{"])
def test_strict_json_rejects_invalid_input(raw: bytes) -> None:
    with pytest.raises(ParseError):
        StrictJSONParser().parse(BytesIO(raw))


def test_strict_json_size_limit() -> None:
    with pytest.raises(BodyTooLarge):
        StrictJSONParser().parse(BytesIO(b" " * 16385))


@pytest.mark.parametrize(
    "data",
    [
        {},
        {"display_name": ""},
        {"display_name": " "},
        {"display_name": 1},
        {"display_name": "Name", "is_staff": True},
        {"display_name": "x" * 151},
        {"display_name": "\x00"},
        {"display_name": "\ud800"},
        [],
    ],
)
def test_profile_validation_rejects_invalid_fields(data: Any) -> None:
    serializer = DisplayNameSerializer(data=data)
    assert not serializer.is_valid()


def test_profile_trims_display_name() -> None:
    serializer = DisplayNameSerializer(data={"display_name": "  Name é  "})
    assert serializer.is_valid()
    assert serializer.validated_data == {"display_name": "Name é"}


def test_pagination_defaults_and_bounds() -> None:
    paginator = BoundedPageNumberPagination()
    factory = RequestFactory()
    request = Request(factory.get("/probe/"))
    assert paginator.paginate_queryset(list(range(110)), request) == list(range(25))
    response = paginator.get_paginated_response(list(range(25)))
    assert response.data["count"] == 110
    assert response.data["previous"] is None
    assert response.data["next"] is not None
    request = Request(factory.get("/probe/?page=2&page_size=100"))
    assert paginator.paginate_queryset(list(range(110)), request) == list(
        range(100, 110)
    )
    assert paginator.get_paginated_response([]).data["next"] is None
    with pytest.raises(NotFound):
        paginator.paginate_queryset(
            list(range(110)), Request(factory.get("/probe/?page=99"))
        )


@pytest.mark.parametrize(
    "query",
    [
        "page_size=101",
        "page_size=0",
        "page_size=abc",
        "page=last",
        "page=0",
        "page=1&page=2",
    ],
)
def test_pagination_rejects_invalid_parameters(query: str) -> None:
    request = Request(RequestFactory().get("/probe/?" + query))
    with pytest.raises(ValidationError):
        BoundedPageNumberPagination().paginate_queryset([1, 2, 3], request)


def test_schema_describes_auth_and_health() -> None:
    generator = SchemaGenerator()  # type: ignore[no-untyped-call]
    schema = cast(
        dict[str, Any],
        generator.get_schema(request=None, public=True),  # type: ignore[no-untyped-call]
    )
    assert schema["openapi"] == "3.1.0"
    paths = schema["paths"]
    for route in (
        "csrf/",
        "register/",
        "resend/",
        "verify/",
        "login/",
        "logout/",
        "password/reset/",
        "password/confirm/",
        "password/change/",
        "me/",
    ):
        assert BASE + "auth/" + route in paths
    login = paths[BASE + "auth/login/"]["post"]
    assert login["security"] == [{"csrfToken": []}]
    assert "403" in login["responses"]
    csrf = schema["components"]["securitySchemes"]["csrfToken"]
    assert (csrf["type"], csrf["in"], csrf["name"]) == (
        "apiKey",
        "header",
        "X-CSRFToken",
    )
    patch = paths[BASE + "auth/me/"]["patch"]
    assert patch["security"] == [{"cookieAuth": [], "csrfToken": []}]
    assert MEDIA_TYPE in patch["responses"]["400"]["content"]
    assert "503" in paths[BASE + "health/ready/"]["get"]["responses"]
    assert paths[BASE + "auth/csrf/"]["get"]["security"] == []
    assert paths[BASE + "auth/me/"]["get"]["security"] == [{"cookieAuth": []}]
    for path in paths.values():
        for method in ("post", "patch", "put", "delete"):
            if method in path:
                assert "csrfToken" in path[method]["security"][0]
                assert all(
                    parameter["name"].lower() != "x-csrftoken"
                    for parameter in path[method].get("parameters", [])
                )


def test_swagger_configures_automatic_csrf(client: Client) -> None:
    with override_settings(FDS_API_DOCS_ENABLED=True):
        response = client.get(BASE + "docs/")
    assert response.status_code == 200
    assert b"requestInterceptor: async (request)" in response.content
    assert b'fetch("/api/v1/auth/csrf/"' in response.content
    assert b'headers.set("X-CSRFToken", csrfToken)' in response.content
    assert b"persistAuthorization: false" in response.content
    assert b"validatorUrl: null" in response.content
