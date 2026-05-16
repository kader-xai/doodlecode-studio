from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import APIRouter, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

from . import __version__ as APP_VERSION
from .explain import explain_code
from .install import pip_install
from .kernel import pool
from .models import (
    FILE_FORMAT_VERSION,
    ExecuteRequest,
    ExecuteResponse,
    ExplainRequest,
    ExplainResponse,
    InstallRequest,
    InstallResponse,
    Notebook,
    VersionInfo,
)
from .notebook import from_ipynb, from_markdown, from_py
from .serialize import serialize_notebook

WORKSPACE = Path.home() / ".doodlecode"
WORKSPACE.mkdir(exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    pool.shutdown_all()


app = FastAPI(title="DoodleCode Studio", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# All HTTP endpoints live under /api so the React build can be served at
# the root path without colliding with API routes.
api = APIRouter()


@api.get("/health")
def health() -> dict:
    return {"ok": True}


@api.get("/version", response_model=VersionInfo)
def version() -> VersionInfo:
    return VersionInfo(app=APP_VERSION, format_version=FILE_FORMAT_VERSION)


@api.post("/execute", response_model=ExecuteResponse)
def execute(req: ExecuteRequest) -> ExecuteResponse:
    session = pool.get(req.session_id)
    return session.execute(req.code)


@api.post("/reset")
def reset(session_id: str = "default") -> dict:
    pool.reset(session_id)
    return {"ok": True, "session_id": session_id}


@api.post("/install", response_model=InstallResponse)
def install(req: InstallRequest) -> InstallResponse:
    """Pip-install packages into the kernel's venv. Returns stdout/stderr.
    Newly installed packages are importable on the next `import` in any
    cell — no kernel restart needed.

    After a successful install we also tell any running kernels to
    invalidate their import caches so packages that were freshly added
    to site-packages are picked up immediately.
    """
    try:
        result = pip_install(req)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    if result.ok:
        # Best-effort cache invalidation on every active session. Tiny
        # cost, removes the "I had to refresh the page" surprise.
        for session in list(pool._sessions.values()):
            session.invalidate_import_caches()
    return result


@api.post("/explain", response_model=ExplainResponse)
def explain(req: ExplainRequest) -> ExplainResponse:
    return explain_code(req.code, mode=req.mode, meta=req.meta)


@api.post("/export", response_class=PlainTextResponse)
def export(nb: Notebook) -> str:
    """Serialize a notebook back to a .py file with `# %%` headers
    and `# @explain:` directives. Round-trips with /upload."""
    return serialize_notebook(nb)


@api.post("/autosave")
def autosave(nb: Notebook) -> dict:
    """Persist the current notebook to ~/.doodlecode/<name>.py so changes
    survive a reload. Called on every edit (debounced client-side)."""
    safe = "".join(c for c in nb.name if c.isalnum() or c in "._- ") or "untitled.py"
    if not safe.endswith(".py"):
        safe = safe.rsplit(".", 1)[0] + ".py"
    target = WORKSPACE / safe
    target.write_text(serialize_notebook(nb), encoding="utf-8")
    return {"ok": True, "path": str(target)}


@api.post("/upload", response_model=Notebook)
async def upload(file: UploadFile = File(...)) -> Notebook:
    raw = await file.read()
    name = file.filename or "untitled"
    lower = name.lower()
    try:
        if lower.endswith(".ipynb"):
            return from_ipynb(name, raw)
        if lower.endswith(".py"):
            return from_py(name, raw)
        if lower.endswith(".md") or lower.endswith(".markdown"):
            return from_markdown(name, raw)
        # fallback: treat as a single python cell
        return from_py(name, raw)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not parse {name}: {e}") from e


app.include_router(api, prefix="/api")
# Backwards-compat: also expose the routes at the root path so older
# clients (and the dev-server proxy) that hit "/execute" instead of
# "/api/execute" don't get a 405 from the SPA catch-all below.
app.include_router(api)

# Serve the built React app at the root. `frontend/dist` is created by
# `npm run build` and shipped with the release. If it isn't present
# (e.g. during pytest), we just skip the mount — the API still works.
_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if _DIST.is_dir():
    app.mount("/assets", StaticFiles(directory=_DIST / "assets"), name="assets")

    @app.get("/")
    def _root() -> FileResponse:
        return FileResponse(_DIST / "index.html")

    @app.get("/{path:path}")
    def _spa(path: str) -> FileResponse:
        # Serve any other file from dist if it exists (favicon, etc.),
        # otherwise fall back to index.html so client-side routing works.
        candidate = _DIST / path
        if candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(_DIST / "index.html")
