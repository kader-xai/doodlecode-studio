# Changelog

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
