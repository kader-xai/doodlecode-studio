# Changelog

## [Unreleased]

### Added (iter 71-73)
- **Cmd/Ctrl+/ toggles collapse on the selected cell** — paired with
  the iter 62 Cmd+K palette workflow: jump to a cell, collapse it,
  jump to the next, no mouse trip needed.
- **Palette stats footer.** The bottom of the Cmd+K modal now shows
  `N cells · K collapsed · L links` next to the keyboard hint so the
  user sees notebook structure at a glance every time they open it.
  Link count dedupes symmetric pairs.

### Refactored
- `firstLine` and `hostOf` moved out of `CellPalette` / `BrowserCell`
  into a new `src/lib/cellPreview.ts` so they're unit-testable.

### Tests
- +11 vitest cases for `firstLine` (md/code/blank/truncate) and
  `hostOf` (www-strip / fallback / blank / port). Suite at
  16 backend + 57 frontend = 73 total.

## v2.3.0 — Cmd+K palette + collapse polish

10 iterations on top of 2.2.0 (60-69). Test suite stays at 46
frontend + 16 backend = 62 tests.

### Added
- **Cmd/Ctrl+K cell palette.** Modal that lists every cell by title
  with a kind icon. Type to filter (title AND source body), ↑↓ to
  highlight, Enter to pick. Picking selects the cell and pans the
  canvas to it. Untitled cells show a dim preview drawn from the
  first non-blank source line (markdown / Python-comment markers
  stripped). Matching characters are highlighted in pink.
- **Source-aware filtering.** Palette filter matches the body of each
  cell, not just the title — find a code cell by a variable name.
- **Collapse on Whiteboard cells** (the fifth and final cell type).
  5/5 editable cell types now support collapse.
- **Selection-count chip in toolbar.** When 2+ cells are selected
  the toolbar shows "▣ N cells selected" so the user can confirm
  the group before bulk actions (Delete, Cmd+D, Align, Link).
- **Collapsed Browser cells show a host chip** (`🌐 example.com`)
  next to the title so users can tell collapsed browsers apart.

### Fixed
- **Duplicate semantics.** `duplicateCell` no longer carries the
  source cell's outgoing links (they'd be asymmetric — target cells
  wouldn't know about the duplicate). The copy gets its own deep-
  cloned callouts so editing one bubble doesn't mutate the source.
- **Collapsed Diagram + Browser actually shrink.** Iter 56 hid the
  body but the outer wrapper still claimed `cell.h` pixels of empty
  space. Outer now drops to ~44 px (just the title strip) when
  `cell.collapsed` is true.

### Docs
- v2/README.md keyboard table refreshed for v2.1.0 / v2.2.0 — 16
  new shortcuts documented; file-format example shows `@link_to` and
  `@collapsed`; optional-directives section calls out each directive's
  release of introduction.

### Tests
- +5 vitest cases for `duplicateCell` semantics, `setPaletteOpen`,
  `panToCell` (+ repeat-bump). Suite at 46 frontend tests.

## v2.2.0 — collapse system + zoom + Jupyter-style shortcuts

7 iterations on top of 2.1.0 (51-57). Test suite now 16 backend + 41
frontend = 57 total.

### Added
- **Collapse / expand cells.** Every editable cell type (Code,
  Markdown, Diagram, Browser) gets a small ▾/▸ chevron in its title
  strip. Click to hide the body and shrink to just the title row.
  Round-trips through the `.py` via an additive `# @collapsed: true`
  directive (omitted when False so files stay clean).
- **Bulk collapse / expand.** Cmd/Ctrl+Shift+`[` collapses every
  cell, Cmd/Ctrl+Shift+`]` expands. Big notebooks become a
  scannable list of titles.
- **Zoom shortcuts.** Cmd/Ctrl+0 resets to 100%, Cmd/Ctrl+1 fits
  every cell in view (animated). Both skip while typing in editors.
- **Shift+Enter runs the selected code cell** — Jupyter convention.
- New `store.setAllCollapsed(bool)` action.

### File format
- New optional `# @collapsed: true` directive on a cell. Files saved
  before this release have no directive and parse with
  `collapsed = false`. Files saved by 2.2.0 still parse cleanly in
  2.1.0 (the unknown directive is ignored).

### Tests
- +3 vitest cases for collapse (single + bulk).
- +2 pytest cases for `@collapsed` round-trip + back-compat.

## v2.1.0 — multi-select, group ops, cell↔cell connections

19 iterations of UX work on top of the 2.0.0 base. Highlights below;
test suite went from 23 → 52 (14 backend + 38 frontend).

### Added (iter 32-42 batch)
- **Drag image files onto canvas → Media cell** at the drop point.
  5 MB cap, `image/*` mime guard, data-URL so the round-trip survives
  Save → reload.
- **Multi-select**: lasso-drag on empty pane (Select mode), Shift /
  Cmd-click to extend. ReactFlow moves the whole group on drag.
- **Group operations**: Backspace / Delete removes every selected
  cell; Cmd/Ctrl+D duplicates the group; arrow keys nudge (10 px,
  Shift = 50 px); Cmd/Ctrl+A selects every cell.
- **Align + distribute bar** appears in the toolbar when 2+ cells are
  selected: left / center-X / right / top / middle-Y / bottom plus
  distribute-H/V (≥3 cells, gaps spread evenly).
- **▶▶ Run All Cells** button + Cmd/Ctrl+Shift+Enter shortcut runs
  every code cell top-to-bottom against the persistent kernel and
  halts at the first error.
- **🧹 Clear Outputs** + Cmd/Ctrl+Shift+L wipes every output panel
  without restarting the kernel — variables and imports survive.
- **Jupyter-style `[n]` execution counter** badge on every code cell;
  resets to 0 on ↻ Kernel / New notebook.
- **Elapsed-ms chip** beside the `[n]` badge (`142ms` / `1.42s`).
- **Red doodle border** when a code cell's last run errored.

### Changed
- Help overlay (`?`) now documents every new shortcut.

### Tests
- +8 vitest cases covering `deleteCells`, `alignSelected` (3 modes),
  `runAllCells` (success + error halt), `clearAllOutputs`. Suite at
  31 passing.

### Added (iter 44-47 batch)
- **■ Stop button** while a code cell is running. SIGINTs the kernel
  subprocess — equivalent to Ctrl+C inside the user's `exec()`. The
  runner catches KeyboardInterrupt → normal error response, kernel
  survives. New `POST /api/kernel/interrupt` endpoint.
- **🔗 Cell ↔ cell connections.** Select exactly two cells, click 🔗
  Link in the toolbar — a sketchy solid line appears between them
  (any pair: code↔text, browser↔diagram, etc.). Visually distinct
  from the dashed dot-flow that connects cells to callouts. Round-
  trips through the .py via additive `# @link_to:` directives; old
  files unaffected. Deleting a cell prunes dangling references.
- **Symmetric link store.** `linkCells(a, b)` writes the link on
  both endpoints so deletion of either end stays consistent.

### Changed
- **DoodleBorder rewrite.** Wide cells (browser 720×480, media
  480×320) no longer stretch the wobble pattern. ResizeObserver now
  reads the parent's real W×H; viewBox is 1:1 so corners stay round
  and jitter stays proportional across long edges. Anchor points are
  resampled every ~64 px so long sides actually wobble.

### Tests
- +7 vitest cases for `linkCells` (symmetric + idempotent + no-self),
  `unlinkCells`, `toggleLinkSelected` (toggle + no-op cases), and
  `deleteCell` link-pruning. Suite at 38 passing.

## v2.0.0 — initial v2 release

Complete from-scratch rewrite. v1 stays at v1.4.0 on `main`; v2 lives
under `v2/` and runs alongside on its own port (8001 vs v1's 8000).

### Cells
- Code cells with Monaco + a **persistent Python kernel** — variables,
  imports, and matplotlib state carry across cells
- Markdown cells with `#/##/###`, `**bold**`, `*italic*`, `` `code` ``,
  bullets, blockquotes, horizontal rules
- Media cells — images, videos, **YouTube + Vimeo embeds**, broken-
  image fallback, corner resize
- Browser cells — iframe with URL bar, Back/Forward/Refresh, **B-key
  interact gate**, optional **`/api/proxy` to bypass X-Frame blocks**
- Whiteboard cells — pen + highlighter + stroke-eraser, 5 colors, 3
  backgrounds, undo/clear, hi-dpi crisp
- Diagram cells — **Doodle flow + bar chart**, **Mermaid**, or **KaTeX
  math**; switch per cell

### Editing
- Click-to-select, drag-to-move, double-click-to-edit
- F2 rename, Cmd/Ctrl+D duplicate, Tab/Shift+Tab cycle
- Multi-callout per cell with text + image (file picker, drag-drop, paste)
- Cell size presets S/M/L/XL/Fit + free corner-drag
- Local-draft text editor pattern keeps typing rock-solid

### Canvas / layout
- V (Select/Move) / H (Hand pan) tool modes
- Pan via wheel; Cmd/Ctrl+wheel zoom; pinch zoom
- **S** key spreads cells one-per-slide (Space) / packs them back (Together)

### Presentation
- F5 / Shift+P toggle 🎬 Present
- Auto-center each slide on the cell's bounding box
- Non-focused cells fade to 35% opacity
- Arrow / Space / PageDown / PageUp / Home / End navigation
- R runs focused code cell; F toggles fullscreen
- **P / H / X** pens (fading red / fading yellow / fixed red), **E**
  erases all — built right this time (z-9999 overlay, ref-tracked
  strokes, currentTarget pointer capture, touchAction:none)

### File handling
- Save / Open `.py` files (round-trip stable for every cell type)
- **File System Access API** integration: bound file ⇒ silent Save
- Cmd/Ctrl+S keyboard
- localStorage autosave
- Backwards-compatible with v1 `@explain:` callouts
- 🎁 demo tour bundled in `examples/demo.py`

### Server-side tools
- `/api/install` — `pip install` with shell-injection guard, auto-resets
  the kernel
- `/api/kernel/reset` + toolbar ↻ Kernel
- `/api/proxy` — server-side fetch with SSRF guard, strips X-Frame
- `/tools` page — **PPT → PNG** via LibreOffice + pdftoppm

### Look + feel
- Hand-drawn doodle aesthetic, polished
- Dark mode that actually works
- 4-theme ambient background animations (off / geometry / nature /
  science)
- Animated dashed connectors with flowing dots between cells and callouts

### Tests
- 23 frontend tests (vitest) — store CRUD, doodle parser, markdown
- 11 backend tests (pytest) — notebook_io round-trip, installer guard
