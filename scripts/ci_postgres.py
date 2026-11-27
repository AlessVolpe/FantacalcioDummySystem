# SPDX-License-Identifier: AGPL-3.0-only

"""Start and destroy a job-local PostgreSQL cluster on GitHub-hosted runners."""

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from secrets import token_hex, token_urlsafe

import psycopg

from scripts.provision_test_database import DatabaseSpec, provision

PORT = 55432
CONTAINER = "fds-postgres-ci"
IMAGE = "postgres:19.0"


def run(*args: str, env: dict[str, str] | None = None) -> None:
    # Do not forward subprocess output: provisioning errors can contain secrets.
    subprocess.run(args, env=env, check=True, capture_output=True, timeout=300)


def windows_bin(temp: Path, name: str) -> str:
    return str(temp / "fds-pg" / "pgsql" / "bin" / f"{name}.exe")


def start(temp: Path) -> None:
    admin = f"bootstrap_{token_hex(8)}"
    admin_password = token_urlsafe(48)
    spec = DatabaseSpec(
        f"fds_test_{token_hex(8)}", f"tester_{token_hex(8)}", token_urlsafe(48), True
    )
    for secret in (admin_password, spec.password):
        print(f"::add-mask::{secret}", flush=True)
    if sys.platform == "win32":
        pwfile = temp / "fds-pg-password"
        try:
            with pwfile.open("x", encoding="ascii") as stream:
                stream.write(admin_password + "\n")
            run(
                windows_bin(temp, "initdb"),
                "-D",
                str(temp / "fds-pg-data"),
                "-U",
                admin,
                "--auth=scram-sha-256",
                "--encoding=UTF8",
                "--no-locale",
                f"--pwfile={pwfile}",
            )
        finally:
            pwfile.unlink(missing_ok=True)
        run(
            windows_bin(temp, "pg_ctl"),
            "-D",
            str(temp / "fds-pg-data"),
            "-l",
            str(temp / "fds-pg.log"),
            "-o",
            f"-h 127.0.0.1 -p {PORT}",
            "-w",
            "start",
        )
    elif sys.platform == "linux":
        env = os.environ.copy()
        env.update(POSTGRES_USER=admin, POSTGRES_PASSWORD=admin_password)
        run(
            "docker",
            "run",
            "--detach",
            "--name",
            CONTAINER,
            "--publish",
            f"127.0.0.1:{PORT}:5432",
            "--env",
            "POSTGRES_USER",
            "--env",
            "POSTGRES_PASSWORD",
            "--env",
            "POSTGRES_DB=postgres",
            "--env",
            "POSTGRES_INITDB_ARGS=--auth-host=scram-sha-256 --auth-local=scram-sha-256",
            IMAGE,
            env=env,
        )
    else:
        raise ValueError("Unsupported runner")

    for attempt in range(60):
        try:
            conn = psycopg.connect(
                host="127.0.0.1",
                port=PORT,
                dbname="postgres",
                user=admin,
                password=admin_password,
                autocommit=True,
                connect_timeout=2,
            )
        except psycopg.OperationalError:
            if attempt == 59:
                raise
            time.sleep(1)
        else:
            break
    else:
        raise RuntimeError("PostgreSQL did not become ready")
    with conn:
        if conn.info.server_version // 10000 != 19:
            raise ValueError("CI requires PostgreSQL 19")
        provision(conn, [spec])
    config = {
        "NAME": spec.name,
        "USER": spec.role,
        "PASSWORD": spec.password,
        "HOST": "127.0.0.1",
        "PORT": str(PORT),
    }
    with Path(os.environ["GITHUB_ENV"]).open("a", encoding="utf-8") as output:
        for key, value in config.items():
            output.write(f"FDS_TEST_DB_{key}={value}\n")
    print("PostgreSQL 19 is ready; dedicated restricted test role provisioned.")


def stop(temp: Path) -> None:
    if sys.platform == "win32":
        data = temp / "fds-pg-data"
        if (data / "postmaster.pid").exists():
            run(
                windows_bin(temp, "pg_ctl"), "-D", str(data), "-m", "fast", "-w", "stop"
            )
        if data.exists():
            shutil.rmtree(data)
    elif sys.platform == "linux":
        result = subprocess.run(
            [
                "docker",
                "ps",
                "-a",
                "--filter",
                f"name=^/{CONTAINER}$",
                "--format",
                "{{.Names}}",
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if CONTAINER in result.stdout.splitlines():
            run("docker", "rm", "-f", "-v", CONTAINER)


def main() -> int:
    if os.environ.get("GITHUB_ACTIONS") != "true" or len(sys.argv) != 2:
        return 1
    temp = Path(os.environ["RUNNER_TEMP"])
    try:
        if sys.argv[1] == "start":
            start(temp)
        elif sys.argv[1] == "stop":
            stop(temp)
        else:
            return 1
    except (
        OSError,
        ValueError,
        RuntimeError,
        psycopg.Error,
        subprocess.SubprocessError,
    ) as exc:
        # Never log raw exceptions, subprocess arguments or captured output.
        print(f"PostgreSQL CI {sys.argv[1]} failed: {type(exc).__name__}")
        if isinstance(exc, psycopg.Error):
            print(f"SQLSTATE: {exc.sqlstate or 'unavailable'}")
        elif isinstance(exc, subprocess.CalledProcessError):
            print(f"Subprocess exit code: {exc.returncode}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
