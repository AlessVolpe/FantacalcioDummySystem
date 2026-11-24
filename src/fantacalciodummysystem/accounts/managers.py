# SPDX-License-Identifier: AGPL-3.0-only

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.contrib.auth.base_user import BaseUserManager
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils import timezone

if TYPE_CHECKING:
    from .models import User


def canonical_email(email: str | None) -> str:
    """Canonical login identity; no provider-specific alias rewriting."""
    address = (email or "").strip()
    # Do not let Unicode case folding alias an otherwise rejected identity.
    return address.lower() if address.isascii() else address


def validate_identity_email(email: str) -> None:
    if not email or len(email) > 254 or any(not 33 <= ord(c) <= 126 for c in email):
        raise ValidationError("Enter an ASCII email address of at most 254 characters.")
    validate_email(email)


class UserManager(BaseUserManager["User"]):
    use_in_migrations = True

    @classmethod
    def normalize_email(cls, email: str | None) -> str:
        return canonical_email(email)

    def get_by_natural_key(self, username: str | None) -> User:
        return self.get(email=self.normalize_email(username))

    async def aget_by_natural_key(self, username: str | None) -> User:
        return await self.aget(email=self.normalize_email(username))

    def create_user(
        self,
        email: str,
        password: str | None = None,
        *,
        display_name: str,
        **extra_fields: Any,
    ) -> User:
        email = self.normalize_email(email)
        validate_identity_email(email)
        display_name = display_name.strip()
        if not display_name or len(display_name) > 150:
            raise ValidationError("Display name must contain 1–150 characters.")
        user = self.model(email=email, display_name=display_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        email: str,
        password: str | None = None,
        *,
        display_name: str,
        **extra_fields: Any,
    ) -> User:
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("email_verified_at", timezone.now())
        for flag in ("is_staff", "is_superuser", "is_active"):
            if extra_fields[flag] is not True:
                raise ValueError(f"Superuser requires {flag}=True")
        if extra_fields["email_verified_at"] is None:
            raise ValueError("Superuser requires verified email")
        return self.create_user(
            email, password, display_name=display_name, **extra_fields
        )
