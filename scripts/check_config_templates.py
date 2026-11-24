# SPDX-License-Identifier: AGPL-3.0-only

import re
import sys
from pathlib import Path


def main() -> int:
    failed = False
    for filename in sys.argv[1:]:
        for number, line in enumerate(
            Path(filename).read_text(encoding="utf-8").splitlines(), start=1
        ):
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            if not re.fullmatch(r"[A-Z][A-Z0-9_]*=", line):
                print(f"{filename}:{number}: configuration template must be blank")
                failed = True
    return int(failed)


if __name__ == "__main__":
    sys.exit(main())
