# SPDX-License-Identifier: AGPL-3.0-only

import os

from django.core.exceptions import ImproperlyConfigured


def required(name: str) -> str:
    value = os.environ.get(name, "")
    if not value.strip():
        raise ImproperlyConfigured(f"Missing required environment variable: {name}")
    return value


def persistent_secret(name: str) -> str:
    value = required(name)
    if len(value) < 50 or len(set(value)) < 5 or value.startswith("django-insecure-"):
        raise ImproperlyConfigured(f"Generate a strong random secret for {name}")
    return value


def postgres(
    prefix: str, *, local: bool = False
) -> dict[str, dict[str, str | dict[str, int]]]:
    config = {
        key: required(prefix + key)
        for key in ("NAME", "USER", "PASSWORD", "HOST", "PORT")
    }

    if local and config["HOST"] not in {"127.0.0.1", "localhost", "::1"}:
        raise ImproperlyConfigured(f"Local database must use loopback for {prefix}")

    if not config["PORT"].isascii() or not config["PORT"].isdecimal():
        raise ImproperlyConfigured(f"Invalid PostgreSQL port for {prefix}")

    if not 1 <= int(config["PORT"]) <= 65535:
        raise ImproperlyConfigured(f"Invalid PostgreSQL port for {prefix}")

    return {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            **config,
            "OPTIONS": {
                "connect_timeout": 5,
            },
        }
    }


def production_hosts() -> list[str]:
    hosts = [host.strip() for host in required("FDS_ALLOWED_HOSTS").split(",")]
    if any(
        not host or host.startswith(".") or "*" in host or "/" in host for host in hosts
    ):
        raise ImproperlyConfigured("FDS_ALLOWED_HOSTS must contain explicit host names")
    return hosts
