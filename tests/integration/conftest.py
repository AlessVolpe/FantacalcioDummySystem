# SPDX-License-Identifier: AGPL-3.0-only

import os
from collections.abc import Iterator

import psycopg
import pytest
from django.conf import settings
from django.core.management import call_command
from django.db import connection, connections
from pytest_django import DjangoDbBlocker

from scripts.provision_test_database import TEST_DATABASE_MARKER

TEST_SETTINGS = "fantacalciodummysystem.config.settings.testing"
# Only the current foundation schema is permitted in the dedicated database.
EXPECTED_TABLES = {
    "accounts_accounttoken",
    "accounts_auththrottle",
    "accounts_user",
    "accounts_user_groups",
    "accounts_user_user_permissions",
    "auth_group",
    "auth_group_permissions",
    "auth_permission",
    "django_admin_log",
    "django_content_type",
    "django_migrations",
    "django_session",
}


@pytest.fixture(scope="session")
def django_db_setup(django_db_blocker: DjangoDbBlocker) -> Iterator[None]:
    """Use the marked pre-provisioned DB; never CREATE or DROP a database."""
    if settings.SETTINGS_MODULE != TEST_SETTINGS or connection.vendor != "postgresql":
        pytest.fail("Integration tests require PostgreSQL testing settings")
    config = settings.DATABASES["default"]
    if config["NAME"] == os.environ.get("FDS_DEV_DB_NAME") or config[
        "USER"
    ] == os.environ.get("FDS_DEV_DB_USER"):
        pytest.fail("Testing and development identities must be distinct")
    with psycopg.connect(
        dbname=config["NAME"],
        user=config["USER"],
        password=config["PASSWORD"],
        host=config["HOST"],
        port=config["PORT"],
        autocommit=True,
        connect_timeout=5,
    ) as guard:
        row = guard.execute(
            """
            SELECT d.datname, r.rolname, shobj_description(d.oid, 'pg_database'),
                   d.datdba = r.oid,
                   NOT (r.rolsuper OR r.rolcreatedb OR r.rolcreaterole
                        OR r.rolreplication OR r.rolbypassrls),
                   NOT EXISTS (SELECT 1 FROM pg_auth_members WHERE member = r.oid)
              FROM pg_database d CROSS JOIN pg_roles r
             WHERE d.datname = current_database() AND r.rolname = current_user
            """
        ).fetchone()
        if row != (
            config["NAME"],
            config["USER"],
            TEST_DATABASE_MARKER,
            True,
            True,
            True,
        ):
            pytest.fail("Refusing an unmarked database or an unsafe testing role")
        # Session-level lock lives on a separate connection, even if Django closes
        # its own connections between transactional tests.
        if guard.execute("SELECT pg_try_advisory_lock(15603371)").fetchone() != (True,):
            pytest.fail("Another integration test session is using this database")
        with django_db_blocker.unblock():
            tables = set(connection.introspection.table_names())
            if not tables <= EXPECTED_TABLES:
                pytest.fail("Unexpected tables in the dedicated testing database")
            with connection.cursor() as cursor:
                for table in (
                    "accounts_user",
                    "accounts_accounttoken",
                    "accounts_auththrottle",
                    "auth_group",
                    "django_admin_log",
                    "django_session",
                ):
                    if table in tables:
                        quoted_table = connection.ops.quote_name(table)
                        cursor.execute(f"SELECT EXISTS (SELECT 1 FROM {quoted_table})")
                        if cursor.fetchone() != (False,):
                            pytest.fail(
                                "Dedicated testing database contains existing data"
                            )
            call_command("makemigrations", check=True, dry_run=True, verbosity=0)
            call_command("migrate", interactive=False, verbosity=0)
        try:
            yield
        finally:
            connections.close_all()
