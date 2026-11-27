# SPDX-License-Identifier: AGPL-3.0-only

from typing import Any

from django.core.management import BaseCommand, call_command
from django.utils import timezone

from ...models import AccountToken, AuthThrottle


class Command(BaseCommand):
    help = "Remove expired account tokens, throttles and Django sessions."

    def handle(self, *args: Any, **options: Any) -> None:
        now = timezone.now()
        AccountToken.objects.filter(expires_at__lte=now).delete()
        AuthThrottle.objects.filter(expires_at__lte=now).delete()
        call_command("clearsessions")
        self.stdout.write("Expired authentication state removed.")
