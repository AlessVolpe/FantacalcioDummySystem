# SPDX-License-Identifier: AGPL-3.0-only

from secrets import token_urlsafe
from typing import Any

import pytest
from django.test import Client
from django.utils import timezone

from fantacalciodummysystem.accounts.models import User
from fantacalciodummysystem.api.problems import MEDIA_TYPE

pytestmark = [pytest.mark.integration, pytest.mark.django_db]
BASE = "/api/v1/"


def login(browser: Client) -> User:
    password = token_urlsafe(32)
    user = User.objects.create_user(
        "profile@example.com",
        password,
        display_name="Original",
        email_verified_at=timezone.now(),
    )
    csrf = browser.get(BASE + "auth/csrf/").json()["csrfToken"]
    response = browser.post(
        BASE + "auth/login/",
        {"email": user.email, "password": password},
        content_type="application/json",
        HTTP_X_CSRFTOKEN=csrf,
    )
    assert response.status_code == 204
    return user


def test_profile_update_is_private_and_csrf_protected() -> None:
    browser = Client(enforce_csrf_checks=True)
    user = login(browser)
    other = User.objects.create_user("other@example.com", display_name="Other")
    route = BASE + "auth/me/"
    assert (
        browser.patch(
            route, {"display_name": "Changed"}, content_type="application/json"
        ).status_code
        == 403
    )
    csrf = browser.get(BASE + "auth/csrf/").json()["csrfToken"]
    response = browser.patch(
        route,
        {"display_name": "  Changed é  "},
        content_type="application/json",
        HTTP_X_CSRFTOKEN=csrf,
    )
    assert response.status_code == 200
    assert response.json() == {
        "id": str(user.pk),
        "email": user.email,
        "display_name": "Changed é",
    }
    assert browser.get(route).json() == response.json()
    user.refresh_from_db()
    other.refresh_from_db()
    assert user.display_name == "Changed é"
    assert other.display_name == "Other"
    assert not user.is_staff
    assert response["Cache-Control"] == "no-store"


@pytest.mark.parametrize(
    "body",
    [
        {"display_name": "Name", "is_staff": True},
        {"email": "evil@example.com"},
        {"display_name": 123},
    ],
)
def test_profile_rejects_mass_assignment(body: dict[str, Any]) -> None:
    browser = Client(enforce_csrf_checks=True)
    user = login(browser)
    csrf = browser.get(BASE + "auth/csrf/").json()["csrfToken"]
    response = browser.patch(
        BASE + "auth/me/", body, content_type="application/json", HTTP_X_CSRFTOKEN=csrf
    )
    assert response.status_code == 400
    assert response["Content-Type"] == MEDIA_TYPE
    assert response.json()["code"] == "validation_error"
    user.refresh_from_db()
    assert user.display_name == "Original"
    assert not user.is_staff


def test_profile_requires_json_and_authentication() -> None:
    browser = Client(enforce_csrf_checks=True)
    login(browser)
    csrf = browser.get(BASE + "auth/csrf/").json()["csrfToken"]
    response = browser.patch(
        BASE + "auth/me/",
        "display_name=Name",
        content_type="application/x-www-form-urlencoded",
        HTTP_X_CSRFTOKEN=csrf,
    )
    assert response.status_code == 415
    assert response["Content-Type"] == MEDIA_TYPE
    anonymous = Client()
    assert (
        anonymous.patch(
            BASE + "auth/me/", {"display_name": "Name"}, content_type="application/json"
        ).status_code
        == 403
    )


def test_database_readiness(client: Client) -> None:
    response = client.get(BASE + "health/ready/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
