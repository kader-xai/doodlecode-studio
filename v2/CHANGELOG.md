# Changelog

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
