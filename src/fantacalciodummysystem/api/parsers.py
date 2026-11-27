# SPDX-License-Identifier: AGPL-3.0-only

import json
from collections.abc import Mapping
from typing import Any

from rest_framework.exceptions import APIException, ParseError
from rest_framework.parsers import BaseParser

MAX_BODY = 16 * 1024


class BodyTooLarge(APIException):
    status_code = 413
    default_detail = "Request body too large."
    default_code = "payload_too_large"


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON member")
        result[key] = value
    return result


def reject_constant(value: str) -> None:
    raise ValueError("Nonstandard JSON constant")


class StrictJSONParser(BaseParser):
    media_type = "application/json"

    def parse(
        self,
        stream: Any,
        media_type: str | None = None,
        parser_context: Mapping[str, Any] | None = None,
    ) -> Any:
        raw = stream.read(MAX_BODY + 1)
        if len(raw) > MAX_BODY:
            raise BodyTooLarge()
        try:
            return json.loads(
                raw.decode("utf-8"),
                object_pairs_hook=unique_object,
                parse_constant=reject_constant,
            )
        except (ValueError, RecursionError) as exc:
            raise ParseError("Invalid JSON.") from exc
