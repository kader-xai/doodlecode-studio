"""Long-running Python kernel that backs `/api/execute`.

Singleton subprocess shared by all requests. A `threading.Lock`
serializes execution so two concurrent `/api/execute` calls don't
interleave on the kernel's stdin/stdout.

Timeout is enforced by reading the response on a background thread
and joining with the configured deadline. If the deadline expires
the kernel is killed and respawned — the user gets a "timeout"
response, the next request starts a fresh process.
"""
from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Optional

from .models import ExecuteOutput, ExecuteRequest, ExecuteResponse

_RUNNER = Path(__file__).parent / "runner.py"


class KernelSession:
    def __init__(self) -> None:
        self._proc: Optional[subprocess.Popen[str]] = None
        self._lock = threading.Lock()

    # ── lifecycle ──────────────────────────────────────────────────

    def _ensure_running(self) -> None:
        if self._proc and self._proc.poll() is None:
            return
        # Force matplotlib to its non-interactive Agg backend so user
        # code that calls plt.show() doesn't try to spawn a window.
        # We capture figures from the runner after each exec.
        env = {**os.environ, "MPLBACKEND": "Agg"}
        self._proc = subprocess.Popen(
            [sys.executable, "-u", str(_RUNNER)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            env=env,
        )

    def reset(self) -> None:
        """Kill the current kernel (next execute spawns a fresh one)."""
        with self._lock:
            if self._proc and self._proc.poll() is None:
                try:
                    self._proc.kill()
                except Exception:
                    pass
            self._proc = None

    def interrupt(self) -> bool:
        """Send SIGINT to the running kernel — equivalent to Ctrl+C
        landing inside the user's `exec()`. The runner catches
        BaseException so we get a normal "error" response back and
        the kernel survives.

        Read `self._proc` once without acquiring the lock — `execute`
        holds the lock for the entire duration of a run and we'd
        deadlock if we tried to take it. Returns True iff a signal
        was actually sent.
        """
        proc = self._proc
        if not proc or proc.poll() is not None:
            return False
        try:
            os.kill(proc.pid, signal.SIGINT)
            return True
        except (ProcessLookupError, PermissionError, OSError):
            return False

    # ── execute ────────────────────────────────────────────────────

    def execute(self, req: ExecuteRequest) -> ExecuteResponse:
        with self._lock:
            self._ensure_running()
            assert self._proc and self._proc.stdin and self._proc.stdout
            t0 = time.monotonic()

            try:
                self._proc.stdin.write(json.dumps({"source": req.source}) + "\n")
                self._proc.stdin.flush()
            except (BrokenPipeError, ValueError, OSError):
                # Kernel died between checks. Drop it; the next call
                # will respawn. Surface the failure to the caller.
                self._proc = None
                return _err("Kernel pipe broken — restart kernel and retry.", t0)

            line_holder: list[str] = []
            done = threading.Event()

            def reader() -> None:
                try:
                    line = self._proc.stdout.readline() if self._proc and self._proc.stdout else ""
                except Exception as e:
                    line = json.dumps({"status": "error", "stdout": "", "stderr": str(e)}) + "\n"
                line_holder.append(line)
                done.set()

            t = threading.Thread(target=reader, daemon=True)
            t.start()

            if not done.wait(timeout=req.timeout_s):
                # Hard timeout — kill the kernel so it doesn't leak.
                try:
                    if self._proc:
                        self._proc.kill()
                except Exception:
                    pass
                self._proc = None
                return ExecuteResponse(
                    status="timeout",
                    elapsed_ms=int((time.monotonic() - t0) * 1000),
                    outputs=[
                        ExecuteOutput(
                            type="error",
                            text=f"Timed out after {req.timeout_s}s — kernel restarted.",
                        )
                    ],
                )

            line = (line_holder[0] if line_holder else "").strip()
            try:
                resp = json.loads(line) if line else {}
            except Exception:
                return _err(f"Bad kernel response: {line!r}", t0)

            outputs: list[ExecuteOutput] = []
            if resp.get("stdout"):
                outputs.append(ExecuteOutput(type="stdout", text=resp["stdout"]))
            if resp.get("stderr"):
                outputs.append(ExecuteOutput(type="stderr", text=resp["stderr"]))
            for b64 in resp.get("images_png_b64", []) or []:
                outputs.append(ExecuteOutput(type="image_png", text=b64))
            outputs.append(ExecuteOutput(type="done"))
            return ExecuteResponse(
                status=resp.get("status", "ok"),
                elapsed_ms=int((time.monotonic() - t0) * 1000),
                outputs=outputs,
            )


def _err(msg: str, t0: float) -> ExecuteResponse:
    return ExecuteResponse(
        status="error",
        elapsed_ms=int((time.monotonic() - t0) * 1000),
        outputs=[ExecuteOutput(type="error", text=msg)],
    )


# Module-level singleton — one kernel per backend process.
_session = KernelSession()


def get_session() -> KernelSession:
    return _session
