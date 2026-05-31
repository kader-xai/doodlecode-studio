# Changelog

## [Unreleased]

### Added (iter 203) — `doodle.table()` data→markdown-table helper
- **The `doodle` kernel helper can now emit a markdown table.**
  `doodle.table(data, headers=…)` turns a mapping (two columns), a list of
  dicts (columns from keys), or a list of rows into `| a | b |` markdown
  source to `print()` and paste into a **Text** cell — closing the loop
  with the iter-196 table renderer. Pipes are escaped and newlines
  flattened so a cell value can't break the table. 5 pytest cases
  (18 helper tests). README helper snippet updated.

### Docs (iter 202) — document the text-cell markdown dialect
- **The README now has a "Markdown in text cells" reference table** —
  headings, bullet / task / ordered lists, blockquotes, rules, inline
  emphasis + code, fenced code, links, and tables — matching exactly what
  the renderer supports, plus an explicit "not supported (by design)"
  note. The Cell-types table's stale inline syntax hint links here
  instead. Docs in lockstep with the renderer (CLAUDE rule 25).

### Added (iter 201) — markdown task lists in text cells
- **`- [ ]` / `- [x]` render read-only checkboxes.** Task-list items in a
  text cell show a checkbox (capital `[X]` accepted); done items strike
  through. Plain bullets and tasks mix freely in one list. Useful for
  tutorial checklists and "what you'll learn" sections. 3 vitest cases
  (225 frontend tests).

## [2.8.0] — 2026-05-31

Authoring + file-format hardening release. Text cells gain **markdown
tables** and **fenced code blocks**; the `doodle` kernel helper can now
emit **stacked + grouped bar** syntax from computed data. Two silent
save-format corruption bugs are fixed — a literal `\n` in a
reveal/note/callout, and a `# %%` line inside a code body — with a
`FILE_FORMAT_VERSION` 3 → 4 bump whose decoder is version-gated, so every
older notebook still parses exactly as before.

### Fixed (iter 199) — code body containing `# %%` no longer splits the cell
- **A code cell whose body contains a `# %%` line round-trips as one
  cell.** The serializer wrote the body verbatim, so any line that looked
  like a cell marker — a pasted Jupyter/VSCode `# %%`, or a deck
  *explaining this very format* — was re-read as a new cell boundary,
  silently splitting the cell and truncating its source. v4 now escapes
  such body lines (`# %%` → `# %\%`) on write and peels one level on
  read; the escape stacks so already-escaped lines stay exact. Old
  (v1–v3) files are untouched. 2 new pytest cases (39 backend tests).

### Fixed (iter 198) — literal `\n` in reveals/notes/callouts no longer corrupts (format v4)
- **A literal backslash-n in a reveal step, speaker note, or callout now
  round-trips byte-for-byte.** The single-line directive encoder escaped
  real newlines as `\n` but didn't escape backslashes, so a reveal of
  `print("a\nb")` (code — backslash-n is everywhere) decoded back to a
  real newline and split the string. The encoder now escapes backslashes
  first and the decoder un-escapes in a single left-to-right pass.
- **`FILE_FORMAT_VERSION` 3 → 4.** New files stamp version 4 and use the
  safe escaping; v1–v3 files keep decoding with the legacy scheme, so
  every previously-saved notebook still parses exactly as before
  (backward-compat verified by test). 4 new pytest cases (37 backend).

### Added (iter 197) — fenced code blocks in text cells
- **Text cells render ```` ``` ```` fenced code blocks.** The content is
  literal — markdown inside a fence is shown verbatim, not parsed — so
  example syntax displays exactly as typed in a monospace doodle-bordered
  block. An optional language tag after the opening fence is kept as a
  `data-lang` attribute; an unterminated fence runs to the end of the
  cell. Complements inline `` `code` `` for code-explanation narratives.
  5 vitest cases (222 frontend tests).

### Added (iter 196) — markdown tables in text cells
- **Text cells now render GitHub-style tables.** A header row of
  `| a | b |` followed by a separator `| --- | :-: |` renders a
  hand-drawn doodle table; colons in the separator set per-column
  alignment (`:--` left, `:-:` center, `--:` right). Short body rows are
  padded to the header's column count, and inline **bold** / `code` /
  links render inside cells. A lone pipe line without a separator stays a
  paragraph. Zero-dependency; 5 vitest cases (217 frontend tests).

### Added (iter 195) — `doodle.stack()` / `doodle.group()` kernel helpers
- **The `doodle` data→chart-syntax helper now emits stacked and grouped
  bars.** `doodle.stack(rows, series=…, title=…)` and `doodle.group(…)`
  turn a `{category: [values]}` table plus a series legend into the exact
  `stack:` / `group:` mini-syntax the renderer parses — closing the gap
  where the renderer and editor supported these charts but a code cell
  couldn't generate them from computed data. Dependency-free and pure;
  3 new pytest cases (34 backend tests). README helper snippet updated.

## [2.7.0] — 2026-05-31

Data-visualization release. The doodle chart suite is now exhaustive —
flow, single / stacked / grouped bar, line, area, pie, and scatter, with
axis titles, dashed reference lines, and live data from a code cell — each
implemented, documented in the README, seeded by an editor preset, shown
in the bundled `examples/data_viz_demo.py` deck, and locked by tests.
Also bundles the accessibility, code-splitting, responsiveness, and
showcase (video timestamps / playback flags, markdown links + ordered
lists) work since 2.6.0.

### Added (iter 193) — grouped (side-by-side) bar chart
- **Diagram cells render grouped bars for comparing series within
  categories.** `group: Title` sets a heading, `series: 2023, 2024` names
  the clustered columns (shared with the stacked-bar legend), and each
  `group NA: 8, 11` row becomes a category whose values are drawn as
  side-by-side columns scaled to the tallest value. A **▦ Grouped** editor
  preset seeds a working sample; the README example + kind table document
  it. Completes the bar family (single / stacked / grouped). 6 vitest
  cases; 212 frontend tests green.

### Added (iter 192) — stacked bar in the data-viz demo deck
- **`examples/data_viz_demo.py` now showcases the stacked bar chart.** A
  new "Stacked — part-to-whole over time" slide (Engineering hours by
  quarter, split Features/Bugs/Docs) sits between scatter and the live
  code cell, with a speaker note and the reveal chain rewired through it.
  The intro and recap copy now say *seven* charts; the backend coverage
  test asserts 9 cells / 6 diagrams and the `stack`/`series:` directives,
  so the demo can't silently drift from the renderer.

### Docs (iter 191) — complete the chart-syntax reference
- **The README "Doodle charts" section now documents every kind.** The
  worked example and kind table gained the **Area**, **Stacked**, and
  **Reference-line (`hline:`)** rows that had shipped without docs, and
  the `doodle` Python-helper snippet now shows `doodle.area(...)`. Brings
  the docs back in lockstep with the renderer (CLAUDE rule 25).

### Added (iter 190) — doodle stacked bar chart
- **Diagram cells render stacked bars for part-to-whole across
  categories.** `stack: Title` sets a heading, `series: Eng, Sales, Ops`
  names the segments (legend), and each `stack Q1: 5, 3, 2` row is a
  horizontal bar split into series-coloured segments with the row total
  at the end. Bar length scales to the widest row so proportions read
  true. Parsed before the bar rule (never mistaken for a `Label: number`
  bar); the Diagram editor gains a **▥ Stacked** preset. 207 frontend
  tests.

### Docs (iter 189) — demo deck exercises the full chart suite
- **`examples/data_viz_demo.py` now covers every v2.6+ feature.** Added
  an Area-chart slide and a target `hline:` on the line chart, plus a
  recap slide that uses markdown **links** and an **ordered list**. The
  backend fixture test was tightened to assert the new coverage (8 cells,
  5 diagrams, area + hline present) and an exact round-trip, so the
  example can't drift from the renderer. 31 backend tests.

### Fixed (iter 188) — new cells always spawn in a tidy column
- **New cells no longer scatter across the canvas.** Spawning used to
  inherit the x of whatever cell was "bottom-most in reading order" and
  fall back to a diagonal step on collision, so once you dragged cells
  around, each new cell appeared at a different x — a staircase. Now
  every new cell spawns in a single fixed left column (`x = 120`),
  placed one gap below the lowest cell's bottom edge so it can never
  overlap. The canvas still auto-pans to it, and you remain free to drag
  it anywhere afterward. 203 frontend tests.

### Added (iter 187) — chart reference / threshold lines
- **Line, area, and scatter charts can draw a dashed reference line.**
  `hline: 0.5` (or `hline Target: 0.5` with a label) marks a goal /
  threshold across the plot — the classic "did we beat the baseline?"
  annotation for data storytelling. Lines outside the chart's y-range
  are skipped; the marker is drawn in marker-pink with a right-aligned
  label. (Dashed here is a data annotation, not the cell-connector
  structure the no-dashed rule covers.) The Line editor preset now seeds
  an `hline Target:` so it's discoverable. 203 frontend tests.

### Added (iter 186) — markdown ordered lists
- **Text cells render numbered lists** (`1. step`, also `1)` style) —
  the natural companion to bullet lists for step-by-step explanations.
  The list honors its first number via the `<ol start>` attribute, so a
  list that begins at `3.` continues 3, 4, 5. Paragraph grouping now
  stops at an ordered-list line so a `1.` after prose starts a fresh
  list. Still zero-dependency. 199 frontend tests.

### Added (iter 185) — markdown links
- **Text cells now render `[label](url)` links** — useful for citing
  references in an explanation. Links open in a new tab with
  `rel="noopener noreferrer"`. The renderer only accepts safe schemes
  (`http`, `https`, `mailto`, and relative/anchor links); a
  `javascript:` href is left as literal text, so user markdown can't
  smuggle in an XSS payload. The zero-dependency renderer stays tiny —
  links were the one piece of CommonMark users kept asking for.
  197 frontend tests (incl. the refused-`javascript:` case).

### Added (iter 184) — video playback flags (loop / autoplay / mute)
- **Media cells carry playback flags from the pasted URL into the
  embed.** Add `&autoplay=1`, `&mute=1`, `&loop=1`, or `&controls=0` to a
  YouTube/Vimeo link and the player honors them — so a "loop this demo
  silently" showcase slide just works. YouTube's `loop=1` automatically
  names the single-video playlist it requires; Vimeo's `mute` maps to
  its `muted` param. Combines cleanly with the iter-183 start time. Param
  order is deterministic (start first), keeping `videoEmbed` fully
  unit-tested. 194 frontend tests.

### Added (iter 183) — video start-time timestamps
- **Media cells honor a start time in YouTube / Vimeo links**, so a
  "jump to the demo" showcase slide opens the clip at the right moment.
  Pasting `…watch?v=ID&t=1m30s` (or `?t=90`, `?t=90s`, `?start=90`,
  `youtu.be/ID?t=…`, a shorts link, or Vimeo's `#t=90s`) now carries the
  offset into the embed (`…/embed/ID?start=90`, Vimeo `…#t=90s`). The
  embed logic moved into a pure, unit-tested `lib/videoEmbed.ts`
  (`parseTimestamp` accepts `90`, `90s`, `1m30s`, `1h2m3s`, and `1:02:03`
  clock form). 191 frontend tests.

### Responsiveness (iter 182) — toolbar wraps on narrow viewports
- **The toolbar no longer runs off-screen on small windows.** The main
  button pill was a single non-wrapping row of ~20 controls, so a narrow
  viewport (split screen, tablet, projector preview) clipped the
  right-hand buttons. The pill now `flex-wrap`s its buttons and the
  header wraps the Tools / shortcuts / theme group below the main pill
  when space runs out — every control stays reachable at any width. No
  behavior change on wide screens. 177 frontend tests.

### Performance (iter 181) — code-split Mermaid + KaTeX
- **The main bundle shrank from ~1.29 MB to ~456 KB** (gzip 353 → 141
  KB). Mermaid (~581 KB) and KaTeX (~258 KB + 29 KB CSS) were imported
  eagerly even though only the Mermaid/Math diagram kinds need them;
  they're now `import()`-ed lazily and split into their own chunks that
  load on first use. Both loaders memoize the module promise (fetched at
  most once), the math render moved from a sync `useMemo` to an async
  effect, and a `src/vite-env.d.ts` declares the dynamic CSS import.
  Faster first paint for everyone who isn't rendering a Mermaid/Math
  diagram. 177 frontend tests; production build is warning-clean.

### CI / open-source (iter 180) — v2 is now gated by CI
- **Continuous integration finally tests the v2 app.** The shared
  `.github/workflows/ci.yml` previously only ran the legacy v1
  `backend/` + `frontend/` suites, so every v2 PR — where all current
  development happens — merged with **zero** automated checks. Added
  `v2-backend` (pytest on Python 3.11 + 3.12) and `v2-frontend`
  (`tsc -b --noEmit` + vitest + `vite build` on Node 20) jobs. Also
  pointed contributors at the active app: CONTRIBUTING now has an
  "Active app lives in `v2/`" section with the v2 dev + local
  CI-equivalent commands.

### Accessibility (iter 179) — color-contrast pass + guardrail
- **The doodle palette is proven to clear WCAG AAA, and locked in.** A
  new pure `lib/contrast.ts` (WCAG 2.1 relative-luminance + contrast
  ratio + `meetsAA`) backs a guardrail test asserting every text/
  background pair stays readable. Measured ratios all exceed the 7:1
  AAA bar: ink on the callout yellow **12.7:1**, chart labels on the
  light card **16.1:1**, dark-theme labels on the dark diagram card
  **14.8:1**, and ink on the lowest-contrast toolbar pastel (sky)
  **9.5:1**. No visual change was needed — the test now fails loudly if
  a future palette tweak drops a pair below AA. 177 frontend tests.

### Accessibility (iter 178) — reduced-motion audit
- **`prefers-reduced-motion` now silences every decorative animation.**
  Previously only the slide entrance respected it; the audit extended
  the media query to also stop the ambient background drift (which uses
  an inline `animation`, so a `.doodle-drift-shape` class + `!important`
  was needed) and the flowing dashed cell→cell connectors. Functional
  presenter ink strokes and one-shot UI transitions are intentionally
  left alone. Result: with "reduce motion" set, the canvas is fully
  still except for direct user interaction. 168 frontend tests.

### Accessibility (iter 177) — accessible names for icon controls
- **Icon-only controls now announce a real name.** A button's emoji
  *content* normally wins over its `title` in the accessible-name
  computation, so screen readers were reading the emoji name (e.g.
  "fountain pen") instead of the action. The four presenter ink tools,
  the presenter fullscreen toggle, the toolbar keyboard-shortcuts
  button, and the theme toggle now carry an explicit `aria-label`; the
  ink tools, fullscreen, and theme toggles also expose `aria-pressed`
  so their on/off state is conveyed. Toolbar action buttons already
  carry text labels, so they were left as-is. 168 frontend tests.

### Accessibility (iter 176) — modal focus management
- **Modals now trap and restore keyboard focus.** Opening the callout
  editor, reveal-steps editor, speaker-note editor, install modal, or
  shortcuts overlay focuses the first field (respecting an existing
  autoFocus), keeps Tab / Shift+Tab cycling **within** the dialog, and
  on close returns focus to whatever triggered it — so keyboard and
  screen-reader users are never dumped at the top of the page. Reusable
  `useFocusTrap` hook with a pure, unit-tested `nextTrapTarget` wrap
  helper. The Cmd/Ctrl+K palette keeps its own Tab-navigates-results
  behavior. 168 frontend tests.

### Accessibility (iter 175) — modal dialog semantics
- **Every modal now announces itself to assistive tech.** The callout
  editor, reveal-steps editor, speaker-note editor, install modal,
  keyboard-shortcuts overlay, and the Cmd/Ctrl+K cell palette gained
  `role="dialog"` + `aria-modal="true"` + a descriptive `aria-label`,
  and the palette's filter box has an `aria-label`. First pass of an
  accessibility sweep toward open-source-readiness; no visual change.

### Added (iter 174) — live data-driven doodle charts
- **A Doodle diagram can render a code cell's output live.** Put a
  `live: <codeCellId>` line in the diagram source and it's replaced with
  that code cell's current stdout before the chart compiles — so a code
  cell that `print()`s `doodle.bar(...)` drives the chart with no paste
  step, re-rendering each time the cell runs. Static chart lines may sit
  alongside `live:` blocks; an unrun / unknown cell just blanks out
  (renders the empty-diagram hint). Pure `lib/liveChart.ts`
  (`resolveLiveDoodleSource` / `stdoutOf`), DiagramCell subscribes to
  `runtimes`, and a **🔌 Live** editor preset makes it discoverable.
  Closes the code→chart loop (slice B). 161 frontend tests.

### Added (iter 173) — `doodle` helper: data → chart syntax in code cells
- **Every code cell's kernel now exposes a `doodle` namespace** (no
  import) that turns Python data into doodle-chart source:
  `print(doodle.bar({"Python": 8, "Rust": 4}, title="LOC"))`. It covers
  `bar` · `line` · `area` · `pie` · `scatter` · `flow`, accepts a dict
  or list of pairs, keeps ints int / trims floats, drops non-positive
  pie slices, and emits exactly the tokens the diagram parser keys on —
  so you compute in Python and paste the printed lines into a 🖍 Doodle
  diagram. First slice of code-driven visuals. Pure, dependency-free
  module (`app/doodle_helper.py`) injected at kernel startup;
  end-to-end verified through the runner subprocess. 31 backend tests.

### Added (iter 172) — doodle area chart
- **Diagram cells render filled area charts.** `area Active: 2, 5, 9`
  draws a line filled to the baseline (28%-opacity wash + solid ink
  edge), great for showing a quantity growing over x. Multiple `area`
  rows stack back-to-front with a square-swatch legend; it shares the
  `xlabel:` / `ylabel:` axis titles with the line and scatter charts,
  is parsed before the bar rule (never mistaken for a bar), and the
  Diagram editor gains an **▰ Area** preset button. 155 frontend tests.

### Docs (iter 171) — README refresh for the data-viz suite
- **README now documents the full v2.6.0 data-viz suite.** New "Doodle
  charts" section with the line-syntax for flow / bar / line / pie /
  scatter and a kind→trigger table; the intro and Diagram cell row
  mention every chart kind; the keyboard table gains **N** (speaker
  note) and **🎬 / Shift+R** (reveal step); the optional-directives
  list documents `# @reveal:` and `# @note:`; and the new
  `examples/data_viz_demo.py` is linked as the worked example.

### Added (iter 170) — data-viz demo deck + regression fixture
- **New `examples/data_viz_demo.py`** — a 7-slide deck that exercises
  the whole v2.6.0 suite end-to-end: a bar chart, a line chart with
  axis titles, a pie/donut, a scatter plot with axis titles, a code
  cell with two reveal steps, and a speaker note on every diagram. It
  doubles as a **regression fixture**: a backend test parses it, asserts
  feature coverage (all four chart kinds, axis titles, notes, reveals),
  and checks an exact round-trip of the format-stable fields — so the
  example can't silently rot. 21 backend tests.

## [2.6.0] — Visual-intuition batch 🎨

_Presenter speaker notes, a full doodle data-viz suite (scatter plots,
chart presets, axis titles), and a gentle slide entrance animation._

### Added (iter 169) — slide entrance animation
- **Each slide gently rises into focus during presentation.** When you
  advance to a cell (→ / ← / Home / End / arrow nav), its content fades
  up with a soft rise + settle (`translateY(12px)→0`, `scale .985→1`,
  420 ms ease-out) so the eye lands on the new slide. The animation
  targets the cell's *inner* content, never the ReactFlow node wrapper
  whose transform carries pan/zoom — so it never fights the viewport and
  is **not** a zoom (CLAUDE rule 6 preserved). It re-triggers each time
  focus lands on a cell, and is fully disabled under
  `prefers-reduced-motion`. 151 frontend tests.

### Added (iter 168) — chart axis titles
- **Line and scatter charts can now name their axes.** Add
  `xlabel: Epoch` / `ylabel: Loss` to a doodle diagram and the x-title
  renders centered under the plot, the y-title rotated -90° along the
  left edge — both in the hand-drawn font. Axis-label directives are
  parsed before the bar `Label: Number` rule so they're never mistaken
  for bars, are escaped like every other user string, and no-op when
  absent (charts without them are unchanged). The Line and Scatter
  editor presets now seed `xlabel:`/`ylabel:` so the feature is
  discoverable. 151 frontend tests.

### Added (iter 167) — diagram chart presets (no syntax to memorize)
- **The Diagram editor now has one-click chart-sample buttons.** When
  you edit a 🖍 Doodle diagram, an "Insert:" bar appears above the
  textarea with **→ Flow · ▭ Bar · 📈 Line · ◔ Pie · ⠿ Scatter**
  buttons. Each appends a working snippet (non-destructively — doodle
  charts stack) you can then tweak, so the mini-syntax is fully
  discoverable without docs. Buttons use `preventDefault` on mousedown
  so the textarea keeps focus and the insert lands cleanly; the bar is
  shown for the doodle kind only. 146 frontend tests.

### Added (iter 166) — doodle scatter plot
- **Diagram cells now render scatter plots for x/y intuition.**
  `scatter: Title` sets a heading; `point: x, y` adds a dot. The result
  is a hand-drawn x/y plane with faint quartile gridlines on both axes,
  L-shaped ink axes, min/max tick labels on each axis, and
  semi-transparent ink-outlined dots. Points need exactly two finite
  numbers (a `point:` with one value is ignored), and scatter is parsed
  before the bar `Label: Number` rule so dots are never mistaken for
  bars. Independent of bars / lines / pies — all can coexist in one
  source. 146 frontend tests.

### Added (iter 165) — presenter speaker notes
- **Per-cell speaker notes you can read while presenting, never shown
  on the slide.** Press **N** with a cell selected (or use the 📝 entry
  in the shortcuts overlay) to open a singleton `NoteEditor` modal;
  the text is saved on the cell as `note`. During presentation a
  `PresenterNotes` HUD pins bottom-left (z-40, `pointer-events:none` so
  it never blocks the PresenterBar or canvas) and shows the focused
  cell's note — hidden when the cell has none. Notes round-trip through
  the `.py` as `# @note:` (newlines escaped, emitted only when present
  so clean files stay clean); old files default to no note. The store
  trims whitespace-only notes back to `undefined`. 142 frontend tests,
  20 backend tests.

### Added (iter 164) — doodle pie / donut chart
- **Diagram cells now render pie/donut charts.** `pie: Title` sets a
  heading; `pie <Label>: <value>` adds a slice. The result is a
  hand-drawn donut (ink-outlined wedges, center hole) with a
  percentage legend. Non-positive slices are ignored; pies are kept
  independent of bars and line series in one source. Verified live:
  a 4-slice "Language share" donut (45/30/15/10%) renders cleanly with
  zero console errors. 139 frontend tests.

### Added (iter 163) — presentation progress bar
- **A thin doodle progress bar pins to the top during presentation**,
  filling to (currentSlide / total) with faint per-slide notches so the
  audience always knows how far through the deck you are. Marker-pink
  fill, animated width, `pointer-events:none` so it never blocks the
  PresenterBar. Pure `progressFraction(index, total)` helper in
  `lib/present.ts` (clamped, last slide = 100%, empty deck = 0).
  Verified live: 4-slide deck on slide 2 → 50% fill, zero console
  errors. 134 frontend tests.

### Fixed (iter 162) — slides frame to the upper third
- **Presentation now anchors each slide's TOP at ~33% from the top**
  of the viewport instead of centering the cell's midpoint at 50%.
  Dropping a cell and pressing Present (or navigating with → / ←) used
  to leave it sitting low / below center; now every slide reads
  top-to-bottom from the upper third, and tall cells no longer run off
  the bottom. The math lives in a pure, unit-tested
  `lib/present.ts:slideCenterY(cellTopY, viewportH, zoom, topFraction)`
  (round-trip + zoom + height-independence covered; 131 frontend
  tests). Note: this is a hard coordinate transform — the headless
  preview throttles ReactFlow's animated `setCenter`, so it's verified
  by the math/unit tests rather than a pixel screenshot.

### Fixed (iter 161) — output panel no longer grows forever
- **The code-cell output panel is now height-capped and scrollable.**
  A runaway `print` loop used to stretch the cell off the canvas with
  no way to scroll ("scrolling indefinitely"). Output now caps at
  360px and becomes its own `overflow-auto nowheel` scroll region;
  when it overflows, **↑ Top / ↓ End** jump buttons appear in the
  header. Each output item is char-capped (`PER_ITEM_CHAR_CAP` =
  100,000) with a "… N more characters truncated" note so a
  multi-MB string can't freeze the browser. Updated CLAUDE rule 18
  to record the output-panel exception. Verified live with a
  5,000-line / 260k-char print: panel capped at 360px, scrollHeight
  32k, truncation note + jump buttons shown, ↓ End scrolls to bottom,
  zero console errors. `clampText` unit-tested (127 frontend tests).

### Fixed (iter 159) — new cells always appear in view
- **The canvas now pans to a newly created cell.** Combined with the
  iter 151 column layout, every **+ Code / Text / Media / Browser /
  Draw / Diagram** add now places the cell below the bottom of the
  column AND scrolls it into view, so you always see the box appear
  in a predictable spot — fixing the "boxes appear here and there"
  complaint at the moment of creation. Drag-dropped cells (which land
  at the cursor) are exempt so the viewport doesn't jump. Verified in
  the browser: consecutive adds each pan into view, selected and
  chained.

### Added (iter 158) — Reveal Steps shortcut
- **Shift+R reveals the next code step** — works during presentation
  (acts on the focused cell) and on the canvas (selected cell).
  No-op unless the target is a code cell with reveal steps left.
  Documented in the Shortcuts overlay (🎬 / Shift+R).

### Added (iter 155-157) — Reveal Steps (UI + file format)
- **Reveal Steps editor** (🎬 on a code cell) — author an ordered
  list of code fragments ahead of a talk.
- **CodeCell Reveal UI**: ✨ Reveal types the next step in below the
  code with a typewriter animation; ↺ resets to the base; the editor
  is read-only during/after a reveal (only step 0 is editable).
- **File round-trip**: reveal steps persist as one `# @reveal:`
  directive per step (newlines escaped, order preserved). Old files
  without `# @reveal:` load with an empty list. Backend round-trip
  tests added (18 backend total).

### Added (iter 154) — Reveal Steps (store layer)
- **Code cells can now hold ordered "reveal" steps.** `cell.reveals`
  is a list of code fragments authored ahead of a talk. The pristine
  `source` is shown at step 0; each reveal appends the next fragment
  below (build-up), so the program grows function-by-function. The
  currently-revealed count is the ephemeral `revealStep` (not
  persisted, resets on load). `runCell` executes the effective
  (revealed) code. New store actions: `setReveals`, `revealNext`,
  `resetReveals`, `openRevealEditor`. Pure `effectiveSource` /
  `revealCount` helpers in `lib/reveal.ts`. UI + file round-trip
  land in following iterations.

### Changed (iter 153)
- **DoodleBorder is now a two-pass sketch.** Pass A is the main
  wobbly stroke; pass B is a thinner inset ghost at 45% opacity with
  a different noise seed. The two together read as a confident
  pencil-drawn box instead of the previous single CAD-like wobble.
  Refactored `buildPath` to take optional `insetX/insetY/seedOffset`
  so future passes can share the same path generator.

### Changed (iter 152)
- **Auto-link new cells to the previous bottom cell.** Together with
  the iter 151 column flow, pressing **New** now extends a visible
  symmetric link from the previous cell down to the new one. Skipped
  for `media` cells (drag-drop image dumps shouldn't all chain) and
  when the caller passes an explicit `links` array.

### Changed (iter 151)
- **Auto-arrange: new cells now stack in a vertical column** below
  the bottom-most existing cell instead of stepping diagonally from
  (80, 80). Empty canvas → (120, 100); subsequent adds → same x,
  `bottom.y + bottom.h + 80` y. Resolves the long-standing
  "boxes appear here and there" complaint — every new cell lands
  exactly where the user expects the flow to continue.

### Tests (iter 150)
- Coverage for `alignSelected("distV")` — equal-gap vertical
  distribution across 3+ cells.
- Test-setup shim for Node 22's native `localStorage` (it requires
  `--localstorage-file` and otherwise collides with jsdom's stub).
  Without the shim, the entire store.test.ts file fails to import.

### Tests (iter 149)
- Coverage for `alignSelected("bottom")` and `("middleY")`. Closes
  the vertical-axis side of the align matrix to match iter 148's
  horizontal additions. The full 7-mode matrix is now exercised.
  96 frontend tests.

### Tests (iter 148)
- Coverage for `alignSelected("right")` (aligns right edges) and
  `alignSelected("centerX")` (centers on bbox midline). Closes the
  last gaps in the align/distribute test matrix. 94 frontend tests.

### Tests (iter 147)
- Lock `nextCell` / `prevCell` reading-order traversal + end-of-list
  clamping. From `null` focus, `nextCell` picks the first cell; both
  walkers CLAMP at the ends rather than wrapping. 92 frontend tests.

### Tests (iter 146)
- Lock `rollbackLayout` no-op when never spaced — cell positions
  stay untouched if `originalPositions` is null. Prevents a future
  refactor that loses the early-return guard from clobbering the
  user's layout the first time they hit **S**. 91 frontend tests.

### Tests (iter 145)
- Lock `spaceForPresentation` snapshot stability: re-pressing **S**
  to re-spread cells must NOT overwrite `originalPositions` with
  the already-spread coordinates — otherwise rollback would
  no-op and the user's hand-placed layout would be lost. 90
  frontend tests.

### Tests (iter 144)
- Lock `setCallouts` filter rules: whitespace-only text entries are
  dropped, image-only entries (no text) are kept, fully-empty
  entries are dropped. The CalloutEditor's "remove" affordance
  relies on this. 89 frontend tests.

### Tests (iter 143)
- Lock two `setExplain` invariants: whitespace-only text clears
  the callouts (same as `null`), and replacing `callouts[0]` does
  not drop `callouts[1+]`. 88 frontend tests.

### Tests (iter 142)
- Lock `setAllCollapsed` object-identity preservation: already-
  matching cells keep their reference so React memo / shallow
  compare doesn't repaint rows whose `collapsed` flag didn't
  actually change. 86 frontend tests.

### Tests (iter 141)
- Lock `addWhiteboardCell` + `addDiagramCell` seed shape: whiteboard
  source is parseable JSON with `strokes: []` and a `bg` field;
  diagram defaults to `diagram_kind: "doodle"`. Drawing and render
  code rely on both invariants. 85 frontend tests.

### Tests (iter 140)
- Lock `addCell` partial-override behavior: a partial with `kind`
  overrides the default `"code"`, x/y still come from
  `spawnPosition`, and the new id mirrors into both `selectedId`
  and `selectedIds` per rule 21e. 84 frontend tests.

### Tests (iter 139)
- Lock `addBrowserCell` URL normalization: bare hosts get an
  `https://` prefix, explicit `http://` is preserved, whitespace
  returns `null`, and the cell's title defaults to the host. 83
  frontend tests.

### Tests (iter 138)
- Lock `renderMarkdown` italic vs bold disambiguation: `*foo*`
  renders as `<em>`, `**foo**` renders as `<strong>` and does NOT
  also produce a stray `<em>`. 80 frontend tests.

### Tests (iter 137)
- Lock `cellsInOrder` y-jitter tolerance: cells whose `y` differ by
  less than the 40 px row bucket sort by `x`, not by `y`. Prevents
  a future refactor from accidentally tightening the bucket and
  reshuffling the reading order when cells aren't perfectly aligned.

### Tests (iter 136)
- Lock `addCell` non-collision: when the diagonal of default spawn
  slots is fully occupied, `spawnPosition` must step past them so
  the new cell never lands on top of an existing one.

## v2.5.5 — Selection-sync hardening

5 iterations on top of v2.5.4 (130-134). Round of guards against
dangling ids and self-references in the link / selection actions,
locking rule 21e (`selectedId` must reference a real cell) at the
store boundary. Test suite went 88 → 93 (77 frontend + 16 backend).

### Fixed
- **`linkCells` refuses dangling endpoints** (iter 130). Stale ids
  from a queued post-delete action no longer write one-sided links
  that `ConnectionsLayer` cannot resolve.
- **`unlinkCells` refuses self-references** (iter 132). Mirrors the
  iter 130 guard.
- **`panToCell` refuses non-existent ids** (iter 133). Stale ids
  (e.g. a deleted cell surfaced by `runAllCells`) no longer set
  `selectedId` to a dangling string or waste a `panToTick` bump.

### Tests
- `alignSelected("distH")` no-op with only 2 cells locked (iter 131).
- `firstLine` preserves URL fragments + leading `*` for non-markdown
  and non-code kinds (iter 134).

## v2.5.4 — Esc / Tab fixes + edge-case tests

7 iterations on top of v2.5.3 (121-127). Test suite went 85 → 88.

### Fixed (iter 121)
- **Shift+Tab from a null selection now jumps to the last cell**
  (Tab still goes to the first). Both used to pick `cells[0]`,
  which felt wrong for the "back" direction.

### Fixed (iter 123)
- **Esc closes the Cmd+K palette as a fallback** when its input has
  lost focus. The palette's own input.onKeyDown handles Esc when
  focused; this is the belt-and-braces case if focus drifted.

### Fixed (iter 125)
- **Esc-from-palette no longer also clears the cell selection** —
  React's synthetic-event stopPropagation didn't stop the underlying
  native event from reaching the window-level App handler. Switched
  to `nativeEvent.stopImmediatePropagation()` so the App cascade
  doesn't fall through to `setSelected(null)` when the palette
  already handled the Esc.

### Tests (iter 126-127)
- +2 vitest cases for `runAllCells` on empty / markdown-only
  notebooks (lock the no-code branches surfaced by iter 116's
  toolbar guard).
- +1 vitest case for `unlinkCells` on a never-linked pair (no-op).
- Suite: 16 backend + 72 frontend = 88 total.

## v2.5.3 — auto-focus + Run All UX + empty-notebook polish

9 iterations on top of v2.5.2 (111-119). Mostly small UX wins; no
new file-format fields.

### Fixed (iter 111-112)
- **First cell is auto-focused after `File → New` / `File → Open` /
  `.py` drag-drop.** Keyboard shortcuts (Cmd+K, Cmd+/, Shift+Enter,
  Cmd+Enter) used to silently no-op until the user clicked
  something. Now the seed cell on a fresh notebook, and the first
  cell in reading order on a loaded one, become the primary
  selection immediately.

### Changed (iter 114-115)
- **▶▶ Run All selects and pans to the failed cell on error.** The
  alert that fired on a halted Run All still pointed to the failed
  title, but the user had to scroll to find it. Now the failed cell
  becomes the primary selection (red iter-40 border lights up) and
  the canvas centers on it.

### Changed (iter 116)
- **Toolbar buttons that act on cells visibly disable when no cells
  apply.** ▶▶ Run All, 🧹 Clear, and ▾/▸ All grey out with
  cursor-not-allowed and explanatory tooltips when the notebook is
  empty (or has no code cells). Avoids "clicked but nothing
  happened" confusion.

### Refactored (iter 118)
- The "next selection after delete" math was duplicated between
  `deleteCell` (iter 108) and `deleteCells` (iter 109). Pulled into
  a shared `nextSelectionAfterDelete` helper so the heuristic only
  lives in one place.

## v2.5.2 — post-delete focus + palette polish

10 iterations on top of v2.5.1 (101-109). Test suite went 80 → 85.

### Fixed
- **`🧹 Clear` now also resets the `[n]` execution counter.** Used to
  wipe the per-cell badges but leave `execCounter` ticking, so the
  next run jumped to `[N+1]` even though no prior outputs were on
  screen.
- **Delete keeps focus nearby.** Both single-cell and group delete
  used to leave the selection empty. Now they pick the next cell in
  reading order (or the previous if deleting from the end), so the
  user lands somewhere useful.

### Added
- **Palette pre-highlights the current selection on open** so users
  don't have to ↑↓ to find their own cell.
- **Palette auto-scrolls the highlighted row into view** — PgDn /
  End / Tab in long match lists no longer push focus off-screen.

### Refactored
- Toolbar's `↻ Kernel` button no longer inlines its own setState; the
  client-side cleanup moved to `store.resetKernelState()` so future
  callers (palette commands, shortcuts) can share it.

### Changed
- `EditableTitle` gains an optional `tooltip` prop; the toolbar
  notebook chip now hints "Double-click to rename notebook" instead
  of the cell-only "Drag to move · Double-click to rename" default.
- `v2/README.md` title dropped the stale `v2.0` pin — version is
  surfaced in the CHANGELOG, the in-app `?` overlay, and
  `__init__.py`. Saves having to remember to edit the header on
  every release.

## v2.5.1 — collapse polish + safety + version chip

9 iterations on top of v2.5.0 (91-99). Mostly cleanup; no new
features that change the file format. Test suite stable at 79.

### Added
- **Cmd/Ctrl+Enter** runs the selected code cell — alias for
  Shift+Enter. Both Jupyter idioms accepted (we don't auto-advance,
  so they behave identically).
- **App version footer in help overlay** ("DoodleCode Studio v2.5.1"
  bottom-right) so users can tell what they're on without opening
  the source. Sourced from the new `APP_VERSION` constant — kept in
  lockstep with backend `__version__` and `package.json` per the
  expanded CLAUDE rule 29.

### Changed
- **Collapsed Diagram title strip** — the kind selector becomes a
  small static chip (🖍 Doodle / 🧭 Mermaid / 📐 Math) and the Edit
  button hides while collapsed.
- **Collapsed Markdown title strip** — Edit button hides too.
- **Collapsed Whiteboard title strip** — hides the entire tool block
  (pen / highlighter / eraser / 5 colors / 3 backgrounds / undo /
  clear). Cramming 20+ buttons into 44 px looked terrible.

### Fixed
- **Drag-dropped `.py` files capped at 10 MB** to prevent a stalled
  FileReader on broken inputs.
- **Toolbar notebook chip uses text cursor**, not the move cursor
  inherited from EditableTitle's drag-handle styling.

## v2.5.0 — file-handling polish + palette niceties

8 iterations on top of v2.4.0 (81-88). Test suite stable at 79
(16 backend + 63 frontend).

### Added (iter 81-88)
- **Drag-drop `.py` file** onto the canvas opens it as a notebook
  (after a confirm prompt). Filename becomes the new notebook name.
  Image drag-drop still works for `image/*` files (iter 32).
- **Save As** — Cmd/Ctrl+Shift+S now prompts via
  `showSaveFilePicker` to pick a new file location, then binds the
  returned handle for subsequent silent Cmd+S writes. Falls back to
  a plain download on browsers without the File System Access API.
  After save, the notebook name syncs from the picked filename.
- **Cmd/Ctrl+\\** toggles dark / light theme without leaving the
  keyboard.
- **Inline rename notebook from toolbar** — double-click the
  notebook name to enter an inline edit. Enter / blur commits, Esc
  cancels.
- **Palette: Tab / Shift+Tab** acts like ↑ / ↓ (VS Code idiom). Pairs
  with the existing Home / End / PgUp / PgDn nav.

### Docs
- `v2/README.md` gains a "Drag & drop" section covering the two
  drop affordances (image → Media cell at drop point; `.py` → open).

## v2.4.0 — selection-sync correctness + palette polish

10 iterations (71-79) on top of v2.3.0. Heavy on test coverage (+17
cases). Net: 16 backend + 63 frontend = 79 tests.

### Added
- **Cmd/Ctrl+/ toggles collapse on the selected cell.** Pairs with
  Cmd+K palette workflow: jump → collapse → next, no mouse needed.
- **▾ All / ▸ All toolbar toggle.** Single button that runs the
  collapse-all / expand-all bulk action — makes the iter 57 shortcut
  discoverable.
- **Palette stats footer.** `N cells · K collapsed · L links` shown
  whenever the palette is open (link count dedupes symmetric pairs).
- **Palette navigation keys.** Home / End / PageUp / PageDown for
  fast scrolling in big notebooks.

### Fixed
- **`setSelectedIds` now keeps `selectedId` in sync** with the new
  set. Previously `setSelectedIds([])` left `selectedId` pointing at
  a deselected cell, so the toolbar's Delete / Callout / size-preset
  surfaces stayed bound to it. Captured as CLAUDE.md rule 21e.
- **5 other selection writers were broken the same way** —
  `addCell`, `duplicateCell`, `focusCell`, `nextCell`, `prevCell` +
  the presenting auto-focus path. All now write `selectedIds` in
  lockstep.
- **Duplicate semantics rule** captured as CLAUDE.md 21f (drop
  outgoing links, deep-clone callouts — fix from iter 60).

### Refactored
- `firstLine` and `hostOf` extracted to `src/lib/cellPreview.ts` so
  they're testable without rendering components.

### Tests
- +17 vitest cases: `firstLine` (md/code/blank/truncate), `hostOf`
  (www / fallback / port / blank), `setSelectedIds` sync (3 branches),
  rule 21e enforcement (addCell / duplicate / focusCell).

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
