# SPDX-License-Identifier: AGPL-3.0-only

import pytest
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command

from fantacalciodummysystem.config.settings.environment import (
    postgres,
    production_hosts,
    required,
)


def test_django_system_checks() -> None:
    call_command("check")


def test_testing_settings() -> None:
    assert settings.AUTH_USER_MODEL == "accounts.User"
    assert settings.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql"
    assert not settings.DEBUG
    assert settings.USE_TZ
    assert settings.TIME_ZONE == "UTC"


def test_production_database_requires_configuration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("FDS_DB_NAME", raising=False)
    with pytest.raises(ImproperlyConfigured, match="FDS_DB_NAME"):
        postgres("FDS_DB_")


def test_secret_required(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FDS_SECRET_KEY", " ")
    with pytest.raises(ImproperlyConfigured, match="FDS_SECRET_KEY"):
        required("FDS_SECRET_KEY")


def test_production_hosts(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FDS_ALLOWED_HOSTS", "example.com, www.example.com")
    assert production_hosts() == ["example.com", "www.example.com"]
    monkeypatch.setenv("FDS_ALLOWED_HOSTS", "*")
    with pytest.raises(ImproperlyConfigured):
        production_hosts()


def test_local_database_rejects_remote_host(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FDS_DEV_DB_HOST", "db.example.com")
    with pytest.raises(ImproperlyConfigured, match="loopback"):
        postgres("FDS_DEV_DB_", local=True)


def test_postgres_connection_timeout() -> None:
    config = postgres("FDS_TEST_DB_", local=True)

    assert config["default"]["OPTIONS"] == {
        "connect_timeout": 5,
    }
