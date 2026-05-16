# 🎨 DoodleCode Studio

> A doodle-powered Python notebook & presentation canvas.
> Write code on the left, hand-drawn explanation bubbles on the right.
> Real Jupyter kernels underneath. Local-first. Open source.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![Node 18+](https://img.shields.io/badge/node-18+-brightgreen.svg)](https://nodejs.org/)
[![Status: alpha](https://img.shields.io/badge/status-alpha-orange.svg)](#status)

DoodleCode Studio turns a Python file into a colorful whiteboard of code
cards and explanation bubbles you can run, edit, present, and export — all
locally, with a real IPython kernel and zero cloud dependencies.

**Developed by [Kader-xai](https://kader-xai.github.io)** ·
[LinkedIn](https://linkedin.com/in/kader-xai) ·
[GitHub](https://github.com/kader-xai)

---

## Why?

Notebooks teach code by smashing prose and code into one column. Slides
present code by stripping it of life. DoodleCode Studio gives each
**section of code its own card** on a pannable canvas, and each card a
**hand-drawn callout bubble** you write yourself — so the code is real and
the explanation is *yours*. Save the file, reopen it later, and your
callouts come back exactly as you left them.

## ✨ Features

- 🐍 **Real Python execution** via persistent IPython kernels (supports
  PyTorch, pandas, matplotlib, anything `pip`-installable).
- 🖊️ **User-authored callouts** — no AI-generated noise on your right column,
  only what you wrote. Encoded into the `.py` file itself.
- 🎨 **Excalidraw-inspired vibrant palette**, color-coded per section.
  Header strip, editor left strip, and callout bubble share the same hue.
- 💾 **Round-trippable file format** — open → edit → save back to a `.py`
  with `# %%` headers and `# @explain:` directives. Commit to git, share,
  reopen.
- ⚡ **Auto-save** to `~/.doodlecode/` + browser `localStorage` after every
  edit (debounced).
- 🎬 **Presentation mode** with cell-by-cell stepping that *pans without
  resetting your zoom*.
- 🌙 **Dark / light mode** with a vibrant palette for both.
- 📂 Upload `.py`, `.ipynb`, or `.md`. Markdown cells render as proper
  formatted text cards.
- 🔌 **Pluggable explanation engine** — the AST-derived stub lives behind a
  single function; swap it for any LLM provider with ~20 lines.

## 🚀 Quickstart

```bash
git clone https://github.com/kader-xai/doodlecode-studio.git
cd doodlecode-studio
./start.sh
```

The first run creates a Python venv, installs deps, and launches:

| Service  | URL                       |
|----------|---------------------------|
| Frontend | <http://localhost:5173>   |
| Backend  | <http://localhost:8000>   |

Open the frontend, click **📂 Open**, and pick one of:

- [`examples/how_it_works.py`](examples/how_it_works.py) — the in-app tutorial.
- [`examples/module_01_python_basics.py`](examples/module_01_python_basics.py) — long-form lesson, 50 cells.
- [`examples/module_02_file_handling.py`](examples/module_02_file_handling.py) — file I/O, CSV, JSON, pathlib.
- [`examples/module_03_ai_doodle_demo.py`](examples/module_03_ai_doodle_demo.py) — a working PyTorch model in 6 cells.

## ✍️ The file format in 30 seconds

```python
# %% kind=function color=mint title="Defining the area function"
# @explain: Takes a radius and returns the area of a circle.
# @explain: math.pi is the constant π. Multiple @explain lines are joined.
# @tags: math, geometry
import math

def area_of_circle(r):
    return math.pi * r * r
```

Available colors: `mint`, `sky`, `yellow`, `pink`, `peach`, `lavender`,
`rose`, `cyan`, `violet`, `green`, `blue`, `orange`, `red`. The full spec is
in [docs/FILE_FORMAT.md](docs/FILE_FORMAT.md).

## 🏗️ Architecture (one screen)

```
┌─────────────────────────────────────────────────────────────────┐
│                          Browser (React)                        │
│                                                                 │
│  ┌─────────────┐    ┌──────────────────┐    ┌────────────────┐  │
│  │  Toolbar    │    │  DoodleCanvas    │    │  CalloutEditor │  │
│  │  Open/Save  │    │  ReactFlow +     │    │  Title/color/  │  │
│  │  Theme/About│    │  Monaco + rough  │    │  explain text  │  │
│  └─────────────┘    └────────┬─────────┘    └────────────────┘  │
│                              │                                  │
│             zustand store + localStorage snapshot               │
└──────────────────────────────┼──────────────────────────────────┘
                               │ fetch /api
                ┌──────────────▼──────────────┐
                │      FastAPI (Python)       │
                │  /upload  /export  /reset   │
                │  /execute /explain /autosave│
                └──────────────┬──────────────┘
                               │
                ┌──────────────▼──────────────┐
                │   jupyter_client            │
                │   one persistent kernel     │
                │   per session_id            │
                └─────────────────────────────┘
```

The full breakdown — every endpoint, every component, every data flow — is
in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## 📚 Documentation

- **[Usage guide](docs/USAGE.md)** — the 60-second workflow, presenter
  mode, keyboard shortcuts, troubleshooting.
- **[File format spec](docs/FILE_FORMAT.md)** — the `# %%` header,
  `# @explain:` directives, color palette, round-tripping rules.
- **[Architecture](docs/ARCHITECTURE.md)** — components, endpoints,
  kernel lifecycle, data flow.
- **[Development guide](docs/DEVELOPMENT.md)** — repo layout, running
  tests, plugging in a real LLM, common gotchas.
- **[Roadmap](docs/ROADMAP.md)** — what's next, and what's not.

## 🛠️ Stack

| Layer       | Pieces |
|-------------|--------|
| Frontend    | React 18 · TypeScript · Vite · Tailwind · Monaco · React Flow · roughjs · zustand · framer-motion |
| Backend     | Python 3.9+ · FastAPI · `jupyter_client` · IPython · pydantic |
| File format | Plain `.py` with `# %%` markers and `# @explain:` comment directives |

## 🤝 Contributing

Contributions are very welcome — especially:

- A real LLM backend behind `backend/app/explain.py` (Anthropic / OpenAI / Ollama).
- PDF / PPTX / animated-GIF export.
- A `nbconvert` round-trip so callouts survive `jupyter nbconvert`.
- Plugin system for custom node types (tensor flow viewer, diff viewer, etc.).
- Tests! See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md#testing).

Read [CONTRIBUTING.md](CONTRIBUTING.md) before you start, and the
[Code of Conduct](CODE_OF_CONDUCT.md) for ground rules.

## 🛡️ Security

Local-only by default — the backend runs arbitrary Python with full system
access. **Do not expose port 8000 to the internet** without sandboxing.
See [SECURITY.md](SECURITY.md) for the threat model and reporting process.

## Status

**Alpha.** The file format and `/upload` / `/export` endpoints are
considered stable from `0.1.0` and will round-trip; everything else may
change. Pin a commit if you depend on internals.

## License

[MIT](LICENSE) © 2026 Kader-xai

## Credits

Built on the shoulders of [FastAPI](https://fastapi.tiangolo.com/),
[Jupyter](https://jupyter.org/), [React](https://react.dev/),
[Monaco](https://microsoft.github.io/monaco-editor/),
[React Flow](https://reactflow.dev/),
[roughjs](https://roughjs.com/), and the
[Excalidraw](https://excalidraw.com/) palette.
