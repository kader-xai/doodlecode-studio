"""Public façade in front of the persistent kernel.

Iter 2 shelled out to a fresh `python -c` per cell. Iter 25 swapped
that for `kernel.KernelSession` — a long-running child process so
`x = 1` in one cell carries over to the next. This module keeps the
public name `execute(req)` so callers in `main.py` don't change.
"""
from __future__ import annotations

from .kernel import get_session
from .models import ExecuteRequest, ExecuteResponse


def execute(req: ExecuteRequest) -> ExecuteResponse:
    return get_session().execute(req)


def reset() -> None:
    get_session().reset()
