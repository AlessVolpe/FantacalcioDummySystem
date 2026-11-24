# SPDX-License-Identifier: AGPL-3.0-only

import os
import sys

from django.core.management import execute_from_command_line


def main() -> None:
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE", "fantacalciodummysystem.config.settings.development"
    )
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
