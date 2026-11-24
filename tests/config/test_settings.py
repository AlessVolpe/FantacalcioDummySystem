# SPDX-License-Identifier: AGPL-3.0-only

from secrets import token_hex, token_urlsafe

import pytest
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command

from fantacalciodummysystem.config.settings import static
from fantacalciodummysystem.config.settings.environment import (
    persistent_secret,
    postgres,
    production_hosts,
    required,
)


def test_django_system_checks() -> None:
    call_command("check")


def test_static_settings() -> None:
    config = static.DATABASES["default"]
    assert config["ENGINE"] == "django.db.backends.dummy"
    for field in ("NAME", "USER", "PASSWORD", "HOST", "PORT"):
        assert not config.get(field)
    assert len(static.SECRET_KEY) >= 50
    assert settings.AUTH_USER_MODEL == "accounts.User"
    assert not settings.DEBUG
    assert settings.USE_TZ
    assert settings.TIME_ZONE == "UTC"


@pytest.fixture
def database_env(monkeypatch: pytest.MonkeyPatch) -> dict[str, str]:
    config = {
        "NAME": f"db_{token_hex(8)}",
        "USER": f"role_{token_hex(8)}",
        "PASSWORD": token_urlsafe(32),
        "HOST": "127.0.0.1",
        "PORT": "5432",
    }
    for prefix in ("FDS_DEV_DB_", "FDS_TEST_DB_", "FDS_DB_"):
        for key, value in config.items():
            monkeypatch.setenv(prefix + key, value)
    return config


@pytest.mark.parametrize(
    ("prefix", "local"),
    [("FDS_DEV_DB_", True), ("FDS_TEST_DB_", True), ("FDS_DB_", False)],
)
@pytest.mark.parametrize("field", ["NAME", "USER", "PASSWORD", "HOST", "PORT"])
@pytest.mark.parametrize("blank", [True, False])
def test_database_has_no_fallback(
    monkeypatch: pytest.MonkeyPatch,
    database_env: dict[str, str],
    prefix: str,
    local: bool,
    field: str,
    blank: bool,
) -> None:
    name = prefix + field
    if blank:
        monkeypatch.setenv(name, " ")
    else:
        monkeypatch.delenv(name)
    with pytest.raises(ImproperlyConfigured, match=name):
        postgres(prefix, local=local)


def test_secret_required(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FDS_SECRET_KEY", " ")
    with pytest.raises(ImproperlyConfigured, match="FDS_SECRET_KEY"):
        required("FDS_SECRET_KEY")


@pytest.mark.parametrize("name", ["FDS_DEV_SECRET_KEY", "FDS_SECRET_KEY"])
def test_persistent_secret(monkeypatch: pytest.MonkeyPatch, name: str) -> None:
    monkeypatch.delenv(name, raising=False)
    with pytest.raises(ImproperlyConfigured, match=name):
        persistent_secret(name)
    monkeypatch.setenv(name, token_urlsafe(4))
    with pytest.raises(ImproperlyConfigured, match=name):
        persistent_secret(name)
    value = token_urlsafe(64)
    monkeypatch.setenv(name, value)
    assert persistent_secret(name) == value


def test_production_hosts(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FDS_ALLOWED_HOSTS", "example.com, www.example.com")
    assert production_hosts() == ["example.com", "www.example.com"]
    monkeypatch.setenv("FDS_ALLOWED_HOSTS", "*")
    with pytest.raises(ImproperlyConfigured):
        production_hosts()


def test_local_database_rejects_remote_host(
    monkeypatch: pytest.MonkeyPatch, database_env: dict[str, str]
) -> None:
    monkeypatch.setenv("FDS_DEV_DB_HOST", "db.example.com")
    with pytest.raises(ImproperlyConfigured, match="loopback"):
        postgres("FDS_DEV_DB_", local=True)


@pytest.mark.parametrize("port", ["0", "65536", "-1", "abc", "１２３"])
def test_invalid_database_port(
    monkeypatch: pytest.MonkeyPatch, database_env: dict[str, str], port: str
) -> None:
    monkeypatch.setenv("FDS_TEST_DB_PORT", port)
    with pytest.raises(ImproperlyConfigured, match="port"):
        postgres("FDS_TEST_DB_", local=True)


def test_postgres_connection_settings(database_env: dict[str, str]) -> None:
    config = postgres("FDS_TEST_DB_", local=True)
    assert config["default"] == {
        "ENGINE": "django.db.backends.postgresql",
        **database_env,
        "OPTIONS": {"connect_timeout": 5},
    }
