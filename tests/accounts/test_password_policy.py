# SPDX-License-Identifier: AGPL-3.0-only

from secrets import token_urlsafe

import pytest
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from fantacalciodummysystem.accounts.models import User


def test_generated_passwords_and_whitespace() -> None:
    user = User(email="person@example.com", display_name="Person")
    for password in (token_urlsafe(64), "  " + token_urlsafe(90) + " é  "):
        validate_password(password, user)
        user.set_password(password)
        assert user.check_password(password)
        if password != password.strip():
            assert not user.check_password(password.strip())


@pytest.mark.parametrize("length", [11, 129])
def test_password_length_bounds(length: int) -> None:
    password = token_urlsafe(100)[:length]
    with pytest.raises(ValidationError):
        validate_password(password)


def test_password_maximum_is_accepted() -> None:
    validate_password(token_urlsafe(100)[:128])
