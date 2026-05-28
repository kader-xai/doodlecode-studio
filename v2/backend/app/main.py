"""DoodleCode Studio v2 — FastAPI server.

Iter 1 scope: serve the built frontend and expose a tiny /api/ping
endpoint that returns the app version. Future iters add /execute,
/save, /open, /proxy, /install, /tools/*.
"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from . import __version__
from .executor import execute as run_python, interrupt as interrupt_kernel, reset as reset_kernel
from . import notebook_io
from .models import (
    ExecuteRequest,
    ExecuteResponse,
    OpenRequest,
    OpenResponse,
    SaveRequest,
    SaveResponse,
)
from fastapi import UploadFile, File

from .proxy import proxy as proxy_handler
from .installer import install as pip_install, InstallRequest, InstallResponse
from .tools import ppt_to_png, PptToPngResponse

ROOT = Path(__file__).resolve().parent.parent.parent  # v2/
DIST = ROOT / "frontend" / "dist"

app = FastAPI(title="DoodleCode Studio v2", version=__version__)

# Local-only by default. v1 left CORS open for dev convenience; we
# keep that here so the Vite dev server on :5174 can talk to us.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/ping")
def ping() -> dict:
    return {"ok": True, "version": __version__, "name": "DoodleCode Studio v2"}


@app.get("/api/demo")
def demo() -> dict:
    """Return the bundled tour .py file as text. Used by the
    "Load demo" item in the File menu."""
    path = ROOT / "examples" / "demo.py"
    if not path.is_file():
        return JSONResponse({"error": "demo file not found"}, status_code=404)  # type: ignore[return-value]
    return {"text": path.read_text(encoding="utf-8")}


@app.post("/api/execute", response_model=ExecuteResponse)
def execute(req: ExecuteRequest) -> ExecuteResponse:
    return run_python(req)


@app.post("/api/kernel/reset")
def kernel_reset() -> dict:
    """Kill the kernel; the next execute spawns a fresh one. Used by
    the toolbar's ↻ Kernel button to wipe leftover globals/imports."""
    reset_kernel()
    return {"ok": True}


@app.post("/api/kernel/interrupt")
def kernel_interrupt() -> dict:
    """Iter 44: SIGINT the running kernel — equivalent to Ctrl+C
    inside the user's exec(). The runner catches BaseException so
    the kernel survives and a normal "error" response comes back."""
    return {"ok": interrupt_kernel()}


@app.post("/api/install", response_model=InstallResponse)
def install_packages(req: InstallRequest) -> InstallResponse:
    """pip install into the kernel's Python. Auto-resets the kernel on
    success so a fresh import of the new package picks it up."""
    res = pip_install(req)
    if res.ok:
        reset_kernel()
    return res


@app.post("/api/save", response_model=SaveResponse)
def save(req: SaveRequest) -> SaveResponse:
    text = notebook_io.serialize(req.notebook)
    return SaveResponse(text=text)


@app.post("/api/open", response_model=OpenResponse)
def open_notebook(req: OpenRequest) -> OpenResponse:
    nb, version = notebook_io.parse(req.text)
    return OpenResponse(notebook=nb, format_version=version)


# X-Frame-Options bypass for the Browser cell. Registered as an
# `async` GET handler — see proxy.py for the SSRF guard and limits.
app.add_api_route("/api/proxy", proxy_handler, methods=["GET"])


@app.post("/api/tools/ppt-to-png", response_model=PptToPngResponse)
async def tools_ppt_to_png(file: UploadFile = File(...)) -> PptToPngResponse:
    return await ppt_to_png(file)


# Static frontend. Mounted last so /api/* takes precedence.
if DIST.is_dir():
    # Serve hashed assets directly.
    app.mount("/assets", StaticFiles(directory=DIST / "assets"), name="assets")

    @app.get("/{full_path:path}")
    def spa(full_path: str):  # noqa: ARG001
        index = DIST / "index.html"
        if index.is_file():
            return FileResponse(index)
        return JSONResponse(
            {"error": "frontend not built", "hint": "run npm run build in v2/frontend"},
            status_code=503,
        )
else:
    @app.get("/")
    def root() -> dict:
        return {
            "ok": True,
            "version": __version__,
            "note": "frontend not built yet — run npm run build in v2/frontend",
        }
