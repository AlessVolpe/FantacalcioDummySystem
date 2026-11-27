# SPDX-License-Identifier: AGPL-3.0-only

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request

if TYPE_CHECKING:
    from rest_framework.views import APIView


def positive_parameter(request: Request, name: str, default: int) -> int:
    values = request.query_params.getlist(name)
    if not values:
        return default
    value = values[0]
    if (
        len(values) != 1
        or not value.isascii()
        or not value.isdecimal()
        or len(value) > 9
        or int(value) < 1
    ):
        raise ValidationError("Invalid pagination parameter.")
    return int(value)


class BoundedPageNumberPagination(PageNumberPagination):
    """Views must supply explicitly ordered querysets; no unbounded collections."""

    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100
    last_page_strings: tuple[str, ...] = ()

    def get_page_size(self, request: Request) -> int:
        size = positive_parameter(request, "page_size", 25)
        if size > 100:
            raise ValidationError("Page size exceeds 100.")
        return size

    def get_page_number(self, request: Request, paginator: Any) -> int:
        return positive_parameter(request, "page", 1)

    def get_schema_operation_parameters(self, view: APIView) -> list[dict[str, Any]]:
        return [
            {
                "name": "page",
                "in": "query",
                "required": False,
                "description": "Page number (one-based).",
                "schema": {"type": "integer", "minimum": 1, "default": 1},
            },
            {
                "name": "page_size",
                "in": "query",
                "required": False,
                "description": "Results per page; values outside 1–100 are rejected.",
                "schema": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "default": 25,
                },
            },
        ]
