# SPDX-License-Identifier: AGPL-3.0-only

from typing import Any

from rest_framework import serializers


class DisplayNameSerializer(serializers.Serializer[dict[str, str]]):
    display_name = serializers.CharField(max_length=150, allow_blank=False)

    def to_internal_value(self, data: Any) -> dict[str, str]:
        if not isinstance(data, dict) or set(data) != {"display_name"}:
            raise serializers.ValidationError(
                {"non_field_errors": ["Expected only display_name."]}
            )
        name = data["display_name"]
        if not isinstance(name, str) or "\x00" in name:
            raise serializers.ValidationError(
                {"display_name": ["Invalid display name."]}
            )
        try:
            name.encode("utf-8")
        except UnicodeError as exc:
            raise serializers.ValidationError(
                {"display_name": ["Invalid display name."]}
            ) from exc
        result = super().to_internal_value(data)
        return {"display_name": str(result["display_name"])}


class HealthSerializer(serializers.Serializer[dict[str, str]]):
    status = serializers.CharField()
