# DoodleCode Studio

> The current version is tracked in [CHANGELOG.md](CHANGELOG.md) and
> surfaced in the in-app `?` help overlay. See
> `backend/app/__init__.py` for the canonical lockstep pin.

A doodle-powered Python notebook + presentation canvas. Code cells with a
persistent Python kernel, markdown, images, YouTube embeds, live browser
panes, a whiteboard, a full suite of hand-drawn charts (flowcharts, bar,
line, pie/donut, scatter — with axis titles), Mermaid, KaTeX math,
multi-callout bubbles with images, live **reveal-step** code build-ups,
per-slide **speaker notes**, and presentation mode with fading pen /
highlighter / fixed-pen ink and a gentle slide entrance animation — all
in **one local app, one `.py` file per notebook**.

## Quickstart

```bash
cd v2
./start.sh           # builds the UI once, serves everything on http://localhost:8001
./start.sh --dev     # Vite hot-reload on :5174 + API on :8001
```

First run will create a `backend/.venv`, install Python deps, install
npm deps, build the frontend, and launch FastAPI.

## Optional tools

For the **PPT → PNG** converter under `/tools`:

```bash
# macOS
brew install libreoffice poppler
# Ubuntu
sudo apt install libreoffice poppler-utils
```

For **matplotlib inline figures** in code cells:

```python
# from inside a code cell:
import matplotlib.pyplot as plt
plt.plot([1, 2, 3]); plt.show()
```

If matplotlib isn't installed yet, open **📦 Install** in the toolbar
and type `matplotlib`.

## Cell types

| Cell        | Add via                     | Body content                              |
|-------------|-----------------------------|-------------------------------------------|
| Code        | `＋ Code` / N               | Python; runs in a persistent kernel       |
| Text        | `＋ Text` / T               | Markdown (see [below](#markdown-in-text-cells)) |
| Media       | `＋ Media` / M              | Image, direct video (`.mp4`/`.webm`/…), YouTube, or Vimeo URL. `?t=1m30s` start + `?autoplay=…&mute=…&loop=…&controls=…` flags honored on all video types (direct files default to a silent background loop; add `?controls=1&mute=0` for a real player) |
| Browser     | `＋ Browser` / W            | Live website in an iframe (with proxy)    |
| Whiteboard  | `＋ Draw` / D               | Pen + highlighter + 5 colors + 3 bgs      |
| Diagram     | `＋ Diagram` / G            | Doodle charts (flow/bar/line/pie/scatter), Mermaid, or KaTeX math |
| Animation   | `＋ Animate`                | One frame per line; **→ / Space** transitions to the next frame *in place* during a talk (fade / slide / pop / draw-on). Cycle the style with the 🎞 chip. See [`examples/animation_showcase.py`](examples/animation_showcase.py) |

## Markdown in text cells

Text cells render a small, zero-dependency markdown dialect — enough for
technical and educational writing, nothing more:

| Syntax                          | Renders                                |
|---------------------------------|----------------------------------------|
| `# H1` `## H2` `### H3`         | hand-drawn headings                    |
| `- item` / `* item`             | bullet list                            |
| `- [ ] todo` / `- [x] done`     | task list (read-only checkbox)         |
| `1. item` / `1) item`           | ordered list (keeps the start number)  |
| `> quote`                       | blockquote                             |
| `---`                           | horizontal rule                        |
| `**bold**` `*italic*` `~~strike~~` `` `code` `` | inline emphasis + code  |
| ```` ```lang … ``` ````         | fenced code block (literal, optional language) |
| `[text](url)`                   | link (http/https/mailto/tel/relative only) |
| `\| a \| b \|` + `\| --- \| :-: \|` | table with per-column alignment    |

Not supported (by design): images, nested lists, raw HTML. Use a Media
cell for images and a Diagram cell for charts/flow/math.

See [`examples/markdown_showcase.py`](examples/markdown_showcase.py) for a
deck that exercises every construct above (and round-trips through the
parser, asserted in the backend tests).

## Keyboard

| Key                       | Action                                    |
|---------------------------|-------------------------------------------|
| V / H                     | Select tool / Hand (pan) tool             |
| N / T / M / W / D / G     | Add code / text / media / browser / draw / diagram |
| F2                        | Rename selected cell                      |
| Cmd/Ctrl+D                | Duplicate selected cell(s) — works on groups |
| Backspace / Delete        | Delete selected cell(s) — works on groups |
| C                         | Open callout editor for selected cell     |
| N (cell selected)         | Edit the per-slide speaker note           |
| 🎬 / Shift+R              | Reveal next code build-up step            |
| Cmd/Ctrl+A                | Select every cell on the canvas           |
| Shift / Cmd-click cell    | Add to current selection                  |
| Drag empty pane (Select)  | Lasso-select multiple cells               |
| ← ↑ → ↓                   | Nudge selected cells (10 px; Shift = 50 px) |
| 🔗 toolbar (2 selected)   | Connect / disconnect two cells            |
| Align bar (2+ selected)   | Left / center / right / top / mid / bot · distribute |
| ▾ / ▸ chevron in title    | Collapse / expand a single cell           |
| Cmd/Ctrl+Shift+[          | Collapse every cell                       |
| Cmd/Ctrl+Shift+]          | Expand every cell                         |
| Shift+Enter               | Run the selected code cell                |
| Cmd/Ctrl+Shift+Enter      | Run All code cells (▶▶)                   |
| Cmd/Ctrl+Shift+L          | Clear every output (kernel survives)      |
| ■ Stop (while running)    | Interrupt the kernel (SIGINT / Ctrl+C)    |
| Cmd/Ctrl+0                | Reset zoom to 100%                        |
| Cmd/Ctrl+1                | Fit entire canvas in view                 |
| Tab / Shift+Tab           | Cycle selection                           |
| Esc                       | Deselect · close overlays · exit modes    |
| Cmd/Ctrl+S                | Save (silently if bound to disk)          |
| ?                         | Toggle shortcut help overlay              |
| S                         | Toggle Space / Together layout            |
| F5 / Shift+P              | Toggle 🎬 Present                         |
| → / Space / PageDown      | Next slide (in present)                   |
| ← / PageUp                | Previous slide                            |
| Home / End                | First / last slide                        |
| 1 – 9                     | Jump to slide N (in present)              |
| R                         | Run focused code cell (in present)        |
| P / H / X                 | Pen / Highlighter / Fixed-pen ink         |
| E                         | Erase all ink                             |
| F                         | Toggle browser fullscreen                 |
| B                         | Toggle interact mode (browser cell only)  |

## Drag & drop

Two desktop-to-canvas drops are wired:

- **Image file** (`.png`, `.jpg`, `.gif`, …) — becomes a Media cell at
  the drop point. 5 MB cap. The image is embedded as a data URL so
  the round-trip through the saved `.py` file is self-contained.
- **`.py` notebook file** — opens the file as the current notebook,
  after a confirm prompt so unsaved work isn't clobbered. The
  filename (sans extension) becomes the new notebook name.

## Doodle charts

A Diagram cell set to **🖍 Doodle** compiles a tiny line-based syntax
into hand-drawn SVG. Kinds stack — put several in one cell and they
render top-to-bottom. While editing, the **Insert:** bar seeds a working
sample for each kind, so there's nothing to memorize.

```text
flowchart                     # arrows between boxes
Idea --> Draft
Draft --> Ship

chart: Scores                 # bar chart (title optional)
Python: 8
Rust: 4

stack: Spend by quarter       # stacked bar — part-to-whole per category
series: Eng, Sales, Ops       # segment legend
stack Q1: 5, 3, 2
stack Q2: 6, 4, 3

group: Revenue by region      # grouped bar — compare series side by side
series: 2023, 2024            # one clustered column per series
group NA: 8, 11
group EU: 6, 9

xlabel: Epoch                 # axis titles apply to line / area / scatter
ylabel: Loss
hline Target: 0.3             # dashed reference line (line / area / scatter)
line Train: 0.9, 0.6, 0.4     # one polyline per `line` row
line Val: 0.95, 0.7, 0.55

area Active: 2, 5, 9, 14      # filled trend — one `area` row per series

pie: Runtime                  # pie / donut + % legend
pie Parsing: 15
pie Rendering: 45

scatter: Size vs time         # x/y dots with gridlines
point: 1, 2
point: 3, 5
```

| Kind      | Trigger line(s)                        |
|-----------|----------------------------------------|
| Flow      | any line containing `-->`              |
| Bar       | `chart: Title` + `Label: number` rows  |
| Stacked   | `stack: Title` + `series: A, B` + `stack Cat: a, b` |
| Grouped   | `group: Title` + `series: A, B` + `group Cat: a, b` |
| Line      | `line Label: n, n, n` (comma/space)    |
| Area      | `area Label: n, n, n` (filled line)    |
| Pie       | `pie: Title` + `pie Label: number`     |
| Scatter   | `scatter: Title` + `point: x, y`       |
| Axis      | `xlabel: …` / `ylabel:…` (line/area/scatter) |
| Reference | `hline: 0.5` or `hline Label: 0.5` (line/area/scatter) |

See [`examples/data_viz_demo.py`](examples/data_viz_demo.py) for a deck
that exercises every kind plus speaker notes and reveal steps.

### Data → chart syntax from a code cell

Compute numbers in a **Code** cell and let the built-in `doodle` helper
emit the matching chart source (no import needed) — then paste it into a
Doodle diagram:

```python
counts = {"Python": 8, "Rust": 4, "Go": 6}
print(doodle.bar(counts, title="Lines of code"))
print(doodle.line({"Train": [0.9, 0.6, 0.4]}, xlabel="Epoch", ylabel="Loss"))
print(doodle.area({"Active": [2, 5, 9, 14]}, xlabel="Week", ylabel="Users"))
print(doodle.stack({"Q1": [5, 3], "Q2": [6, 4]}, series=["Eng", "Ops"]))
print(doodle.group({"NA": [8, 11], "EU": [6, 9]}, series=["2023", "2024"]))
print(doodle.pie(counts))
print(doodle.scatter([(1, 2), (3, 5)], xlabel="x", ylabel="y"))
print(doodle.table(counts, headers=["Lang", "LOC"]))  # markdown for a Text cell
```

`doodle` exposes `bar` · `line` · `area` · `pie` · `scatter` · `flow`,
each taking a dict (or list of pairs) and returning ready-to-paste
syntax. Ints stay ints, floats are trimmed, non-positive pie slices are
dropped.

**Skip the paste — go live.** A Doodle diagram can pull a code cell's
output directly with a `live: <codeCellId>` line. Whenever that code
cell runs and prints chart syntax, the diagram re-renders:

```text
live: c3          # c3 is a code cell that prints doodle.bar(...)
```

Static chart lines can sit alongside `live:` blocks in the same
diagram. (The cell id shows in the 🔍 Cmd/Ctrl+K palette.)

## File format

One `.py` file per notebook. Cells are separated by `# %%` headers.

```python
# doodlecode format-version: 3
# notebook: my-deck

# %% kind=code id=c0 x=80 y=80 w=580 h=300
# @title: Hello, Python
# @explain: This is a callout bubble
# @link_to: d0
print("hi")

# %% kind=diagram id=d0 x=720 y=80 w=560 h=420
# @title: Flow + chart
# @diagram_kind: doodle
# @collapsed: true
flowchart
A --> B
B --> C

chart: progress
A: 6
B: 8
C: 10
```

Optional directives (additive — old files keep loading):

- `# @callout` — start a new bubble (multi-callout support)
- `# @image: data:image/png;base64,…` — embed an image in the current bubble
- `# @link_to: <id>` — draw a sketchy line to another cell (v2.1.0+)
- `# @collapsed: true` — render only the title strip (v2.2.0+)
- `# @reveal: <code>` — a build-up step typed in live during a talk;
  one directive per step, newlines escaped as `\n` (v2.6.0+)
- `# @note: <text>` — a presenter speaker note shown only to you
  (bottom-left HUD) while presenting; newlines escaped (v2.6.0+)
- `# @transition: <style>` — animation-cell frame transition
  (`fade` / `slide` / `pop` / `draw-on`); frames live in the body, one
  per line (v2.11.0+)

Old `# @explain:` files load as `callouts[0]` automatically — files
written by any prior version still open.

## Export

**File ▸ Export Markdown…** downloads the deck as a plain `.md` handout:
titles become `##` headings, code → fenced ```python blocks, diagram and
chart sources → fenced ```text blocks, image media → `![]()`, video and
browser cells → links, and audience-facing callouts → blockquotes.
Speaker notes stay presenter-private and are omitted. Backed by
`POST /api/export/markdown` (pure, dependency-free `app/export_md.py`).

## Tests

```bash
cd v2/frontend && npm test
cd v2/backend  && .venv/bin/python -m pytest tests/ -q
```

## Architecture

- **Backend** — FastAPI (`v2/backend/app/`)
  - `main.py` — routes
  - `kernel.py` + `runner.py` — persistent Python child process
  - `executor.py` — façade
  - `notebook_io.py` — `.py` serializer + parser
  - `proxy.py` — X-Frame-bypass proxy with SSRF guard
  - `installer.py` — pip install with regex allow-list
  - `tools.py` — PPT → PNG (LibreOffice + pdftoppm)
- **Frontend** — React 18 + Vite + Zustand + ReactFlow (`v2/frontend/src/`)
  - `store.ts` — single source of truth for cells, selection, theme, etc.
  - `components/` — one file per cell type + toolbar + modals
  - `lib/` — markdown renderer, doodle-diagram compiler

## License

MIT.
