"""Validation tests for the /install endpoint helper.
The actual pip call is NOT exercised here — that's covered by an
integration test in CI when needed (slow + network)."""
from __future__ import annotations

import pytest

from app.install import _validate


@pytest.mark.parametrize("ok", [
    "torch",
    "pandas matplotlib",
    "numpy==1.26.4",
    "pillow opencv-python",
    "scikit-learn>=1.3",
    "transformers,accelerate",
    "git+https://github.com/owner/repo.git@v1",  # supported via PIP_RE chars
])
def test_validate_accepts_reasonable_inputs(ok: str):
    out = _validate(ok)
    assert out, ok


@pytest.mark.parametrize("bad", [
    "requests; rm -rf /",
    "pkg && other",
    "pkg | other",
    "pkg `cat /etc/passwd`",
    "pkg $(whoami)",
    "",
    "   ",
])
def test_validate_rejects_shell_injection(bad: str):
    with pytest.raises(ValueError):
        _validate(bad)


def test_validate_splits_on_commas_and_whitespace():
    assert _validate("a, b\tc d") == ["a", "b", "c", "d"]
