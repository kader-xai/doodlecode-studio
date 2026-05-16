# 🤖 DoodleCode Studio — AI Handoff Brief

> **You are an AI assistant who has been pointed at this project to
> understand it, fork it, extend it, or rebuild it.** This file is the
> single-page brief you need. Read it top to bottom and you will know
> what this project is, how it's structured, what its conventions are,
> and where to go for deeper detail.

---

## What this project is, in one paragraph

DoodleCode Studio is a **local-first Python notebook with a doodle
canvas presentation layer**. Code lives in colored hand-drawn cards on
the left, user-authored explanations live as callout bubbles on the
right, all stored in a single `.py` file. The file is real Python that
runs end-to-end with `python file.py`. Inside the app, an IPython
kernel executes cells and the output renders inline. A presentation
mode auto-fits each cell to the screen with a fading pen + highlighter
for live drawing. It's an MIT-licensed monorepo with a FastAPI backend
and a React + Vite frontend.

**Audience**: anyone who needs to teach or present Python code where
showing the explanation *next to* the code matters more than scrolling
through cells.

**Tagline in the About modal**: "Co-AI Developed by Kader Mohideen."

---

## Repository shape

```
DoodleNotebook/
├─ backend/                 FastAPI + IPython kernel
│  ├─ app/
│  │  ├─ main.py            HTTP routes (/upload, /export, /execute, …)
│  │  ├─ kernel.py          Persistent kernel-per-session pool
│  │  ├─ notebook.py        .py / .ipynb / .md parsing
│  │  ├─ serialize.py       Notebook → .py with # %% markers
│  │  ├─ explain.py         User-callout generator (no AI by default)
│  │  ├─ install.py         pip install validator + runner
│  │  ├─ parser.py          AST helpers
│  │  └─ models.py          Pydantic schemas (shared shape with the FE)
│  ├─ tests/                pytest suite (~90 tests)
│  ├─ requirements.txt
│  ├─ pyproject.toml
│  └─ ruff.toml             lint config
├─ frontend/                React 18 + TypeScript strict + Vite
│  ├─ src/
│  │  ├─ App.tsx            Mounts everything, theme + fullscreen wiring
│  │  ├─ store.ts           zustand store + localStorage + debounced autosave
│  │  ├─ api.ts             fetch wrappers for every backend endpoint
│  │  ├─ types.ts           TS mirror of pydantic schemas + APP_VERSION
│  │  ├─ lib/rough.ts       Color palette (light + dark), kind→color fallback
│  │  ├─ lib/useMeasuredHeight.ts   ResizeObserver hook
│  │  ├─ index.css          Tailwind base + .doodle-card + cursors
│  │  └─ components/
│  │     ├─ DoodleCanvas.tsx        ReactFlow surface, focused-cell fitBounds
│  │     ├─ Toolbar.tsx             Top bar (Open / Save / Code / Text / …)
│  │     ├─ CodeCellNode.tsx        Monaco editor + colored top strip
│  │     ├─ MarkdownNode.tsx        Editable text/slide card
│  │     ├─ ExplanationNode.tsx     Right-side callout bubble
│  │     ├─ CalloutEditor.tsx       Draggable popover for callout meta
│  │     ├─ TextEditor.tsx          Draggable popover for slide content
│  │     ├─ InstallModal.tsx        pip install dialog
│  │     ├─ PresenterBar.tsx        Prev/Next + pen + highlighter + ⛶
│  │     ├─ PresenterOverlay.tsx    Fading SVG ink layer
│  │     ├─ Outputs.tsx             Execute-result renderer (text/png/html)
│  │     ├─ EditableTitle.tsx       Double-click inline title rename
│  │     ├─ ResizeHandle.tsx        Bottom-right corner drag
│  │     ├─ About.tsx               Author + project URL modal
│  │     └─ ErrorBoundary.tsx       Catches unhandled render errors
│  ├─ tests/                vitest (~40 tests, jsdom)
│  ├─ package.json
│  ├─ tsconfig.json         strict mode on
│  ├─ vite.config.ts        `/api` proxied to :8000 in dev
│  └─ tailwind.config.js    darkMode: "class"
├─ docs/                    User-facing docs (you're reading one)
│  ├─ AI_HANDOFF.md         ← THIS FILE
│  ├─ FILE_FORMAT.md        The .py wire contract
│  ├─ USAGE.md              End-user guide
│  ├─ AUTHORING.md          Writing .py files by hand
│  ├─ ARCHITECTURE.md       Layer + endpoint breakdown
│  ├─ DEVELOPMENT.md        Local-dev guide
│  ├─ ROADMAP.md            Future work
│  └─ VIDEO_SCRIPT.md       Screencast recording shot list
├─ examples/                Tutorial .py files in the project's format
├─ .github/
│  ├─ workflows/ci.yml      Matrix CI: Python 3.9/3.11/3.12 × Node 18/20
│  ├─ ISSUE_TEMPLATE/       Bug / feature forms
│  ├─ PULL_REQUEST_TEMPLATE.md
│  └─ FUNDING.yml
├─ start.sh                 One-shot launcher (venv + uvicorn + vite)
├─ README.md
├─ CHANGELOG.md             Keep-a-Changelog format
├─ LICENSE                  MIT
├─ CONTRIBUTING.md
├─ CODE_OF_CONDUCT.md
├─ SECURITY.md
└─ .editorconfig
```

The author also maintains a **local-only** `CLAUDE.md` (gitignored)
with private working notes / rules. You won't see it in the repo
clone. Don't recreate it unless explicitly asked.

---

## The single most important contract: the file format

Every `.py` saved by the app is **plain Python** that runs end-to-end
with `python file.py`. The cell structure + callouts live in comments.

```python
# doodlecode format-version: 2

# %% [markdown] color=sky title="Slide title"
# @explain: Optional callout body shown on the right.
# @image: data:image/png;base64,AAA…             (optional)
# # Heading
# Markdown body

# %% kind=function color=mint title="Compute area"
# @explain: Wraps the formula so we don't repeat it.
# @callout title="Aside" color=peach
# @explain: A second bubble next to the same cell.
import math
def area(r):
    return math.pi * r * r
```

Rules:
- Cell delimiters: any line matching `^\s*#\s*%%\s*(.*)$`
- Header values: `kind=str color=str title="quoted if needed"`
- Directives (leading lines only): `# @explain:`, `# @title:`,
  `# @color:`, `# @kind:`, `# @image:`, `# @tags:`, `# @callout`
- Markdown cells: `# %% [markdown]` then body lines prefixed `# `
- Multiple callouts: `# @callout` separator opens a new bubble
- Backward compatibility: v1 files (no preamble, single callout) still
  parse identically

Full spec with palette table and round-trip guarantees lives in
[FILE_FORMAT.md](FILE_FORMAT.md). The parser is
`backend/app/notebook.py`, the writer is `backend/app/serialize.py`.
Every change to either MUST keep the example files round-tripping
(there's a parameterised pytest that walks `examples/` and asserts).

---

## Architecture in 30 seconds

```
Browser (React + Vite, :5173)
  ↓ /api proxy
FastAPI (:8000)
  ↓ jupyter_client (zeromq)
IPython kernel process  (one per session_id)
```

Frontend state lives in a single **zustand store** (`store.ts`). Both
`localStorage` (browser-side autosave) and `POST /autosave`
(server-side autosave to `~/.doodlecode/<name>.py`) fire on every edit,
debounced 1.2 s.

The full breakdown — every endpoint, every component, every data flow
— is in [ARCHITECTURE.md](ARCHITECTURE.md).

---

## Public HTTP contract (stable as of v1.0)

| Method | Path        | Body          | Returns         |
|--------|-------------|---------------|-----------------|
| GET    | `/health`   | —             | `{ok: true}`    |
| GET    | `/version`  | —             | `{app, format_version}` |
| POST   | `/upload`   | `multipart`   | `Notebook`      |
| POST   | `/export`   | `Notebook`    | `text/plain`    |
| POST   | `/autosave` | `Notebook`    | `{path}`        |
| POST   | `/execute`  | `ExecuteReq`  | `ExecuteResp`   |
| POST   | `/explain`  | `ExplainReq`  | `ExplainResp`   |
| POST   | `/install`  | `InstallReq`  | `InstallResp`   |
| POST   | `/reset`    | `?session_id` | `{ok}`          |

All requests/responses use the pydantic models in
`backend/app/models.py`. Their TypeScript mirror is in
`frontend/src/types.ts`.

---

## The conventions you will be measured against

These are the project's load-bearing principles. **Do not violate
them without explicit user approval.**

1. **Callouts are user-authored only.** The right-side bubbles
   contain what the user wrote in `# @explain:` directives — never
   AI-generated commentary. The auto-explain code path was
   deliberately removed; do not add it back.
2. **Outputs are below the editor, not on the right.** Execution
   results live inside the cell card. They never leak into the
   callout column.
3. **One single `.py` file is the entire wire format.** No sidecar
   JSON, no shadow database. Callouts, images, multiple callouts,
   title, color — everything in one file.
4. **Backward compatibility is non-negotiable.** When you bump
   `FILE_FORMAT_VERSION`, the parser must still accept every previous
   version. Files saved by older versions never break.
5. **Three-tool canvas (Cursor / Hand / Move).** Don't reintroduce
   the "drag anywhere auto-disambiguates" Figma-style auto-mode —
   it broke click vs. double-click reliability.
6. **No auto-zoom-reset during presentation.** `fitBounds` is fine;
   `setCenter(..., { zoom: 0.9 })` is not. Preserve user's zoom
   wherever the cell change is implicit.
7. **No internal scrollbars on cells.** Cells auto-grow. Monaco's
   own editor scroll is the one exception (it's a code editor).
8. **No `Claude` / `Anthropic` brand mentions** in code, docs, or
   comments. The pluggable LLM seam in `backend/app/explain.py`
   speaks in generic terms.
9. **Singleton popovers via the store.** `openEditor`, `installOpen`,
   `aboutOpen`, `fullscreen` all live in zustand and are rendered
   once at App level. Local-state popovers are forbidden — they
   caused real bugs.
10. **CSS-only border on `.doodle-card`.** Don't reintroduce the
    rough.js SVG accent — the alignment races weren't worth the
    aesthetic. The doodle feel comes from the color palette,
    handwriting font, and offset shadow.
11. **TypeScript strict mode stays on.** Don't relax `tsconfig.json`.
    No `any` unless documented.
12. **Local-only safety defaults.** CORS open for dev, kernel runs
    user code with full system access. Any move toward multi-user
    hosted mode must go behind a config flag + update
    [SECURITY.md](../SECURITY.md).

---

## Quality bars

The project ships a stable v1.2.0 (the "Golden Stable" release). To
keep that label honest, every PR must:

- `ruff check backend/app backend/tests` — clean
- `(cd backend && pytest -q)` — 92 / 92 pass
- `(cd frontend && npx tsc -b --noEmit)` — strict typecheck clean
- `(cd frontend && npm test)` — 40 / 40 vitest pass
- `(cd frontend && npm run build)` — production bundle succeeds
- All shipped `examples/*.py` files round-trip byte-stable through
  `from_py → serialize_notebook → from_py`

CI enforces these across Python 3.9 / 3.11 / 3.12 and Node 18 / 20.

---

## How to run it locally

```bash
git clone <this repo>
cd doodlecode-studio
./start.sh
```

`start.sh` creates `backend/.venv`, installs deps, registers an
IPython kernel, launches FastAPI on :8000 and Vite on :5173, then
opens the app. After the first launch, you can run the two servers
independently — see [DEVELOPMENT.md](DEVELOPMENT.md).

---

## Where to start if you're forking it

If you're an AI taking over the project:

1. **Read this file** end to end (you're doing it now).
2. **Read [FILE_FORMAT.md](FILE_FORMAT.md)** — the format is the
   contract everything else hangs off.
3. **Read [ARCHITECTURE.md](ARCHITECTURE.md)** — for the layered
   diagram and per-component responsibility table.
4. **Skim `frontend/src/store.ts`** — single source of truth for
   client state. If you understand this, you understand the UX.
5. **Skim `backend/app/notebook.py` + `serialize.py`** — the parser
   and writer. These two files are the entire wire format.
6. **Run the test suite** (commands above) — green tests are the
   safety net for any refactor.
7. **Open `examples/live_demo.py` in the app** — see what a typical
   user-authored file looks like rendered.

If you're going to change something:

- Edit code in tight focused PRs.
- Bump the four version stamps in lockstep
  (`backend/app/__init__.py`, `backend/pyproject.toml`,
  `frontend/package.json`, `frontend/src/types.ts`).
- Add a `CHANGELOG.md` entry under `[Unreleased]`.
- Touch the docs that describe what you changed
  (USAGE / FILE_FORMAT / ARCHITECTURE as applicable).
- If you change behaviour the user can see, the README must reflect
  reality on the same commit.

---

## What's worth fixing next

Open opportunities, ordered by impact:

1. **Streaming kernel output** via WebSocket so long-running cells
   don't block the UI.
2. **Pluggable LLM in `backend/app/explain.py`** — env-gated, default
   stub. See [DEVELOPMENT.md#plugging-in-a-real-llm](DEVELOPMENT.md).
3. **PDF / PPTX export** of the canvas.
4. **Tensor-flow visualizer** as a custom React Flow node type.
5. **`nbconvert` integration** — read `.ipynb` already works; produce
   `.ipynb` would be the inverse.

Full list with rationale: [ROADMAP.md](ROADMAP.md).

---

## Where to get help

- README: <https://github.com/kader-xai/doodlecode-studio>
- Issues: <https://github.com/kader-xai/doodlecode-studio/issues>
- Security: see [SECURITY.md](../SECURITY.md) — privately email the
  maintainer for vulnerabilities; do not file public issues.
- Author: Kader Mohideen · <https://kader-xai.github.io>

---

*This file is the single canonical brief for any AI / human taking
over the project. It is kept in sync with the codebase. If something
in here is wrong, fix it AND fix the code that contradicted it.*
