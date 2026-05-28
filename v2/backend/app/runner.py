"""Long-running Python child process. Acts as a tiny kernel.

Protocol (line-delimited JSON over stdin/stdout):
  request : { "source": str }
  response: { "status": "ok"|"error", "stdout": str, "stderr": str }

`exec()` runs against a single persistent `_globals` dict so `x = 1`
in one cell is visible to the next. The script's own stdin loop
remains unaffected because we redirect stdout/stderr inside the
`exec()` call only.

Why not jupyter_client? It works but adds a heavy dep (~50 MB) and
a ZMQ socket setup just to ship `x = 1` from one cell to the next.
This 40-line runner does the same in plain Python.
"""
from __future__ import annotations

import base64
import contextlib
import io
import json
import sys
import traceback


def _capture_matplotlib_figures() -> list[str]:
    """If matplotlib has been imported, drain every open figure as a
    base64-encoded PNG and close it. Returns one base64 string per
    figure, in figure-number order.

    We probe via `sys.modules` so we don't import matplotlib unless
    the user already did — keeps cold-start cheap. The parent process
    sets `MPLBACKEND=Agg` so plt.show() never tries to open a window.
    """
    if "matplotlib" not in sys.modules:
        return []
    try:
        import matplotlib.pyplot as plt  # already imported by the user
    except Exception:
        return []
    out: list[str] = []
    for num in list(plt.get_fignums()):
        try:
            fig = plt.figure(num)
            buf = io.BytesIO()
            fig.savefig(buf, format="png", bbox_inches="tight", dpi=110)
            out.append(base64.b64encode(buf.getvalue()).decode("ascii"))
            plt.close(fig)
        except Exception:
            # Skip a broken figure rather than blow up the whole cell.
            continue
    return out


def _run_once(_globals: dict, source: str) -> dict:
    out_buf = io.StringIO()
    err_buf = io.StringIO()
    status = "ok"
    try:
        # `compile` first so SyntaxError is reported before the
        # redirect tries to capture it — gives clearer line numbers
        # in the traceback.
        try:
            code = compile(source, "<cell>", "exec")
        except SyntaxError:
            traceback.print_exc(file=err_buf)
            status = "error"
        else:
            with contextlib.redirect_stdout(out_buf), contextlib.redirect_stderr(err_buf):
                try:
                    exec(code, _globals)
                except BaseException:
                    traceback.print_exc(file=err_buf)
                    status = "error"
    except Exception:
        # Anything outside the user's code — runner bug.
        traceback.print_exc(file=err_buf)
        status = "error"
    return {
        "status": status,
        "stdout": out_buf.getvalue(),
        "stderr": err_buf.getvalue(),
        "images_png_b64": _capture_matplotlib_figures(),
    }


def main() -> None:
    _globals: dict = {"__name__": "__main__"}
    # Unbuffered line-by-line. Parent reads exactly one JSON line
    # per request.
    for raw in sys.stdin:
        raw = raw.strip()
        if not raw:
            continue
        try:
            req = json.loads(raw)
        except Exception as e:
            sys.stdout.write(
                json.dumps({"status": "error", "stdout": "", "stderr": f"bad request: {e}"})
                + "\n"
            )
            sys.stdout.flush()
            continue
        resp = _run_once(_globals, req.get("source", ""))
        sys.stdout.write(json.dumps(resp) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
