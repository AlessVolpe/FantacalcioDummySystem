# SPDX-License-Identifier: AGPL-3.0-only

from secrets import token_urlsafe

import pytest

from scripts.provision_test_database import DatabaseSpec, validate_specs


def test_distinct_valid_database_specs() -> None:
    validate_specs(
        [
            DatabaseSpec("development", "developer", token_urlsafe(32)),
            DatabaseSpec("testing", "tester", token_urlsafe(32), True),
        ]
    )


@pytest.mark.parametrize("name", ["postgres", "template0", "bad-name", "A", "x" * 64])
def test_invalid_database_name(name: str) -> None:
    with pytest.raises(ValueError):
        validate_specs([DatabaseSpec(name, "tester", token_urlsafe(32), True)])


def test_shared_role_or_password_is_rejected() -> None:
    password = token_urlsafe(32)
    first = DatabaseSpec("development", "developer", password)
    with pytest.raises(ValueError):
        validate_specs([first, DatabaseSpec("testing", "developer", token_urlsafe(32))])
    with pytest.raises(ValueError):
        validate_specs([first, DatabaseSpec("testing", "tester", password)])
