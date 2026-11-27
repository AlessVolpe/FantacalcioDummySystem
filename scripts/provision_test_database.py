# SPDX-License-Identifier: AGPL-3.0-only

"""Provision new, independently owned local databases; never modify existing ones."""

import re
from dataclasses import dataclass, field
from getpass import getpass
from typing import Any

import psycopg
from psycopg import sql

TEST_DATABASE_MARKER = "FDS disposable integration test database v1"
LOOPBACK = {"127.0.0.1", "localhost", "::1"}


@dataclass(frozen=True)
class DatabaseSpec:
    name: str
    role: str
    password: str = field(repr=False)
    testing: bool = False


def validate_specs(specs: list[DatabaseSpec]) -> None:
    names = [spec.name for spec in specs]
    roles = [spec.role for spec in specs]
    if len(set(names)) != len(names) or len(set(roles)) != len(roles):
        raise ValueError("Database names and roles must be distinct")
    if len({spec.password for spec in specs}) != len(specs):
        raise ValueError("Database passwords must be independent")
    for spec in specs:
        for identifier in (spec.name, spec.role):
            if not re.fullmatch(r"[a-z][a-z0-9_]{0,62}", identifier):
                raise ValueError("Use simple lowercase PostgreSQL identifiers")
        if spec.name in {"postgres", "template0", "template1"} or spec.role.startswith(
            "pg_"
        ):
            raise ValueError("Reserved database or role name")
        if len(spec.password) < 24 or not spec.password.strip():
            raise ValueError(
                "Use an independently generated password of 24+ characters"
            )


def provision(
    conn: psycopg.Connection[tuple[Any, ...]], specs: list[DatabaseSpec]
) -> None:
    validate_specs(specs)
    if not conn.autocommit:
        raise ValueError("Provisioning requires autocommit")
    # Preflight every requested object before making any changes.
    for spec in specs:
        database_exists = conn.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s", (spec.name,)
        ).fetchone()
        role_exists = conn.execute(
            "SELECT 1 FROM pg_roles WHERE rolname = %s", (spec.role,)
        ).fetchone()
        if database_exists or role_exists:
            raise ValueError(
                "A requested database or role already exists; refusing changes"
            )
    for spec in specs:
        role = sql.Identifier(spec.role)
        database = sql.Identifier(spec.name)
        # Send a SCRAM verifier rather than a plaintext password in SQL.
        verifier = conn.pgconn.encrypt_password(
            spec.password.encode(), spec.role.encode(), b"scram-sha-256"
        ).decode()
        conn.execute(
            sql.SQL(
                "CREATE ROLE {} LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE "
                "NOREPLICATION NOBYPASSRLS PASSWORD {}"
            ).format(role, sql.Literal(verifier))
        )
        conn.execute(sql.SQL("CREATE DATABASE {} OWNER {}").format(database, role))
        conn.execute(sql.SQL("REVOKE ALL ON DATABASE {} FROM PUBLIC").format(database))
        if spec.testing:
            conn.execute(
                sql.SQL("COMMENT ON DATABASE {} IS {}").format(
                    database, sql.Literal(TEST_DATABASE_MARKER)
                )
            )


def prompt_spec(label: str, *, testing: bool = False) -> DatabaseSpec:
    name = input(f"{label} database name: ").strip()
    role = input(f"{label} role name: ").strip()
    password = getpass(f"{label} role password (from private configuration): ")
    if password != getpass("Repeat password: "):
        raise ValueError("Passwords differ")
    return DatabaseSpec(name, role, password, testing)


def main() -> int:
    try:
        host = input("PostgreSQL loopback host [127.0.0.1]: ").strip() or "127.0.0.1"
        if host not in LOOPBACK:
            raise ValueError("Only loopback hosts are supported")
        port = int(input("PostgreSQL port [5432]: ").strip() or "5432")
        if not 1 <= port <= 65535:
            raise ValueError("Invalid port")
        admin = input("Bootstrap administrator role: ").strip()
        password = getpass("Bootstrap administrator password: ")
        specs = [prompt_spec("Development"), prompt_spec("Testing", testing=True)]
        validate_specs(specs)
        if password in {spec.password for spec in specs}:
            raise ValueError("Administrator and application passwords must differ")
        if input("Create both NEW databases and roles? [y/N]: ").lower() != "y":
            return 1
        with psycopg.connect(
            host=host,
            port=port,
            dbname="postgres",
            user=admin,
            password=password,
            autocommit=True,
            connect_timeout=5,
        ) as conn:
            provision(conn, specs)
    except (ValueError, psycopg.Error, EOFError, KeyboardInterrupt) as exc:
        # Avoid echoing SQL, connection parameters or password verifiers.
        if isinstance(exc, psycopg.Error):
            print(f"PostgreSQL error: {type(exc).__name__}")
            print(f"SQLSTATE: {exc.sqlstate or 'unavailable'}")
        elif isinstance(exc, (EOFError, KeyboardInterrupt)):
            print("Provisioning cancelled.")
        else:
            print("Invalid provisioning configuration or existing objects.")
        print("If partially created, inspect the new roles/databases before retrying.")
        return 1
    print("Development and dedicated testing databases provisioned.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
