# SPDX-License-Identifier: AGPL-3.0-only

import pytest

from fantacalciodummysystem import main


def test_main_prints_scaffold_message(capsys: pytest.CaptureFixture[str]) -> None:
    main()

    captured = capsys.readouterr()
    assert captured.out == "Hello from fantacalciodummysystem!\n"
    assert captured.err == ""
