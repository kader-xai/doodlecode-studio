# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.3.9] — 2026-05-17 — **Latest Stable** 🥇

### Added
- **🖊 Fixed pen** — third presenter ink tool. Same red color and
  width as ✒️ Pen, but the stroke does NOT fade — it stays on top
  of the slide until you erase or leave presentation. Keyboard
  shortcut **X**.
- **🧽 Erase all** — wipes every ink stroke currently on screen
  (pen, highlighter, fixed pen) in one click. Bumps a store
  counter that the overlay subscribes to. Keyboard shortcut **E**.

### Changed
- Presenter bar bottom hint updated:
  `← → · P pen · H highlighter · X fixed · E erase · F fullscreen · Esc exit`.

### Compatibility
- Exiting presentation still clears every annotation, including
  fixed-pen strokes — slides are never permanently inked. No file-
  format changes.

## [1.3.8] — 2026-05-17

### Added
- **Whiteboard shape tools** — Pen / Line / Circle / Arrow / Eraser.
  Pen stays freehand; Line / Circle / Arrow draw via click-drag with
  live preview; Eraser removes any stroke under the cursor (segment
  hit-test, radius driven by the width slider). Arrow gets a filled
  triangular arrowhead. Each saved stroke now carries an optional
  `kind` field; whiteboards written by 1.3.7 still load as pen
  strokes automatically.

### Compatibility
- File format v2.2 unchanged. `cell.meta.strokes` schema is purely
  additive (new optional `kind` field on each stroke object).

## [1.3.7] — 2026-05-17

### Added
- **✨ Vibe picker** — five presenter-ambient themes: 🎨 Doodle
  (squiggles), 🌿 Zen (ensō, leaves, clouds, mountains), 💻 Tech
  (servers, terminals, chips, gears, Wi-Fi), 💡 Ideas (lightbulbs,
  sparkles, paper planes, sticky notes), 🚫 Off. Hand-drawn SVG
  paths in a uniform 60 × 60 viewBox; each theme has 6–9 shapes;
  stroke color slowly cycles through the doodle palette.
- **🌓 BG picker** — page background swatches: **Sandal** (default
  warm), **Gray** (neutral), **White** (projector-ready), **Black**
  (auto-enables dark mode). Replaces the binary 🌙/☀ toggle.
- **Browser cell — Back / Forward / Refresh** — session-only URL
  stack maintained per cell (not persisted to .py). ◀ ▶ buttons are
  disabled when the stack ends; ↻ remounts the iframe via key bump.
- **Browser cell — 🛡 Proxy toggle** — opt-in routing through
  `/api/proxy` that strips `X-Frame-Options` / CSP frame-ancestors
  and injects `<base href>` so public sites that refuse iframing
  can be embedded. SSRF-guarded, 8 MB / 15 s caps. Cookies are
  intentionally NOT forwarded — every fetch is a clean GET. UI
  hint surfaces the trade-offs.
- **Browser cell — 1280 × 760 default** with 16:9 aspect and per-
  type focus width during presentation so the iframe fills the
  screen on every step-pan.
- **/tools — LibreOffice-backed PPT renderer** — accurate slide
  screenshots (fonts, colors, layouts intact) replace the text-only
  fallback when LibreOffice is on PATH. `start.sh` prints a one-
  line install hint if missing.

### Changed
- **Doodle ambient now visible outside presentation** at lower
  opacity (0.22 light / 0.16 dark vs 0.45 / 0.32 in presenter).
  The vibe choice is reflected immediately while editing.
- **Background contrast preserved** across all four page bg
  swatches — dark text on light bgs, white text on black, dot-
  pattern texture stays soft on every variant.

### Fixed
- **Wide cells (Whiteboard / Browser / media-only) no longer shift
  right during presentation.** fitBounds focus region uses the
  cell's actual rendered width (cellSize override + per-type
  defaults: 1280 px browser, 1100 px whiteboard, 720 px media,
  580 px otherwise).
- **Browser URL bar can't navigate the parent page** — input wrapped
  in `<form onSubmit={preventDefault}>`, Go is `type="submit"`,
  protocol auto-prefixed for `localhost:…` (http) and bare hosts
  (https).

### Compatibility
- File format unchanged (still v2.2). New UI state
  (`presenterAmbient`, `pageBg`, browser proxy toggle, browser
  history) is session-only / localStorage and never serialized into
  `.py` files.

## [1.3.6] — 2026-05-17

### Added
- **New cell types** (file-format v2.2, additive — old files load
  unchanged):
  - **＋ Browser** cell — embeds any URL in an iframe with a URL bar.
    Auto-prefixes the protocol, opens external sites in a real tab
    via the ↗ link, sandbox is permissive enough for typical apps.
  - **＋ Whiteboard** cell — canvas drawing surface with 7 pen
    colors, 1–24 px width slider, white / black background toggle,
    undo, clear, and draggable / resizable image stickers. Strokes
    and sticker positions autosave into `cell.meta.strokes` /
    `cell.meta.stickers` as JSON.
  - **＋ Image / ＋ Video** toolbar buttons that drop a media-only
    markdown cell with a single `![](…)`. Renders frameless and
    full-bleed with `object-fit: contain`. Drag the corner to
    resize both width and height, or pick **S / M / L / XL / Fit**
    presets from the toolbar selection bar.
- **Selection-driven toolbar action bar.** Click any cell or callout
  → toolbar shows "Selected: …" with **✏️ Edit** and **🗑 Delete**.
  Per-card buttons are gone — cards stay clean during presentation.
- **`/tools` page** — visit `http://localhost:8000/tools` (or
  toolbar 🛠 Tools button). First tool: **PPT → Images**. Upload a
  `.pptx`, get one PNG per slide plus a `notes.txt` of speaker
  notes under `~/.doodlecode/tools/<deck>/`. Uses LibreOffice
  headless when installed; falls back to a python-pptx text
  renderer if not (warning banner suggests `brew install --cask
  libreoffice`).
- **Inline media in markdown body** — `![](…)` inside text cells
  renders the image / video right there, resizable by dragging the
  corner.
- **Demo media assets** (`frontend/public/demo/`) — bouncing-ball
  GIF, wave MP4, chart PNG, architecture PNG — plus
  `examples/media_demo.py` and `examples/full_demo.py` decks
  exercising the new features.

### Fixed
- **Wide cells (whiteboard / browser / media-only) no longer
  shift right during presentation.** The presenter `fitBounds`
  region now uses the cell's actual rendered width (from
  `cellSize` + per-type defaults: 960 px for whiteboard / browser,
  560 px for media-only, 580 px for the rest) instead of always
  `CARD_W`. Cluster lands centered, fills the screen.
- **Browser URL bar.** Wrapped in `<form onSubmit={preventDefault}>`
  with `type="submit"` on Go so Enter / click never triggers a
  parent-page navigation. URLs without a protocol auto-prefix
  (`localhost:3000` → `http://`, otherwise → `https://`).
- **Slide counter** in the presenter bar now has explicit
  `text-ink dark:text-white` (was inheriting black on dark).

### Removed
- **Per-card edit / delete buttons** on code, markdown, and callout
  nodes — replaced by the toolbar selection action bar.
- **✏️ Edit Logo** toolbar button — cluttered the space; the
  branding editor + store action are still in the codebase for
  later re-exposure (e.g. from About).

### Changed
- "📐 Auto-Space [Presentation]" toolbar button renamed to
  **📐 Space** — clearer, less tooltip-heavy.
- Tool name labels ("Cursor tool (V)", "Hand tool (H)", …) removed
  from the status line below the toolbar; tooltips on the icons
  still explain each tool.

### Compatibility
- File format **v2.2** — adds optional `cell_type`, `browser_url`,
  `whiteboard_bg`, `strokes`, `stickers` to `CellMeta`. Old `.py`
  files load identically; new files written with these features
  are silently ignored by older parsers. **100 / 100 backend
  pytest** and **40 / 40 frontend vitest** pass.

## [1.3.5] — 2026-05-17

### Added
- **`examples/roadmap/`** — 90 presentation-ready `.py` decks
  converted from the
  [`kader-xai/data-science-roadmap`](https://github.com/kader-xai/data-science-roadmap)
  Jupyter notebooks. ~2,400 slides total across modules 01–90.
  Code is preserved verbatim; markdown trimmed to short cards with
  1–5 `@explain:` callouts per code slide. Module 1 is hand-tuned as
  the reference style.
- `examples/roadmap/README.md` — attribution + source link.

### Fixed
- **Presentation: callouts clipped on the right edge.** Added a
  `FOCUS_RIGHT_BUFFER` to the fitBounds region used by the presenter
  step-pan, so the right-most callout has breathing room on narrower
  screens. Code and markdown slides now use the SAME focus-region
  width (always sized around the cell card, never widened by the
  callout column), so both slide types center at the same horizontal
  position during a talk. Click-to-focus and open-pan keep their
  original centering.

## [1.3.4] — 2026-05-16

### Added
- **Single-port deployment.** `./start.sh` builds the React UI once
  and serves both the UI and the API from `http://localhost:8000`.
  End users no longer need `npm run dev`. `./start.sh --dev` keeps
  the old hot-reload flow for development.
- **Per-cell Delete button** (🗑) in both code and text cell headers.
  Confirms before deletion. The chain connector auto-reconnects the
  remaining cells in order (delete cell 3 from 1→2→3→4→5 and the
  chain becomes 1→2→4→5 immediately).

### Fixed
- **/execute returned 405** after the static-mount change. API
  routes are now exposed at both `/api/*` (canonical) and `/*`
  (legacy alias) so any cached client keeps working.
- **Dark-mode slide counter** in the presenter bar was rendering in
  black on a dark background. Now uses `text-ink dark:text-white`.

### Removed
- **Recording feature** (screen / camera / mic capture) — the
  presenter bar 🔴 button, `RecorderController`, `RecorderSetup`,
  and `CameraPiP` components are all gone, along with their store
  state. Bundle size dropped ~4 KB gzip as a result.

### Compatibility
- File format unchanged. Old notebooks load and save identically.

## [1.3.3] — 2026-05-16

### Added
- **✏️ Edit Logo** button in the toolbar (right of 📦 Install) opens a
  branding editor: customize the logo emoji and the full author byline
  ("Co-AI Developed by …" or anything else). Live preview, ↺ Reset,
  💾 Save. Values persist in `localStorage` and propagate to the
  toolbar wordmark + About modal title + author card.
- Meetup URL canonicalized to
  <https://www.meetup.com/machine-learning-group-riyadh> (no `/g/`
  prefix) everywhere it appears.

### Compatibility
- File format unchanged. UI / branding metadata only.
- Older `{name}` branding payloads in localStorage auto-migrate to a
  full byline on first load — no user action needed.

## [1.3.2] — 2026-05-16

### Added
- **Font-size A− / A+ control** next to the 🎨 Design picker in the
  toolbar. Scales the whole UI 80%–160% via the root `font-size`;
  persists to `localStorage`.

### Changed
- About modal: License, Community, and "Point your AI" demoted to
  compact one-line chips under a dashed divider so the four primary
  cards (Star/clone, LinkedIn, GitHub, Website) stay visually dominant.
- Toolbar "🎨 DoodleCode" wordmark now sets explicit
  `text-ink dark:text-white` — previously inherited body color and
  appeared near-black against the dark canvas on some setups.

### Compatibility
- File format unchanged. UI only.

## [1.3.1] — 2026-05-16

### Added
- **🤝 Community Work** card in the About modal, linking to the Riyadh
  ML meetup the author runs:
  <https://www.meetup.com/machine-learning-group-riyadh>.
- **📜 License** card in the About modal — explicit "MIT © 2026 Kader
  Mohideen" so anyone presenting from the app can show the license
  attribution on screen.
- README now lists the Riyadh ML Meetup alongside LinkedIn / GitHub
  in the author byline, and the **License section** explains why MIT
  (vs. AGPLv3) was chosen.

### Changed
- LICENSE copyright holder updated to **Kader Mohideen** (canonical
  full name, matching the About modal author credit).
- `backend/pyproject.toml` `authors` and `frontend/package.json`
  `author.name` aligned to the same canonical name.

### Compatibility
- File format unchanged. Metadata + UI text only.

## [1.3.0] — 2026-05-16

### Added
- **[docs/AI_HANDOFF.md](docs/AI_HANDOFF.md)** — single-page briefing
  for any AI assistant (or human) taking over the project. Covers
  architecture, file format, conventions, quality bars, repo layout,
  and where to start. Linked from the README.
- **🤖 "Point your AI" section** at the bottom of the About modal,
  showing the file path `docs/AI_HANDOFF.md` so users can paste it
  straight into another assistant.
- **🎨 Design picker** in the toolbar with **four font themes**:
  - **Doodle** (golden default) — Caveat + Patrick Hand
  - **Professional** — Inter sans-serif
  - **Serif** — Lora editorial serif
  - **Mono** — JetBrains Mono terminal feel
  Choice persists to `localStorage` and is applied app-wide via a
  CSS custom property (`--font-display`) on `<html>`.

### Fixed
- **Dark-mode text contrast floor.** Added a global CSS pass that
  forces every Tailwind `text-ink/N` and `border-ink/N` utility to a
  bright light-on-dark equivalent when `<html class="dark">` is set.
  Stops author-level oversights from producing dark-on-dark text in
  the About modal or anywhere else.

### Compatibility
- File format unchanged.

## [1.2.0] — 2026-05-16 · **🥇 GOLDEN STABLE**

The recommended production version. All the polish and bug-fixes from
the v1.1.x line, rolled up into one named release.

### What's in it

- **Canvas** — three explicit tools (Cursor / Hand / Move), auto-grow
  cells, ResizeHandle drag, inline title rename, no internal scrollbars.
- **Borders** — single clean CSS border on every cell type, identical
  on code / text / callout. No SVG drift, no double-border confusion.
- **Cells** — code with Monaco + colored top strip + chunky left edge,
  text with markdown + image + title, callouts with multi-bubble +
  image + color picker.
- **Presentation** — auto-fit per slide, arrow-key navigation, ✒️ Pen
  (Excalidraw-style fading red ink, **P**), 🖍 Highlighter (**H**),
  ⛶ Fullscreen with auto-hiding chrome (**F**), Esc to exit.
- **Kernel** — real IPython, matplotlib inline rendering, one-click
  📦 pip install with auto-invalidate-caches.
- **File format** — v2 (`# %% kind=… color=… title="…"` + `# @explain:`
  / `# @callout` / `# @image:` directives) is a stable contract.
  Files round-trip byte-stable.
- **Quality** — 92 backend pytest + 40 frontend vitest = 132 green
  tests; ruff lint clean; TypeScript strict clean; production build
  116 KB gzip; CI matrix Python 3.9/3.11/3.12 × Node 18/20.

### Migration

None required from any v1.x. Just `git pull` and `./start.sh`.

## [1.1.5] — 2026-05-16

### Changed
- **Removed the wavy SVG border accent from every cell type.** It
  was visually confusing — a second line floating inside the CSS
  border, and the callout's wavy line never quite matched the code
  cell's. Now every card (code, text, callout) has the SAME clean
  CSS border: 2 px solid + 4 px / 5 px chunky offset shadow + rounded
  corners. Consistent, reliable, no double-borders.
- The doodle aesthetic comes from the colors, the Caveat / Patrick
  Hand font, and the offset shadow — the same ingredients that make
  Excalidraw feel hand-drawn without any wavy lines.

### Compatibility
- File format unchanged.

## [1.1.4] — 2026-05-16

### Changed
- **Doodle aesthetic is back — without the alignment bug.** Cards now
  have a TWO-layer border:
  - **CSS layer**: a 1 px solid line with the chunky offset shadow.
    This is the geometric truth — it's part of the box, so it can't
    misalign by definition.
  - **SVG layer on top**: a hand-drawn wavy stroke from rough.js,
    `fill: none` (so it can never paint over content). It's purely
    decorative.
  Result: code cells and text boxes look hand-drawn again (no more
  "looks like VS Code"), and the perfect alignment is guaranteed by
  the CSS layer underneath.
- `DoodleBorder` keeps its self-measuring ResizeObserver from v1.1.1
  so the wavy stroke tracks the parent. Even if it momentarily lags
  by a pixel, the CSS layer is already in place — no visible gap.

### Compatibility
- File format unchanged.

## [1.1.3] — 2026-05-16

### Fixed
- **"Rendered fewer hooks than expected" crash when going fullscreen.**
  `Toolbar` had an early `return null` placed BEFORE some `useStore`
  calls. When `fullscreen + presenting` flipped to true, React saw a
  shorter hook list than the previous render and threw. Moved the
  early return below every hook so the count is always stable. Rule
  of Hooks violation → fixed.

### Compatibility
- File format unchanged.

## [1.1.2] — 2026-05-16

### Changed
- **Replaced the wavy SVG border with a plain CSS border** on every
  cell type. The SVG-based border had too many races (React state vs.
  ResizeObserver vs. ReactFlow transform) and was visibly drifting off
  the box on load and during resize. The new `.doodle-card` has
  `border: 2px solid` + `border-radius: 18` + a sketchy box-shadow —
  it IS the box's own border, so it can never get out of sync.
- The wavy aesthetic comes back from the color palette, the hand
  font, and the offset shadow — net visual loss is minimal.
- Code cells keep their colored top strip and the chunky colored
  left edge on the Monaco editor, so they still read as doodle cards
  and not bare VS Code.

### Fixed
- **Fullscreen no longer triggers the error page.** Wrapped
  `requestFullscreen` / `exitFullscreen` in try/catch + promise
  `.catch()`. Some browsers throw synchronously (Safari, older Chrome
  outside user-gesture); the ErrorBoundary was catching those throws.
  Now they're swallowed silently and the user can re-click the ⛶
  button.

### Compatibility
- File format unchanged.

## [1.1.1] — 2026-05-16

### Fixed
- **Doodle border now ALWAYS matches the rendered card.** Rewrote
  `DoodleBorder` to bypass React state entirely:
  - The wrapper div fills the parent via CSS (`inset: 0`).
  - A `ResizeObserver` watches the parent (the doodle-card).
  - Every size change → the SVG inside is rebuilt imperatively to the
    parent's exact `getBoundingClientRect()` dimensions.
  No more prop-vs-DOM mismatch. The wavy outline tracks the card on
  load, on text wrap, on font load, on image load, on drag-resize —
  every code path.
- `DoodleBorder` no longer takes `width` / `height` props. Callsites
  in `MarkdownNode`, `ExplanationNode`, and `CodeCellNode` simplified
  accordingly.

### Compatibility
- File format unchanged. Pure rendering fix.

## [1.1.0] — 2026-05-16

### Added
- **⛶ Fullscreen presentation mode**, button next to the highlighter
  on the presenter bar (shortcut **F**). Click → the browser goes
  fullscreen, the toolbar disappears entirely, and the presenter bar
  auto-fades after 2.5 s of mouse-idle (reappears on mouse-move).
  Exiting presentation drops you out of fullscreen automatically.
- **Tighter auto-fit** in fullscreen: cell padding drops from 12% to
  6% so each slide fills more of the screen.
- `fullscreen` flag in the store, mirrored from the browser's
  `fullscreenchange` event. `setFullscreen(true/false)` is a no-op if
  the browser denied the request.
- New example **[`heavy_text_demo.py`](examples/heavy_text_demo.py)** —
  five slides packed with long paragraphs to verify the auto-grow
  border works on first paint without any manual resize.

### Compatibility
- File format unchanged.

## [1.0.5] — 2026-05-16

### Fixed
- **Doodle border now tracks the box pixel-for-pixel during resize.**
  Two specific bugs were collapsing into the "border resizes first,
  box follows" symptom:
  1. `DoodleBorder` rebuilt its SVG inside `useEffect`, which runs
     AFTER browser paint. Now uses `useLayoutEffect` — the SVG is
     rebuilt synchronously before paint, so the wavy outline and the
     colored card commit to the new size in the same frame.
  2. The text-cell card was sized with `min-height: drag-target`, so
     when the user dragged smaller, the card stayed taller than the
     drag target until content shrunk. Now the card uses
     `height: size?.height` (exact) when the user has dragged, and
     auto-grows from content otherwise. Drag direction is honoured
     immediately.
- Text cells with an explicit user-set height now have
  `overflow: hidden` so accidental overflow is clipped to the box
  edge rather than spilling past the SVG.

### Compatibility
- File format unchanged. Pure rendering fix.

## [1.0.4] — 2026-05-16

### Fixed
- **Doodle border now matches content size on FIRST render, with zero
  manual drag required.** Previously the measurement effect ran AFTER
  the browser painted, so a cell loaded with long text (e.g. the
  problem-statement slide in `live_demo.py`) showed a 60-px-tall SVG
  outline floating on a 400-px-tall box until the ResizeObserver
  caught up. Switched to `useLayoutEffect` — measurement runs
  synchronously after every commit, before paint — so the SVG always
  matches the rendered card size in the same frame.
- Both `MarkdownNode` and `ExplanationNode` now share a single
  `useMeasuredHeight` hook in [lib/useMeasuredHeight.ts](frontend/src/lib/useMeasuredHeight.ts).
  It combines `useLayoutEffect` (sync, every render) + `ResizeObserver`
  (async, for fonts / images / drags), with a 2 px dead-band against
  feedback loops.
- The hook also fires on every prop change (no deps array on the
  layout-effect) so typing more text immediately grows the SVG too.

### Compatibility
- File format unchanged. Pure rendering fix.

## [1.0.3] — 2026-05-16

### Fixed
- **Doodle border now stays INSIDE the card**, never leaks past the
  edge. Previously the SVG was sized `cardSize + 8` and positioned at
  `inset: -4`, so rough.js's wavy stroke could oscillate past the
  card boundary. Now the SVG fills the card exactly (`inset: 0`) and
  the rectangle is drawn 5 px inside, absorbing the stroke's
  roughness within the SVG bounds.
- All three node types — `CodeCellNode`, `MarkdownNode`,
  `ExplanationNode` — updated to pass exact card dimensions (no
  `+8`). The new `BORDER_INSET = 5` constant in `lib/rough.ts` is the
  single knob that controls how deep the wavy stroke sits inside the
  card.
- Roughness lowered slightly (1.4 → 1.2) and bowing 1.3 → 1.0 so the
  line is tight enough to track the card edge precisely without
  losing its hand-drawn feel.

### Compatibility
- File format unchanged. Pure rendering geometry fix.

## [1.0.2] — 2026-05-16

### Fixed
- **Doodle border now always wraps the full content.** MarkdownNode +
  ExplanationNode both measure their actual rendered size with
  `ResizeObserver` + `getBoundingClientRect()` (which includes
  padding) instead of guessing height from text length, so the SVG
  outline grows to enclose every line you type. Two-pixel deadband
  prevents sub-pixel feedback loops.
- **Long titles wrap inside the header strip** instead of overflowing
  the colored bar. `EditableTitle` adds `break-words` /
  `overflow-wrap: anywhere`. Cell-header containers switched from
  `leading-none` → `leading-tight` to give wrapped lines room.

### Compatibility
- File format unchanged. Pure rendering fix.

## [1.0.1] — 2026-05-16

### Changed
- **Replaced the laser-pointer dot with an Excalidraw-style fading
  pen.** Drag the cursor to draw red ink; strokes fade out in ~1.4 s.
  Quickly circle something and the circle vanishes by the time the
  audience looks. Same drawing code as the highlighter; only the
  color / width / fade-duration differ.
- Presenter button is now **✒️ Pen** with keyboard shortcut **P**
  (was 🔴 Laser, L).
- Highlighter remains unchanged (yellow, thick, ~4 s fade).

### Docs
- [docs/USAGE.md](docs/USAGE.md) updated with the new tool table.
- [CLAUDE.md](CLAUDE.md) rule **5g** locks in the fading-strokes
  approach — no tracking-dot tool to be reintroduced.

## [1.0.0] — 2026-05-16 · **STABLE**

First stable release. Everything in v0.x is baked in; nothing was
removed. The contract going forward:

- The **file format** (currently v2) round-trips byte-stable for every
  field documented in [docs/FILE_FORMAT.md](docs/FILE_FORMAT.md).
- The **HTTP API** (`/upload`, `/export`, `/explain`, `/execute`,
  `/install`, `/autosave`, `/version`, `/reset`, `/health`) is stable.
- The **CLI command** (`./start.sh`) and the **examples** folder are
  stable contracts.

### Changed
- **Author credit reads "Co-AI Developed by Kader Mohideen"** in the
  About modal, the toolbar status line, and the README.
- README status badge: alpha → **stable**; backend pyproject
  Development Status classifier: Alpha → Production/Stable.

### Sanity tape from the release
- ruff (Python 3.9/3.11/3.12) — clean
- **87 / 87** pytest tests pass
- TypeScript strict typecheck — clean
- **40 / 40** vitest tests pass
- vite production build — 393 KB → 125 KB gzip
- All **16 shipped example `.py` files** round-trip exact through
  serialize → parse → equality

### Migration from 0.x
None required. Saved files are identical. Just `git pull` and
`./start.sh`.

## [0.7.3] — 2026-05-16

### Added
- **Global ErrorBoundary** wraps the React tree. Any unexpected
  rendering error now shows a friendly card with the traceback and a
  Reload button instead of a blank page. Auto-saved work survives.
- **Retry button** on install failure: the modal's main button label
  flips from "▶ Install" → "▶ Retry" once the previous attempt failed,
  so the user can edit and retry without a refresh.

### Fixed
- **Cursor on every button is now `pointer`** (and `not-allowed` when
  disabled). Tailwind's preflight resets `button { cursor: inherit }`,
  which made buttons inside the InstallModal pick up the canvas's
  `cursor-grab` while the Hand tool was active. Same fix applied to
  `a`, `label`, `input`, `textarea`. Modal Close + Install + Retry now
  always show the right cursor.
- **Install modal dark-mode contrast**: every text element now uses
  explicit `text-ink dark:text-white` (or `/85`, `/70`) so the body
  copy, the input value, the log preview, and the success/failure
  banners are all readable in dark mode.

### Verified
End-to-end install + plot test against the live backend:
- `pip install numpy` (already present) → 200 ok
- `pip install seaborn` → installed pandas + seaborn (9.9 MB wheel)
- A numpy + matplotlib + seaborn cell → status `ok`, PNG image
  (24 KB) + stdout in one response. The image renders inline in the
  output panel; `ResizeObserver` then shifts the next cell down.

### Compatibility
- **File format unchanged.** Pure UI / robustness release.

## [0.7.2] — 2026-05-16

### Fixed
- **Install modal now actually works.** Lifted state into the zustand
  store and moved the modal render up to `App.tsx`. Previously the
  modal was rendered inside the `Toolbar`'s `pointer-events: none`
  wrapper — its descendants inherited that and silently swallowed all
  clicks, so the package input was un-typeable and the Close button
  un-clickable. Now the modal is a top-level singleton, fully
  interactive, dismissable via Close / Esc / backdrop.
- **Highlighter strokes vanish when you exit presentation.** The
  PresenterOverlay clears its strokes + in-flight stroke on
  `presenting → false`. Re-entering presentation starts on a clean
  board.

### Changed
- **Presentation no longer locks panning.** Two-finger trackpad scroll
  and hand-tool drag work mid-talk so the presenter can browse around.
  Zoom is still locked (no pinch / scroll-zoom / double-click zoom)
  to protect the auto-fit slide. Arrow keys still auto-focus + fit
  the next/prev cell.
- **About modal redesigned.** Headline reads "Developed by Kader
  Mohideen". A big yellow project-URL card sits right below with a
  wiggling 👉 hand pointing at it — perfect to point at during a
  recording. All text uses explicit `text-ink` / `dark:text-white`
  classes so every word is readable in dark mode (previous version
  had near-invisible sub-text in dark).

### Compatibility
- **File format unchanged** — still v2. Pure UI fixes; saved `.py`
  files round-trip byte-identical from v0.4 onward.

### Tests
- 2 new vitest cases for the `installOpen` store flag.
- Total: **87 backend + 40 frontend = 127 green tests.**

## [0.7.1] — 2026-05-16

### Fixed
- **Install modal is now always dismissable.** Close (✕) button and
  Esc key work even while `pip install` is in flight. The Close button
  changes label to "Hide (install continues)" during a long install,
  matching what actually happens.
- **No more page-refresh after install.** Successful installs now
  silently call `importlib.invalidate_caches()` in every active kernel
  session, so packages added to `site-packages` are visible on the
  next `import` without a kernel restart.
- **Presenter bar + modals are always clickable.** Lowered the
  PresenterOverlay z-index from 9998 → 25, below the bar (30) and
  every modal (50+). Highlighter mode no longer eats clicks on the
  Prev / Next buttons or the install/about/callout/text dialogs.
- **Highlighter toggles off reliably.** The 🖍 button is no longer
  shadowed by the overlay it activates — single click on or off.

### Changed
- **Custom doodle cursor removed.** It interfered with text editing
  caret and looked off across OSes. The OS default cursor is now used
  everywhere. The pen-style cursor remains, but ONLY while the
  highlighter tool is active.

### Added
- **Matplotlib (and any image-output library) renders inline by
  default.** Kernels start with `%matplotlib inline` +
  `InlineBackend.figure_format = 'png'`. `plt.show()` produces a PNG
  in the cell's output panel; ResizeObserver shifts the next cell down
  to accommodate the image. Verified with a synthetic sine plot
  end-to-end (22 KB PNG).

### Compatibility
- **File format unchanged** — still v2. Behaviour-only release; saved
  `.py` files round-trip byte-identical in any version from v0.4 on.

## [0.7.0] — 2026-05-16

### Added
- **Hand-drawn marker cursor** across the whole canvas. Defined as a CSS
  custom property (`--doodle-cursor`) — yellow pencil with a pink eraser.
  Switches to a glowing laser-style cursor during presentation, and to
  a crosshair when the highlighter tool is active.
- **Laser pointer presenter tool** (🔴 button on the presenter bar,
  shortcut **L**). Red glowing dot follows the mouse without
  intercepting clicks — you can still navigate normally.
- **Highlighter presenter tool** (🖍 button, shortcut **H**). Drag to
  draw fading yellow highlighter strokes anywhere on the canvas; each
  stroke fades to nothing over ~4 seconds.
- New `presenterTool` state in the store (`"none" | "laser" |
  "highlighter"`) + `setPresenterTool` action. Auto-resets to `"none"`
  when leaving presentation.
- New `PresenterOverlay` component — single SVG layer drawn on top of
  the canvas with `pointer-events` switched per tool so the laser
  passes clicks through while the highlighter captures them.

### Changed
- **No internal scrollbars on cells.** The output panel and markdown
  text body no longer cap their height — they auto-grow with content,
  ResizeObserver measures the new size, and the next cell shifts down.
- **Popovers hide their scrollbar** via a new `.scrollbar-none`
  utility, while keeping the ability to scroll if a tiny viewport
  forces it.
- Markdown cell tracks its own measured content height so the doodle
  border always wraps tightly, no matter how much text is in the box.

### Compatibility
- **File format unchanged** — still v2. All v0.7 features are pure UI:
  cursor, overlay, in-session size tracking. Files saved here open
  byte-identical in any version from v0.4 onward.

### Documentation
- [docs/USAGE.md](docs/USAGE.md) gains a "Presenter tools" subsection
  documenting Laser / Highlighter and their L / H shortcuts.
- [CLAUDE.md](CLAUDE.md) updated with rules 5e (no internal
  scrollbars), 5f (doodle cursor), 5g (presenter overlay tools).

### Tests
- 3 new vitest cases for `presenterTool` default, transitions, and
  auto-reset on presentation exit.
- Total: **87 backend + 38 frontend = 125 green tests.**

## [0.6.0] — 2026-05-16

### Added
- **Three-tool toolbar** (top-left) in Figma convention:
  - **➤ Cursor (V)** — default. Click selects, double-click edits.
    No drag. Trackpad still pans / pinches.
  - **✋ Hand (H)** — drag the canvas to pan; cells locked.
  - **✥ Move (M)** — drag to reposition cells; canvas pan is wheel-only.
- **Double-click anywhere on a cell opens its editor.**
  - Double-click a **code cell** → callout editor.
  - Double-click a **text cell** → text editor.
  - Double-click a **callout bubble** → callout editor for the source.
  - Double-click a cell **title strip** → inline rename.
- **Esc closes any open popover** (in addition to its own Close button).

### Changed
- **Editor popovers are now a singleton in the store.** `openEditor`
  lives in zustand; `App.tsx` mounts exactly one CalloutEditor /
  TextEditor at a time. Buttons, double-clicks, and keyboard shortcuts
  all dispatch the same store action — fixes the "Edit button not
  working" bug from v0.5.1, which was caused by stale per-cell local
  state when the popover was re-mounted.
- **Click vs double-click is reliable again.** Removed the v0.5
  Figma-style "drag empty pans / drag cell moves" auto-mode that ate
  some click events. Three explicit tools make every click predictable.

### Compatibility
- **File format unchanged** — still v2 (`# %% [...]` + `# @explain:` /
  `# @callout` / `# @image:` directives). Files written by any v0.4+
  release open identically in v0.6.0, and v0.6.0 files open in older
  versions without loss.

### Documentation
- [docs/USAGE.md](docs/USAGE.md) now documents the three-tool model
  and the double-click affordances.
- [CLAUDE.md](CLAUDE.md) updated with rules 5b / 5c / 5d locking in
  the new behaviour.

### Tests
- 3 new vitest cases for `interactionMode` default + transitions and
  the `openEditor` singleton.
- Total: **87 backend + 35 frontend = 122 green tests.**

## [0.5.1] — 2026-05-16

### Changed
- **Compact icon-only buttons** in every cell header — `▶`, `✎`, `📝`
  no longer carry text labels. Each is a 32×32 square; tooltips still
  describe what they do on hover.
- **Removed the kind chip** (`EXPR`, `TEXT`, `FUNCTION`, …) from cell
  headers. Color + title carry the meaning; the extra label was clutter.
- **EditableTitle hides when empty.** No more "title — double-click to
  edit" placeholder polluting every cell. An empty title strip is just
  empty space — still double-clickable to start a title.
- **About modal** now shows the project's GitHub URL in a prominent
  yellow card at the top, and a separate "Project on GitHub" link in
  the link list.

### Added
- **Per-cell resize handle** (bottom-right corner) on code AND text
  cells. Drag to set width/height; **Shift-drag** locks the height;
  **double-click** the handle to reset to auto. Dimensions are stored
  in-session only (not in the .py file — file format unchanged).
- New `cellSize` store map + `setCellSize` action with 3 vitest cases.

### Compatibility
- **File format unchanged** — v0.5.1 reads and writes exactly the same
  `# %% [...]` / `# @explain:` / `# @callout` / `# @image:` directives
  as v0.4 / v0.5.0. Files saved here open identically in any older or
  newer release.

## [0.5.0] — 2026-05-16

### Added
- **Inline title editing.** Double-click the title strip on any cell
  (code or text) to rename it in place. Enter commits, Esc cancels.
  Works without opening the full editor.
- **📐 Auto-Space [Presentation]** toolbar button. Computes one slide-
  height of vertical space per cell so each one fills the viewport
  during a talk. Tall cells get rounded up to the next slide-slot.
- **🔗 Together** button (replaces Auto-Space once active) brings the
  cells back to the default close-packed layout for editing.
- **docs/AUTHORING.md** — friendly hand-authoring guide for writing
  DoodleCode `.py` files in any editor. Linked from the README.

### Changed
- Cell layout in DoodleCanvas now honours `cellPositionOverrides` when
  present, falling back to the auto-computed stack otherwise.

### Internals
- New `EditableTitle` component used by both `CodeCellNode` and
  `MarkdownNode`. Stops the click bubbling so node-click navigation
  doesn't fire while you're editing.
- Store gains `cellPositionOverrides`, `autoSpaceForPresentation`, and
  `rollbackLayout`. Three new vitest cases cover them.

## [0.4.0] — 2026-05-16

### Added
- **Presentation text boxes.** New **＋ Text** toolbar button creates an
  editable text/slide cell with title, body markdown, optional inline
  image, and its own colored card. Sits on the canvas alongside code
  cells and supports side callouts the same way.
- **In-place editing for markdown cells.** Every text cell now has a
  **📝 Edit** button (text + image + title + color) and a **✎ Callout**
  button (right-side bubble), both on the cell's header.
- New **TextEditor** popover — drag by the yellow title bar, viewport-
  clamped, attaches an image as a data URL inside the same `.py` file.
- **＋ Code** toolbar button (renamed from `＋ Cell`) for explicit
  code-cell creation.
- File format extended: `# %% [markdown]` cells can carry
  `kind=`/`color=`/`title=` on the header and `# @image:` /
  `# @explain:` / `# @callout` directives — round-trip exact.

### Changed
- `addCell` accepts a `kind` parameter and focuses the newly added cell.
- Markdown cells now render an optional inline image above the body.

### Fixed
- Title text containing spaces in markdown headers is correctly
  preserved through serialize → parse (tests cover this).

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
