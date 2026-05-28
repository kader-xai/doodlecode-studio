"""`pip install …` into the kernel's Python.

Synchronous endpoint — we wait for pip to finish then return the
combined stdout/stderr to the frontend. After a successful install
the caller should reset the kernel so freshly-installed modules are
discoverable on the next import.

Safety:
  * `--disable-pip-version-check` — keeps output focused on the install.
  * Package names go through a simple allow-list pattern so a user
    can't smuggle `&& rm -rf /` into the args. Same regex as pip's
    own requirement spec (letters, digits, `_-.[]<>=~,!` plus
    surrounding whitespace).
"""
from __future__ import annotations

import re
import subprocess
import sys
import time
from typing import List

from pydantic import BaseModel


# Liberal package-name regex: name, optional extras, optional version
# spec. Reject anything with shell metacharacters.
_PKG_RE = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9_\-.]*(\[[A-Za-z0-9_,\-.]+\])?"
    r"([<>=!~]=?[A-Za-z0-9_\-.,*]+)?$"
)


class InstallRequest(BaseModel):
    packages: str  # space- or newline-separated


class InstallResponse(BaseModel):
    ok: bool
    elapsed_ms: int
    output: str
    packages: List[str]


def _split(s: str) -> List[str]:
    out: List[str] = []
    for tok in re.split(r"[\s,]+", s.strip()):
        if tok:
            out.append(tok)
    return out


def install(req: InstallRequest) -> InstallResponse:
    pkgs = _split(req.packages)
    if not pkgs:
        return InstallResponse(ok=False, elapsed_ms=0, output="No packages given.", packages=[])
    bad = [p for p in pkgs if not _PKG_RE.match(p)]
    if bad:
        return InstallResponse(
            ok=False, elapsed_ms=0,
            output=f"Refusing — not a valid package spec: {', '.join(bad)}",
            packages=pkgs,
        )

    t0 = time.monotonic()
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "pip", "install",
             "--disable-pip-version-check", "--no-color", *pkgs],
            capture_output=True, text=True, timeout=180,
        )
    except subprocess.TimeoutExpired:
        return InstallResponse(
            ok=False,
            elapsed_ms=int((time.monotonic() - t0) * 1000),
            output="pip install timed out after 180 s.",
            packages=pkgs,
        )

    out = (proc.stdout or "") + (("\n" + proc.stderr) if proc.stderr else "")
    return InstallResponse(
        ok=(proc.returncode == 0),
        elapsed_ms=int((time.monotonic() - t0) * 1000),
        output=out.strip(),
        packages=pkgs,
    )
