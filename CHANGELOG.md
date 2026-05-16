# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] — 2026-05-16

### Added
- **One-click package installs.** Toolbar **📦 Install** button opens a
  prompt that runs `pip install` inside the kernel's venv; packages are
  importable on the next `import` (no kernel restart).
- **Automatic install chip on `ModuleNotFoundError`.** The output panel
  shows "📦 Install foo" when a cell fails on a missing module; common
  aliases (`cv2`, `PIL`, `sklearn`, `yaml`, `bs4`) are remapped to PyPI
  names.
- `POST /install` backend endpoint with input validation (refuses shell
  metacharacters).
- **10-part Python-for-Machine-Learning curriculum** in `examples/`:
  numpy, pandas, viz, statistics, linear algebra, probability,
  preprocessing, sklearn basics, regression, neural networks.
- **Test suite**: 80 pytest tests for the backend (parser, serializer,
  explainer, install validation, HTTP endpoints) and 24 vitest tests
  for the frontend (store, palette, Outputs component) — all green.
- **Lint configs**: `ruff` for Python, full TypeScript strict mode for
  the frontend. CI enforces both.
- **CI runs lint + unit tests + build** across Python 3.9 / 3.11 / 3.12
  and Node 18 / 20.
- New file output: serializer emits a `# doodlecode format-version: N`
  preamble so future readers can detect the level.

### Changed
- **Figma / Excalidraw-style canvas behaviour** — no more arrow / hand
  tool switcher. Dragging an empty area pans, dragging a cell moves it,
  both at once.
- **One single output box** with `↳ output` label, colored left stripes
  per output kind (stdout / stderr / result / display / error).
- Removed the `[N]` execution-count badge and green `ok` pill from the
  output header (only the red `error` pill stays — it's the one that
  conveys information you can't see elsewhere).
- Outputs render outside the doodle border so they're always visible,
  with `ResizeObserver` reporting actual cell height so the next cell
  auto-shifts down when stdout grows.
- Auto-fit zoom on presentation focus (uses `fitBounds` against the
  measured cell + callout bounds, no zoom reset on plain edits).
- Canvas completely locked during presentation: no wheel pan, no
  scroll-zoom, no pinch, no node drag, no hover-focus.

### Fixed
- **Round-trip bug**: column-aligned multi-space text inside `@explain`
  bodies was being collapsed to single spaces on save. Caught by the
  new `test_internal_multispace_survives_round_trip` test.
- **Unicode escape bug**: titles containing em-dash (`—`), superscript
  (`²`), or any non-ASCII character were mangled by
  `decode("unicode_escape")`. Fixed with a manual unescape that's
  encoding-safe. Caught by `test_unicode_title_round_trip`.
- The "Cell 5a8b…" placeholder label on cells without a kind no longer
  shows — header is clean when there's nothing to say.
- Camera no longer flies to whichever cell the mouse hovers over — the
  unintentional `onMouseEnter → focus` was removed.
- Run, Edit, callout-editor popover, and the output panel now carry
  `nodrag` so clicks never start a card-drag.

## [0.2.0] — 2026-05-16

### Added
- **Multiple callouts per cell** via `# @callout` separator. Each callout
  may carry its own `title`, `color`, `kind`, `explain`, `image`, `tags`.
- **Image attachments** on callouts (`# @image:` directive, data URL or
  path). Embedded thumbnails render inside the bubble.
- **Keyboard navigation** in presentation mode: `→` / `Space` / `PageDown`
  next, `←` / `PageUp` prev, `Home` / `End` jump, `Esc` to exit. `↑` / `↓`
  are intercepted to prevent autoscrolling during a talk.
- **`/version` endpoint** returning `{app, format_version}`. Versions also
  exposed in the About modal.
- **`CLAUDE.md`** capturing the project's behavioural rules so future
  contributors / coding assistants stay aligned.
- **Format-version stamp** at the top of every saved `.py` file.

### Changed
- Bumped file-format level to **v2**. v1 files still parse — extra v2
  features degrade gracefully.
- Sketchy borders now use a `solid` fill (was `hachure`) — clearer
  output panel and callouts, no more diagonal stripes.
- Dark-mode palette retuned for legibility; callout text is light on dark.
- Cell-chain connectors are now thin solid lines (was dotted).
- Selected-cell outline is a solid pink ring (was dashed).
- Callout edges are solid in dark mode.

### Fixed
- Presentation pan no longer resets the user's zoom level.
- Removed all `Claude` / `Anthropic` brand mentions from docs.

## [0.1.0] — 2026-05-16

### Added
- Real IPython-kernel execution backend (`POST /execute`) with persistent
  per-session kernels and full mime-bundle support (text, html, png).
- Upload (`POST /upload`) supporting `.py`, `.ipynb`, `.md`. Round-trippable.
- Cell-callout file format: `# %% kind=… color=… title="…"` headers and
  `# @explain:` / `# @tags:` directives. See [docs/FILE_FORMAT.md](docs/FILE_FORMAT.md).
- Hand-drawn React Flow canvas: code cells on the left, user-authored
  callout bubbles on the right, animated dashed connectors.
- Color-coded sections (Excalidraw-inspired vibrant palette) shared across
  cell header, editor left strip, and callout bubble.
- In-app callout editor (`✎`) with live preview.
- Export (`POST /export`) and auto-save (`POST /autosave`) to
  `~/.doodlecode/`, plus `localStorage` snapshot in the browser.
- Presentation mode with cell-by-cell navigation; pan-only (no zoom reset).
- Dark / light theme toggle with persistent preference.
- About modal with author links.
- Example modules: Python basics, file handling, AI doodle (PyTorch),
  and a self-guided walkthrough.

### Known limitations
- Kernel output is request/response, not streamed.
- No PDF / PPTX export yet.
- No multi-user collaboration.
- No PyTorch-specific tensor visualizer.
