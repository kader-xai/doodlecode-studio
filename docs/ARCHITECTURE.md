# Architecture

> Goal of this document: anyone landing on the repo can understand the
> moving parts in 10 minutes and find the file they need to change.

## Bird's-eye view

```
┌──────────────────────────────────────────────────────────────────────────┐
│  Browser  (Vite dev server, http://localhost:5173)                       │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │  React app (frontend/src/)                                         │  │
│  │                                                                    │  │
│  │  App.tsx                                                           │  │
│  │   ├── Toolbar         Open / Save / Run / Theme / About            │  │
│  │   ├── DoodleCanvas    ReactFlow with three node types              │  │
│  │   │    ├── CodeCellNode       Monaco editor + Outputs              │  │
│  │   │    ├── ExplanationNode    Hand-drawn callout bubble            │  │
│  │   │    └── MarkdownNode       Rendered markdown card               │  │
│  │   ├── PresenterBar    Prev/Next stepper                            │  │
│  │   └── About           Modal with credit + links                    │  │
│  │                                                                    │  │
│  │  store.ts (zustand)   notebook, cellState, theme, focusedCellId    │  │
│  │                       Autosaves to localStorage + POST /autosave   │  │
│  │  api.ts               fetch wrappers for the seven endpoints       │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                              │                                           │
│                /api → vite proxy → http://localhost:8000                 │
└──────────────────────────────┼───────────────────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────────────────┐
│  FastAPI  (backend/app/main.py, http://localhost:8000)                   │
│                                                                          │
│   /health           liveness                                             │
│   /upload      ←──  .py / .ipynb / .md → Notebook(cells, meta)           │
│   /export      ──→  Notebook → .py text (round-trips with /upload)       │
│   /autosave    ──→  Persist Notebook to ~/.doodlecode/<name>.py          │
│   /execute     ←──  code → run on the kernel → outputs + status          │
│   /explain     ←──  code + meta → cell-level callout                     │
│   /reset       ──→  drop a session's kernel                              │
│                                                                          │
│  modules:                                                                │
│   notebook.py       parser  for the # %% + # @explain format             │
│   serialize.py      writer  for the same format                          │
│   parser.py         AST → CodeBlock list (used internally)               │
│   explain.py        callout generator (stub — wire an LLM here)          │
│   models.py         pydantic schemas shared with the frontend            │
│   kernel.py         KernelPool: one persistent IPython kernel/session    │
└──────────────────────────────┼───────────────────────────────────────────┘
                               │ jupyter_client (zeromq)
                ┌──────────────▼──────────────┐
                │   IPython kernel process    │
                │   (one per session_id)      │
                └─────────────────────────────┘
```

## Frontend

### Components

| File | Responsibility |
|------|----------------|
| `App.tsx`                 | Mounts the canvas, toolbar, presenter bar, About modal. Toggles `<html class="dark">`. |
| `components/Toolbar.tsx`  | Top bar — file ops, theme, About. Shows "saved Ns ago" indicator. |
| `components/DoodleCanvas.tsx` | The ReactFlow graph. Builds node layout from `notebook.cells` + `cellState`. Owns pan/zoom behaviour. |
| `components/CodeCellNode.tsx` | A code card. Hosts the Monaco editor, the ✎ callout-editor toggle, the ▶ Run button, and the Outputs panel. |
| `components/MarkdownNode.tsx` | Renders a markdown cell with a minimal inline parser (headings, bullets, bold, inline code). |
| `components/ExplanationNode.tsx` | A callout bubble. Reads `data.color` from the cell meta. |
| `components/CalloutEditor.tsx` | The popover that edits a cell's title / explanation / color / kind. |
| `components/Outputs.tsx`  | Renders the result mime bundle — stream, result, display, error. Scrollable, capped at 288 px. |
| `components/PresenterBar.tsx` | The bottom Prev/Next strip while presenting. |
| `components/About.tsx`    | Modal with author info + LinkedIn/GitHub/site links. |
| `components/DoodleBorder.tsx` | Thin wrapper around `roughjs` that renders the sketchy SVG rectangle around every card. |
| `lib/rough.ts`            | Shared palette + helpers. Holds light & dark hex maps. |
| `store.ts`                | Single zustand store. Reads / writes `localStorage`. Debounces `POST /autosave`. |
| `api.ts`                  | Fetch wrappers for the seven endpoints. |
| `types.ts`                | TypeScript mirror of the pydantic schemas. |

### Data flow

1. **Open** → fetch `POST /upload` → `Notebook` → `store.setNotebook`.
2. The store sets `focusedCellId`. Subscribers re-render.
3. `DoodleCanvas` recomputes nodes (memoised on `cells` + `cellState`) and
   edges (cell-to-explanation, cell-to-cell chain).
4. Each `CodeCellNode` calls `POST /explain` whenever its `cell.meta`
   changes; the response becomes one entry in `cellState[id].explain` and
   the right-side bubble updates.
5. **Run** → `POST /execute` → outputs land in `cellState[id].outputs`.
6. **Any edit** → store debounces a `POST /autosave` (1.2 s).
7. **💾 Save** → `POST /export` → blob download.

### Themes

`store.theme` is `"light" | "dark"`. `App.tsx` toggles
`document.documentElement.classList`. Tailwind is configured with
`darkMode: "class"`, and `lib/rough.ts` exports a parallel `PALETTE_DARK`
map. Components that pick colors pass `dark` into `colorFor()`.

## Backend

### Endpoints

All endpoints are documented in `backend/app/main.py`. They return
pydantic models declared in `models.py`.

| Method | Path        | Body          | Response       | Side effects |
|--------|-------------|---------------|----------------|--------------|
| GET    | `/health`   | —             | `{"ok": true}` | None |
| GET    | `/version`  | —             | `{app, format_version}` | None |
| POST   | `/upload`   | `multipart`   | `Notebook`     | None |
| POST   | `/export`   | `Notebook`    | `text/plain`   | None |
| POST   | `/autosave` | `Notebook`    | `{path}`       | Writes `~/.doodlecode/<name>.py` |
| POST   | `/execute`  | `ExecuteReq`  | `ExecuteResp`  | Runs code on the session's kernel |
| POST   | `/explain`  | `ExplainReq`  | `ExplainResp`  | None (pure function) |
| POST   | `/install`  | `InstallReq`  | `InstallResp`  | Runs `pip install` inside the kernel's venv |
| POST   | `/reset`    | `?session_id` | `{ok}`         | Shuts down the session's kernel |

CORS is open (`*`). That is **fine for localhost** and **not safe** for
public hosting — see [SECURITY.md](../SECURITY.md).

### Kernel pool

`kernel.py` keeps a `dict[session_id, KernelSession]`. A `KernelSession`
owns a `KernelManager` + `KernelClient` pair started via
`jupyter_client`. Execution is serialized via a per-session `Lock`; the
client polls iopub messages until the kernel reports `idle`.

`pool.shutdown_all()` runs on FastAPI's `lifespan` exit so kernels don't
leak when you Ctrl-C the server.

The default session id is `"default"`. The frontend never sets a
different one yet — that's a hook for future multi-tab / multi-doc
support.

### Notebook parsing

`notebook.from_py()` is the input side; `serialize.serialize_notebook()`
is the output side. Together they round-trip. The exhaustive rules are
in [FILE_FORMAT.md](FILE_FORMAT.md).

### Explanation engine

`explain.explain_code()` is the integration seam for any real LLM.

The current implementation returns:

- One `Explanation` per cell **if** the cell has user-authored meta
  (title/explain). Otherwise an empty list.

That is the deliberate UX: right-column callouts are user content only.

To wire in a real model, replace the function body with a call to your
LLM and return one or more `Explanation` objects. Keep the
`Explanation.color` field set (`KIND_COLOR[meta.kind]` is the default
fallback) so the bubble colors stay coordinated with the section.

## Storage

| Where                      | What |
|----------------------------|------|
| `localStorage["doodlecode.notebook.v2"]` | Last notebook (browser-side autosave) |
| `localStorage["doodlecode.theme"]`        | `"light"` / `"dark"` |
| `~/.doodlecode/<name>.py`                 | Disk-side autosave (server) |
| `~/Library/Jupyter/kernels/doodlecode`    | The IPython kernelspec (registered on first run) |
| `backend/.venv/`                          | Python virtual environment |

## Build & run flow

```
./start.sh
   ├── python -m venv backend/.venv         (first run)
   ├── pip install -r backend/requirements.txt
   ├── ipykernel install --user --name doodlecode
   ├── uvicorn app.main:app --port 8000     (backend, background)
   ├── npm install (frontend)               (first run)
   └── vite --port 5173                     (frontend, background)
```

`vite.config.ts` proxies `/api/*` to `http://localhost:8000`. There is no
production build target yet — see [ROADMAP.md](ROADMAP.md).

## Testing strategy (current → target)

- **Today**: `tsc -b --noEmit`, `python -m compileall`, manual smoke
  tests, the CI round-trip assertion.
- **Target**:
  - `backend/tests/` with `pytest` covering `notebook.py`,
    `serialize.py`, `explain.py`, and a kernel-light test (using a
    `mock-jupyter-client`).
  - `frontend/tests/` with Vitest for `store.ts` and the renderers.
  - A Playwright happy-path test (open → run → save → reopen).
