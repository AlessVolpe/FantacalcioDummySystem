# SPDX-License-Identifier: AGPL-3.0-only

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import timedelta
from ipaddress import ip_address

from django.conf import settings
from django.db import transaction
from django.http import HttpRequest
from django.utils import timezone
from django.utils.crypto import salted_hmac

from .models import AuthThrottle


def client_ip(request: HttpRequest) -> str:
    # Trust only the direct peer. Proxy integration is a deployment decision.
    try:
        address = ip_address(request.META.get("REMOTE_ADDR", ""))
    except ValueError:
        return "unknown"
    if address.version == 6:
        mapped = getattr(address, "ipv4_mapped", None)
        if mapped is not None:
            return str(mapped)
    return str(address)


def bucket(scope: str, identity: str, seconds: int) -> AuthThrottle:
    key = salted_hmac(
        "fds.auth.throttle", f"{scope}:{identity}", algorithm="sha256"
    ).hexdigest()
    now = timezone.now()
    row, _ = AuthThrottle.objects.select_for_update().get_or_create(
        key=key, defaults={"expires_at": now + timedelta(seconds=seconds)}
    )
    if row.expires_at <= now:
        row.count = 0
        row.expires_at = now + timedelta(seconds=seconds)
        row.save(update_fields=["count", "expires_at"])
    return row


def increment(row: AuthThrottle) -> None:
    row.count += 1
    row.save(update_fields=["count"])


def take(scope: str, identity: str, limit: int, seconds: int) -> bool:
    with transaction.atomic():
        row = bucket(scope, identity, seconds)
        if row.count >= limit:
            return False
        increment(row)
        return True


def mail_budget(scope: str, request: HttpRequest, email: str) -> tuple[bool, bool]:
    email_limit, ip_limit, seconds = settings.FDS_AUTH_LIMITS[scope]
    if not take(f"{scope}:ip", client_ip(request), ip_limit, seconds):
        return False, False
    return True, take(f"{scope}:email", email, email_limit, seconds)


def token_budget(request: HttpRequest) -> bool:
    _, limit, seconds = settings.FDS_AUTH_LIMITS["token"]
    return take("token:ip", client_ip(request), limit, seconds)


@dataclass
class LoginBudget:
    allowed: bool
    succeeded: bool = False


@contextmanager
def login_budget(request: HttpRequest, email: str) -> Iterator[LoginBudget]:
    # Keep both row locks until the authentication result is known. Count only
    # failures, including disabled/unverified accounts, irrespective of existence.
    email_limit, ip_limit, seconds = settings.FDS_AUTH_LIMITS["login"]
    with transaction.atomic():
        ip_row = bucket("login:ip", client_ip(request), seconds)
        if ip_row.count >= ip_limit:
            yield LoginBudget(False)
            return
        email_row = bucket("login:email", email, seconds)
        if email_row.count >= email_limit:
            increment(ip_row)
            yield LoginBudget(False)
            return
        budget = LoginBudget(True)
        yield budget
        if not budget.succeeded:
            increment(ip_row)
            increment(email_row)
