# SPDX-License-Identifier: AGPL-3.0-only

from django.core.exceptions import ValidationError


class PasswordLengthLimit:
    def validate(self, password: str, user: object = None) -> None:
        if len(password) > 128:
            raise ValidationError(self.get_help_text(), code="password_too_long")

    def get_help_text(self) -> str:
        return "Your password must contain at most 128 characters."
