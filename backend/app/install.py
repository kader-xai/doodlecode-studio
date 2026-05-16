"""Pip-install packages into the kernel's virtualenv.

This runs `python -m pip install <pkgs>` using the same interpreter that
hosts the FastAPI process — which is the venv the IPython kernel was
registered against in start.sh. So whatever lands here becomes
importable in the next `import` the user runs.

Validation is intentionally light (this is a local-only tool, see
SECURITY.md) — we just refuse shell metacharacters and split on
whitespace.
"""
from __future__ import annotations

import re
import subprocess
import sys

from .models import InstallRequest, InstallResponse

_PKG_RE = re.compile(r"^[A-Za-z0-9_.\-\[\]=<>!~+,@/:]+$")


def _validate(packages: str) -> list[str]:
    tokens = [t for t in packages.replace(",", " ").split() if t.strip()]
    if not tokens:
        raise ValueError("No package given.")
    bad = [t for t in tokens if not _PKG_RE.match(t)]
    if bad:
        raise ValueError(f"Refusing suspicious tokens: {bad}")
    return tokens


def pip_install(req: InstallRequest, timeout: float = 600.0) -> InstallResponse:
    pkgs = _validate(req.packages)
    cmd = [sys.executable, "-m", "pip", "install"]
    if req.upgrade:
        cmd.append("--upgrade")
    cmd.extend(pkgs)
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    return InstallResponse(
        ok=proc.returncode == 0,
        packages=pkgs,
        stdout=proc.stdout[-8000:],
        stderr=proc.stderr[-8000:],
        returncode=proc.returncode,
    )
