# SPDX-License-Identifier: AGPL-3.0-only

import uuid
from secrets import token_urlsafe

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone

from fantacalciodummysystem.accounts.backends import VerifiedEmailBackend
from fantacalciodummysystem.accounts.managers import (
    canonical_email,
    validate_identity_email,
)
from fantacalciodummysystem.accounts.models import User


@pytest.mark.parametrize(
    ("address", "expected"),
    [
        ("  EXAMPLE+Tag@Example.COM  ", "example+tag@example.com"),
        ("a.b@example.com", "a.b@example.com"),
        (None, ""),
    ],
)
def test_canonical_email(address: str | None, expected: str) -> None:
    assert canonical_email(address) == expected


@pytest.mark.parametrize("address", ["", "invalid", "a b@example.com", "é@example.com"])
def test_invalid_identity(address: str) -> None:
    with pytest.raises(ValidationError):
        validate_identity_email(address)


def test_user_identity() -> None:
    assert get_user_model() is User
    user = User(email="EXAMPLE@example.com", display_name="Example")
    user.clean()
    assert isinstance(user.pk, uuid.UUID)
    assert user.email == "example@example.com"
    assert user.email_verified_at is None
    assert str(user) == "Example"
    assert user.is_active and not user.is_staff


@pytest.mark.parametrize(
    ("active", "verified", "allowed"),
    [
        (True, True, True),
        (False, True, False),
        (True, False, False),
        (False, False, False),
    ],
)
def test_backend_requires_verified_active_user(
    active: bool, verified: bool, allowed: bool
) -> None:
    user = User(
        email="user@example.com",
        display_name="Example",
        is_active=active,
        email_verified_at=timezone.now() if verified else None,
    )
    assert VerifiedEmailBackend().user_can_authenticate(user) is allowed


def test_manager_hashes_password_and_canonicalizes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def no_save(self: User, **kwargs: object) -> None:
        assert kwargs == {"using": None}

    monkeypatch.setattr(User, "save", no_save)
    password = token_urlsafe(32)
    user = User.objects.create_user(
        " EXAMPLE@Example.COM ", password, display_name=" Example "
    )
    assert user.email == "example@example.com"
    assert user.display_name == "Example"
    assert user.password != password
    assert user.check_password(password)
    assert user.email_verified_at is None


def test_superuser_rejects_unverified() -> None:
    with pytest.raises(ValueError, match="verified email"):
        User.objects.create_superuser(
            "admin@example.com", display_name="Admin", email_verified_at=None
        )


def test_unicode_identity_does_not_alias_ascii() -> None:
    email = canonical_email("K@example.com")
    assert email != "k@example.com"
    with pytest.raises(ValidationError):
        validate_identity_email(email)
