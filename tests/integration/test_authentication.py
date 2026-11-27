# SPDX-License-Identifier: AGPL-3.0-only

from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from secrets import token_urlsafe
from threading import Barrier
from typing import Any, cast

import pytest
from django.contrib.auth import SESSION_KEY
from django.core import mail
from django.core.mail import EmailMessage
from django.core.management import call_command
from django.db import connections
from django.test import Client, override_settings
from django.utils import timezone

from fantacalciodummysystem.accounts import lifecycle, throttles
from fantacalciodummysystem.accounts.models import AccountToken, AuthThrottle, User
from fantacalciodummysystem.accounts.sessions import SEEN, START

pytestmark = [pytest.mark.integration, pytest.mark.django_db]
BASE = "/api/v1/auth/"


def post(client: Client, endpoint: str, **data: str) -> Any:
    return client.post(BASE + endpoint + "/", data, content_type="application/json")


def outbox() -> list[EmailMessage]:
    return cast(list[EmailMessage], getattr(mail, "outbox", []))


def latest_token() -> str:
    return str(outbox()[-1].body).split("#token=", 1)[1].split()[0]


def verified() -> tuple[User, str]:
    password = token_urlsafe(32)
    user = User.objects.create_user(
        "member@example.com",
        password,
        display_name="Member",
        email_verified_at=timezone.now(),
    )
    return user, password


def test_email_first_registration_and_replay(client: Client) -> None:
    password = "  " + token_urlsafe(64) + " é  "
    assert post(client, "register", email=" NEW@Example.COM ").status_code == 202
    assert not User.objects.exists()
    first = latest_token()
    assert post(client, "resend", email="new@example.com").status_code == 202
    second = latest_token()
    assert first != second
    assert AccountToken.objects.get().digest == lifecycle.digest(second)
    response = post(
        client, "verify", token=first, display_name="New", password=password
    )
    assert response.status_code == 400
    assert client.get(BASE + "verify/").status_code == 405
    response = post(
        client, "verify", token=second, display_name="New", password=password
    )
    assert response.status_code == 201
    response = post(
        client, "verify", token=second, display_name="New", password=password
    )
    assert response.status_code == 400
    user = User.objects.get()
    assert user.email_verified_at is not None
    assert user.check_password(password)
    assert not AccountToken.objects.exists()
    assert client.get(BASE + "me/").status_code == 403
    assert post(client, "login", email=user.email, password=password).status_code == 204
    assert client.get(BASE + "me/").json()["id"] == str(user.pk)


def test_csrf_and_session_rotation() -> None:
    user, password = verified()
    browser = Client(enforce_csrf_checks=True)
    response = post(browser, "login", email=user.email, password=password)
    assert response.status_code == 403
    assert post(browser, "register", email="new@example.com").status_code == 403
    session = browser.session
    session["anonymous"] = True
    session.save()
    before = session.session_key
    csrf = browser.get(BASE + "csrf/").json()["csrfToken"]
    response = browser.post(
        BASE + "login/",
        {"email": user.email, "password": password},
        content_type="application/json",
        HTTP_X_CSRFTOKEN=csrf,
    )
    assert response.status_code == 204
    assert browser.session.session_key != before
    assert browser.session[SESSION_KEY] == str(user.pk)
    assert post(browser, "logout").status_code == 403
    csrf = browser.get(BASE + "csrf/").json()["csrfToken"]
    assert browser.post(BASE + "logout/", HTTP_X_CSRFTOKEN=csrf).status_code == 204
    assert browser.get(BASE + "me/").status_code == 403


@pytest.mark.parametrize("key,seconds", [(START, 7 * 86400), (SEEN, 86400)])
def test_session_expiration(client: Client, key: str, seconds: int) -> None:
    user, password = verified()
    assert post(client, "login", email=user.email, password=password).status_code == 204
    session = client.session
    session[key] -= seconds
    session.save()
    assert client.get(BASE + "me/").status_code == 403


def test_reset_expiration_and_session_revocation(client: Client) -> None:
    user, password = verified()
    other = Client()
    for browser in (client, other):
        response = post(browser, "login", email=user.email, password=password)
        assert response.status_code == 204
    assert post(client, "password/reset", email=user.email).status_code == 202
    expired = latest_token()
    AccountToken.objects.update(expires_at=timezone.now() - timedelta(seconds=1))
    replacement = token_urlsafe(32)
    response = post(client, "password/confirm", token=expired, password=replacement)
    assert response.status_code == 400
    assert post(client, "password/reset", email=user.email).status_code == 202
    token = latest_token()
    response = post(
        client, "verify", token=token, display_name="Wrong", password=replacement
    )
    assert response.status_code == 400
    response = post(client, "password/confirm", token=token, password=replacement)
    assert response.status_code == 204
    response = post(client, "password/confirm", token=token, password=password)
    assert response.status_code == 400
    for browser in (client, other):
        assert browser.get(BASE + "me/").status_code == 403
    assert post(client, "login", email=user.email, password=password).status_code == 403
    response = post(client, "login", email=user.email, password=replacement)
    assert response.status_code == 204


def test_password_change_preserves_current_session(client: Client) -> None:
    user, password = verified()
    other = Client()
    for browser in (client, other):
        response = post(browser, "login", email=user.email, password=password)
        assert response.status_code == 204
    assert post(client, "password/reset", email=user.email).status_code == 202
    token = latest_token()
    replacement = token_urlsafe(32)
    response = post(
        client, "password/change", current_password=password, password=replacement
    )
    assert response.status_code == 204
    assert client.get(BASE + "me/").status_code == 200
    assert other.get(BASE + "me/").status_code == 403
    response = post(client, "password/confirm", token=token, password=password)
    assert response.status_code == 400


def test_mail_enumeration_and_login_throttle(client: Client) -> None:
    user, password = verified()
    existing = post(client, "register", email=user.email)
    absent = post(client, "register", email="absent@example.com")
    assert existing.status_code == absent.status_code == 202
    assert existing.json() == absent.json()
    assert len(outbox()) == 1
    for _ in range(5):
        response = post(client, "login", email=user.email, password=token_urlsafe(32))
        assert response.status_code == 403
    assert post(client, "login", email=user.email, password=password).status_code == 429
    AuthThrottle.objects.update(expires_at=timezone.now() - timedelta(seconds=1))
    assert post(client, "login", email=user.email, password=password).status_code == 204


def test_mail_budget_and_cleanup(client: Client) -> None:
    for _ in range(4):
        assert post(client, "resend", email="new@example.com").status_code == 202
    assert len(outbox()) == 3
    AccountToken.objects.update(expires_at=timezone.now() - timedelta(seconds=1))
    AuthThrottle.objects.update(expires_at=timezone.now() - timedelta(seconds=1))
    call_command("cleanup_auth")
    assert not AccountToken.objects.exists()
    assert not AuthThrottle.objects.exists()


def test_disabled_and_unverified_users(client: Client) -> None:
    user, password = verified()
    user.is_active = False
    user.save(update_fields=["is_active"])
    assert post(client, "login", email=user.email, password=password).status_code == 403
    assert post(client, "password/reset", email=user.email).status_code == 202
    assert not AccountToken.objects.exists()
    user.is_active = True
    user.email_verified_at = None
    user.save(update_fields=["is_active", "email_verified_at"])
    assert post(client, "login", email=user.email, password=password).status_code == 403


@pytest.mark.django_db(transaction=True)
def test_concurrent_token_consumption() -> None:
    lifecycle.issue("race@example.com", lifecycle.REGISTER)
    token = latest_token()
    barrier = Barrier(2)

    def consume() -> bool:
        try:
            barrier.wait(timeout=15)
            return lifecycle.register(token, "Race", token_urlsafe(32))
        finally:
            connections.close_all()

    with ThreadPoolExecutor(max_workers=2) as pool:
        one = pool.submit(consume)
        two = pool.submit(consume)
        assert sorted([one.result(timeout=30), two.result(timeout=30)]) == [False, True]
    assert User.objects.filter(email="race@example.com").count() == 1


def test_email_gate_and_completion_page(client: Client) -> None:
    response = client.get("/auth/register/")
    assert response.status_code == 200
    assert b'autocomplete="new-password"' in response.content
    assert "default-src 'none'" in response["Content-Security-Policy"]
    assert not AccountToken.objects.exists()
    with override_settings(FDS_AUTH_EMAIL_ENABLED=False):
        assert post(client, "register", email="new@example.com").status_code == 503
        assert client.get("/auth/register/").status_code == 503
    assert not AccountToken.objects.exists()


def test_admin_disable_revokes_session_even_after_reactivation(client: Client) -> None:
    user, password = verified()
    admin_password = token_urlsafe(32)
    admin = User.objects.create_superuser(
        "admin@example.com", admin_password, display_name="Admin"
    )
    assert post(client, "login", email=user.email, password=password).status_code == 204
    staff = Client()
    response = post(staff, "login", email=admin.email, password=admin_password)
    assert response.status_code == 204
    url = f"/admin/accounts/user/{user.pk}/change/"
    assert staff.get(url).status_code == 200
    assert staff.post(url, {"_save": "Save"}).status_code == 302
    user.refresh_from_db()
    assert not user.is_active
    assert staff.post(url, {"is_active": "on", "_save": "Save"}).status_code == 302
    assert User.objects.get(pk=user.pk).is_active
    assert client.get(BASE + "me/").status_code == 403


def test_registration_expiration_and_invalid_password(client: Client) -> None:
    assert post(client, "register", email="new@example.com").status_code == 202
    token = latest_token()
    response = post(client, "verify", token=token, display_name="New", password="x")
    assert response.status_code == 400
    assert AccountToken.objects.exists()
    AccountToken.objects.update(expires_at=timezone.now() - timedelta(seconds=1))
    response = post(
        client, "verify", token=token, display_name="New", password=token_urlsafe(32)
    )
    assert response.status_code == 400
    assert not User.objects.exists()


def test_delivery_failure_has_generic_response(
    client: Client, monkeypatch: pytest.MonkeyPatch
) -> None:
    def unavailable(*args: object, **kwargs: object) -> int:
        raise OSError("Simulated mail failure")

    monkeypatch.setattr(lifecycle, "send_mail", unavailable)
    response = post(client, "register", email="new@example.com")
    assert response.status_code == 202
    assert response.json() == {"status": "accepted"}
    assert not User.objects.exists()
    assert AccountToken.objects.exists()


@pytest.mark.django_db(transaction=True)
def test_concurrent_throttle_consumption() -> None:
    barrier = Barrier(2)

    def consume() -> bool:
        try:
            barrier.wait(timeout=15)
            return throttles.take("probe", "synthetic", 1, 900)
        finally:
            connections.close_all()

    with ThreadPoolExecutor(max_workers=2) as pool:
        one = pool.submit(consume)
        two = pool.submit(consume)
        assert sorted([one.result(timeout=30), two.result(timeout=30)]) == [False, True]
