# SPDX-License-Identifier: AGPL-3.0-only

"""Validate the generated OpenAPI document and fail on committed schema drift."""

import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "docs" / "openapi-v1.yaml"
SETTINGS = "fantacalciodummysystem.config.settings.static"


def main() -> int:
    if not SCHEMA.is_file():
        print("Missing docs/openapi-v1.yaml; generate and commit the schema.")
        return 1
    with TemporaryDirectory() as tmp:
        generated = Path(tmp) / "openapi.yaml"
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "manage.py"),
                "spectacular",
                f"--settings={SETTINGS}",
                "--validate",
                "--fail-on-warn",
                "--file",
                str(generated),
            ],
            cwd=ROOT,
            check=False,
            timeout=120,
        )
        if result.returncode:
            return result.returncode
        # read_text normalizes LF and CRLF across Windows and Linux.
        if generated.read_text(encoding="utf-8") != SCHEMA.read_text(encoding="utf-8"):
            print("OpenAPI schema drift; regenerate docs/openapi-v1.yaml.")
            return 1
    print("OpenAPI schema is valid and matches the committed contract.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
