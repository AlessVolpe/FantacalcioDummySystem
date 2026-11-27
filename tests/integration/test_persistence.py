# SPDX-License-Identifier: AGPL-3.0-only

import uuid
from concurrent.futures import ThreadPoolExecutor
from secrets import token_urlsafe
from threading import Barrier

import pytest
from django.contrib.auth import authenticate
from django.contrib.auth.models import Permission
from django.core.management import call_command
from django.db import IntegrityError, connection, connections, transaction
from django.utils import timezone

from fantacalciodummysystem.accounts.models import User

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


def test_migrations_and_postgresql() -> None:
    assert connection.vendor == "postgresql"
    call_command("migrate", check_unapplied=True, verbosity=0)
    tables = connection.introspection.table_names()
    assert "accounts_user" in tables
    assert "django_session" in tables
    assert "auth_user" not in tables


def test_persist_update_and_delete_user() -> None:
    password = token_urlsafe(32)
    user = User.objects.create_user(
        " EXAMPLE@Example.COM ", password, display_name=" Example "
    )
    saved = User.objects.get(pk=user.pk)
    assert isinstance(saved.pk, uuid.UUID)
    assert saved.email == "example@example.com"
    assert saved.display_name == "Example"
    assert saved.password != password
    assert saved.check_password(password)
    assert saved.email_verified_at is None
    saved.display_name = "Updated"
    saved.save(update_fields=["display_name"])
    user.refresh_from_db()
    assert user.display_name == "Updated"
    pk = user.pk
    user.delete()
    assert not User.objects.filter(pk=pk).exists()


@pytest.mark.parametrize(
    "address", ["UPPER@example.com", "a b@example.com", "é@example.com", ""]
)
def test_database_rejects_noncanonical_storage(address: str) -> None:
    # Bypass manager/model validation to exercise the actual SQL constraint.
    with pytest.raises(IntegrityError), transaction.atomic():
        User.objects.create(email=address, display_name="Invalid")
    assert not User.objects.exists()


def test_unique_email_and_rollback() -> None:
    User.objects.create_user("first@example.com", display_name="First")
    with pytest.raises(IntegrityError), transaction.atomic():
        User.objects.create_user("second@example.com", display_name="Second")
        User.objects.create_user(" FIRST@EXAMPLE.COM ", display_name="Duplicate")
    assert list(User.objects.values_list("email", flat=True)) == ["first@example.com"]


def test_password_authentication_requires_verified_active_user() -> None:
    password = token_urlsafe(32)
    user = User.objects.create_user("user@example.com", password, display_name="User")
    assert authenticate(email=user.email, password=password) is None
    user.email_verified_at = timezone.now()
    user.save(update_fields=["email_verified_at"])
    assert authenticate(email=" USER@EXAMPLE.COM ", password=password) == user
    assert authenticate(email=user.email, password=token_urlsafe(32)) is None
    user.is_active = False
    user.save(update_fields=["is_active"])
    assert authenticate(email=user.email, password=password) is None


def test_superuser_and_permissions_persist() -> None:
    admin = User.objects.create_superuser("admin@example.com", display_name="Admin")
    saved = User.objects.get(pk=admin.pk)
    assert saved.is_staff and saved.is_superuser and saved.is_active
    assert saved.email_verified_at is not None
    user = User.objects.create_user(
        "regular@example.com", display_name="Regular", email_verified_at=timezone.now()
    )
    permission = Permission.objects.get(
        content_type__app_label="accounts", codename="change_user"
    )
    user.user_permissions.add(permission)
    assert User.objects.get(pk=user.pk).has_perm("accounts.change_user")


@pytest.mark.django_db(transaction=True)
def test_concurrent_duplicate_creation() -> None:
    barrier = Barrier(2)

    def create(address: str) -> bool:
        try:
            barrier.wait(timeout=15)
            User.objects.create_user(address, display_name="Concurrent")
        except IntegrityError:
            return False
        finally:
            connections.close_all()
        return True

    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(create, "race@example.com")
        second = pool.submit(create, " RACE@EXAMPLE.COM ")
        assert sorted([first.result(timeout=30), second.result(timeout=30)]) == [
            False,
            True,
        ]
    assert User.objects.filter(email="race@example.com").count() == 1
