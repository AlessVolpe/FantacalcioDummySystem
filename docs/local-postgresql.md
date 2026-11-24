# Private local PostgreSQL setup

Use either native PostgreSQL (target major version 18) or the supplied local
Compose service. Both use the same Django settings and SQL provisioning
procedure. Native PostgreSQL is not started by Compose. Run Python on the host
with uv. Do not use a production instance or real competition data here.

## 1. Prepare private files

From the repository root (PowerShell):

```powershell
Copy-Item examples/.env.development.example .env.development
Copy-Item examples/.env.testing.example .env.testing
```

These files are ignored by Git. Open them locally in an editor, never a public
PR, chat, screenshot or terminal recording. Choose two distinct role names,
two distinct database names and two independently generated passwords. Use a
password manager or Python's `secrets.token_urlsafe(48)` to generate passwords.
Use a separate `secrets.token_urlsafe(64)` value for `FDS_DEV_SECRET_KEY`.
Record them in the corresponding private files; do not commit them or use any
value previously published in the repository. Keep private files outside any
untrusted sync/backup location where possible and restrict filesystem access.

`FDS_DEV_DB_HOST` and `FDS_TEST_DB_HOST` should be `127.0.0.1`; set the port to
that of your selected local PostgreSQL server. Host and port are configuration,
not credentials. All settings are mandatory. Environment variables already set
in the shell can override values loaded by uv; avoid stale variables and do not
export production settings in a development shell.

```sh
git check-ignore .env.development .env.testing
```

Both paths must be listed. Never use `git add -f` for private configuration.

## 2A. Native PostgreSQL on Windows

Start the installed PostgreSQL service if necessary, using Windows Services.
Open SQL Shell (psql), or run `psql` from its installation's `bin` directory.
Connect to the local administrative database (normally `postgres`) using the
existing administrator account, with the password prompt (`-W`):

```sh
psql -h 127.0.0.1 -p 5432 -U postgres -d postgres -W
```

Adjust the port and administrator role for your installation. The role above
is a conventional installer default, not an application credential. In psql,
run `SHOW server_version;`, `SHOW port;`, `SHOW listen_addresses;` and
`SHOW hba_file;`. Confirm local TCP authentication uses SCRAM-SHA-256 for the
application roles; do not configure `trust` or expose the service publicly.
Review the actual `pg_hba.conf` and its first matching rules before making
changes. If other services use the cluster, avoid blanket changes to them.
Then continue with section 3.

## 2B. Docker Compose alternative

If using Compose instead, copy the blank bootstrap template and create an
ignored password file (PowerShell):

```powershell
Copy-Item examples/.env.postgres.example .env.postgres
New-Item -ItemType Directory -Force secrets
New-Item -ItemType File secrets/postgres-admin-password
```

Edit `.env.postgres` privately: choose a bootstrap administrator role and a free
loopback host port (e.g. 55432 if native PostgreSQL occupies 5432). Put a newly
generated bootstrap password, and nothing else, in
`secrets/postgres-admin-password`. Do not reuse it as an application password.
Check that both private paths are ignored:

```sh
git check-ignore .env.postgres secrets/postgres-admin-password
docker compose --env-file .env.postgres up -d
docker compose --env-file .env.postgres ps
```

The image initializes its database only when the volume is empty. Editing the
bootstrap files later does not rotate an existing database role. The password
is mounted as a Compose secret, not passed in a command-line argument. Local
Docker administrators can still access the server and its mounted secret.
Compose is a local service, not a production deployment.

Connect with psql from the host using the selected host port and bootstrap
role, or use the container's psql:

```sh
docker compose --env-file .env.postgres exec postgres psql -U YOUR_BOOTSTRAP_ROLE -d postgres -W
```

Replace `YOUR_BOOTSTRAP_ROLE` locally with your selected role. Enter the
password at the prompt, not in the command. Continue with section 3.

To stop the service without deleting data, use
`docker compose --env-file .env.postgres down`. Do not add `-v` unless you
intend to permanently delete its database volume.

## 3. Provision independent application roles and databases

Run the following in the administrator's **psql** session, not in an ordinary
shell. Choose the private names already recorded in the two environment files.
Use simple lowercase identifiers (letters, digits, underscores; begin with a
letter) and distinct names. PostgreSQL quotes identifiers through psql's
`:"variable"` interpolation. `\password` prompts without putting a plaintext
password in SQL history. Enter the corresponding generated password twice.

```sql
\prompt 'Development role name: ' dev_role
\prompt 'Development database name: ' dev_db
\prompt 'Testing role name: ' test_role
\prompt 'Testing database name: ' test_db
SET password_encryption = 'scram-sha-256'; -- pragma: allowlist secret
CREATE ROLE :"dev_role" LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
\password :dev_role
CREATE ROLE :"test_role" LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
\password :test_role
CREATE DATABASE :"dev_db" OWNER :"dev_role";
CREATE DATABASE :"test_db" OWNER :"test_role";
REVOKE ALL ON DATABASE :"dev_db" FROM PUBLIC;
REVOKE ALL ON DATABASE :"test_db" FROM PUBLIC;
\du
\l
\q
```

The database owner can migrate its own dedicated database (PostgreSQL 15+
public schema default ownership). Do not grant superuser or `CREATEDB` to these
roles. Revoking PUBLIC access isolates these two databases from each other's
roles; unrelated existing databases may have their own PUBLIC grants, which
must be reviewed if using a shared cluster. This is one-time provisioning; do
not rerun against existing roles blindly. Do not change unrelated data or
roles.

The test database is reserved for the next PR. Django normally creates a
separate test database. The persistence PR must explicitly handle its lifecycle
without granting unrestricted database creation on the native cluster; do not
run database-dependent pytest tests until that design is implemented.

## 4. Check private configuration and connectivity

Run database-free checks without any env file:

```sh
uv sync --locked
uv run --locked python manage.py check --settings=fantacalciodummysystem.config.settings.static
uv run --locked mypy
uv run --locked pytest
```

Then verify that both independent profiles can authenticate (from the repository
root). The commands print only a fixed success message, not credentials:

```sh
uv run --locked --env-file .env.development python manage.py shell --settings=fantacalciodummysystem.config.settings.development -c "from django.db import connection; connection.ensure_connection(); print('Development connection OK')"
uv run --locked --env-file .env.testing python manage.py shell --settings=fantacalciodummysystem.config.settings.testing -c "from django.db import connection; connection.ensure_connection(); print('Testing connection OK')"
```

Check the initial migration against the development database:

```sh
uv run --locked --env-file .env.development python manage.py makemigrations --check --dry-run --settings=fantacalciodummysystem.config.settings.development
```

Expected: `No changes detected`. If desired, apply the migration only to the
new disposable development database after checking its identity:

```sh
uv run --locked --env-file .env.development python manage.py migrate --plan --settings=fantacalciodummysystem.config.settings.development
uv run --locked --env-file .env.development python manage.py migrate --settings=fantacalciodummysystem.config.settings.development
```

Never run migrations against a database with existing important data during
this phase. The next PR will make migration execution and constraint checks
required against real PostgreSQL. Production deployment and privilege grants
are deliberately not implemented yet.
