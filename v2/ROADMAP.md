# DoodleCode Studio v2 — Roadmap to a one-stop visual presentation tool

The north star: **one app to explain code, build visual intuition with
charts/graphs, embed live demos + video, and present it all as a
doodle-styled visual treat.** Iterations are small, tested, and shipped
one at a time (see CHANGELOG for the running log).

## Pillars

1. **Code explanation** — code cells run real Python; reveal-steps build
   programs up live; inline matplotlib output.
2. **Visual intuition** — doodle charts (bar ✓, **line ✓ iter 160**,
   pie ✓ iter 164, **scatter ✓ iter 166**), flowcharts ✓, mermaid ✓,
   math (KaTeX) ✓.
3. **Live demo + video** — browser cells embed live pages ✓; media cells
   play video/GIF ✓; (▢) one-click "record this slide → GIF/MP4".
4. **Presentation** — slide flow ✓, slide counter ✓, presenter ink ✓,
   reveal steps ✓, progress bar ✓, speaker notes ✓; (▢) auto-advance.
5. **Doodle visual treat** — two-pass sketch borders ✓, ambient themes ✓,
   sketchy connectors ✓; (▢) hand-drawn chart axes, (▢) entrance anims.

## Iteration plan (next up)

- **160 — Doodle line charts** *(in progress)*: `line Loss: 0.9, 0.6, …`
  renders a hand-drawn multi-series line chart. Trends/loss-curves.
- **161 — Presentation progress bar** ✓ (shipped as iter 163): thin
  doodle bar across the top showing deck progress + per-slide notches.
- **162 — Pie / donut doodle chart** ✓ (shipped as iter 164):
  `pie A: 30` slices → hand-drawn donut + % legend.
- **163 — Speaker notes** ✓ (shipped as iter 165): `# @note:` per cell,
  shown only to the presenter (bottom-left HUD) during a talk. **N**
  opens the editor; round-trips in the .py.
- **164 — Scatter chart** ✓ (shipped as iter 166): `point: x, y` →
  hand-drawn x/y plane with gridlines + axis ticks. For x/y intuition.
- **165 — Diagram cell chart presets** ✓ (shipped as iter 167): an
  "Insert:" bar of Flow / Bar / Line / Pie / Scatter sample buttons in
  the Diagram editor so users don't memorize syntax.
- **166 — Chart axis labels + gridlines** ✓ (shipped as iter 168):
  gridlines + ticks landed with line/scatter; `xlabel:`/`ylabel:` add
  hand-drawn axis titles to both.
- **167 — Entrance animation for revealed slides** ✓ (shipped as iter
  169): focused slide rises + settles (translateY + fade), inner content
  only so it never fights pan/zoom; respects reduced-motion.
- **168 — Release** ✓ (shipped as v2.6.0): bundled the visual-intuition
  batch (speaker notes, scatter, chart presets, axis titles, slide
  entrance animation). Lockstep bump 2.5.5 → 2.6.0, tagged.

### Next batch (post-2.6.0) — ideas, prioritized
- **169 — Visual-intuition demo deck** ✓ (shipped as iter 170):
  `examples/data_viz_demo.py` exercises every chart kind
  (bar/line/pie/scatter + axis labels), speaker notes, and reveal steps;
  a backend test asserts coverage + round-trip so it stays honest.
- **170 — README/docs refresh** ✓ (shipped as iter 171): "Doodle
  charts" syntax section + kind table, N / Shift+R keys, `@reveal` /
  `@note` directives, linked the data-viz demo.
- **171 — Area chart** ✓ (shipped as iter 172): `area Label: …` fills a
  line to the baseline; stacks back-to-front; shares axis titles.
- **172 — Chart data from a code cell** — live data-driven visuals.
  - *Slice A ✓ (iter 173):* kernel `doodle` helper turns Python data
    into chart syntax to `print()` and paste.
  - *Slice B ✓ (iter 174):* a Doodle diagram renders a linked code
    cell's stdout live via a `live: <id>` directive — no paste step.

### Accessibility & polish (toward open-source-readiness)
- **173 — Modal dialog semantics** ✓ (iter 175): `role="dialog"` +
  `aria-modal` + `aria-label` on all six overlays; labelled palette
  input.
- **174 — Focus management for modals** ✓ (iter 176): `useFocusTrap`
  autofocuses, traps Tab, restores focus to the trigger on close.
- **175 — Icon-button labels sweep** ✓ (iter 177): presenter ink tools
  + fullscreen, toolbar help button, theme toggle got `aria-label` +
  `aria-pressed`; toolbar action buttons already had text labels.
  *(Follow-up: cell-header collapse chevrons across the six cell types.)*
- **176 — Reduced-motion audit** ✓ (iter 178): ambient drift, flowing
  connectors, and slide entrance all stop under `prefers-reduced-motion`
  (presenter ink + UI transitions kept). No effects-burst exists in v2.
- **177 — Color-contrast pass** ✓ (iter 179): `lib/contrast.ts` (WCAG
  2.1) + guardrail test; every text/bg pair measured 9.5:1–16.1:1, all
  clearing AAA. No visual change needed; the test locks it in.

The accessibility & polish batch (173–177) is complete.

### Open-source readiness
- **178 — CI covers v2** ✓ (iter 180): added `v2-backend` (pytest) +
  `v2-frontend` (tsc/vitest/build) jobs; CONTRIBUTING points to `v2/`.
- **179 — Bundle code-split** ✓ (iter 181): Mermaid + KaTeX lazy-loaded;
  main chunk 1.29 MB → 456 KB; build warning-clean.
- **180 — Small-viewport responsiveness** ✓ (iter 182): toolbar pill +
  header `flex-wrap` so controls stack instead of overflowing.

### Showcase features
- **181 — Video start-time timestamps** ✓ (iter 183): media cells honor
  `?t=`/`#t=` start offsets in YouTube/Vimeo links.
- **182 — Loop / autoplay / mute toggles** ✓ (iter 184): playback flags
  (`autoplay`/`mute`/`loop`/`controls`) propagate from the URL to the
  embed for YouTube + Vimeo.
- **183 — Animated GIF export** of a single slide (capture the canvas
  region to a shareable loop).

- **184 — Markdown links** ✓ (iter 185): `[text](url)` in text cells,
  new-tab + safe-scheme guard.
- **185 — Markdown ordered lists** ✓ (iter 186): `1. step` numbered
  lists with `<ol start>` offset.
- **186 — Chart reference lines** ✓ (iter 187): `hline: 0.5` dashed
  threshold on line/area/scatter for "beat the baseline" storytelling.
- **187 — Stacked bar chart** ✓ (iter 190): `stack Cat: a, b` + `series:`
  legend for part-to-whole across categories.
- **188 — Chart reference docs** ✓ (iter 191): README example + kind table
  gained Area / Stacked / `hline:` rows; `doodle.area(...)` in the helper
  snippet — docs back in lockstep with the renderer.
- **189 — Stacked bar in the demo deck** ✓ (iter 192): a stacked slide in
  `examples/data_viz_demo.py` (Engineering hours by quarter); coverage
  test now asserts 9 cells / 6 diagrams and the `stack`/`series:` lines.
- **190 — Grouped (side-by-side) bar chart** ✓ (iter 193): `group Cat: a, b`
  clusters one column per series, shares the `series:` legend; ▦ Grouped
  preset + README. Bar family complete (single / stacked / grouped).
- **191 — Release v2.7.0** ✓ (iter 194): bundled the data-viz batch
  (stacked + grouped bar, demo-deck coverage, complete chart-syntax docs)
  on top of the a11y / code-split / showcase work since 2.6.0. Lockstep
  bump 2.6.0 → 2.7.0, tagged. CI-equivalent green (tsc, 212 FE tests,
  build, 31 BE tests).

- **192 — `doodle.stack()` / `doodle.group()` helpers** ✓ (iter 195):
  the kernel data→syntax helper can now emit stacked + grouped bar source
  from a `{category: [values]}` table, matching the renderer. 34 backend
  tests.
- **193 — Markdown tables** ✓ (iter 196): text cells render GitHub-style
  `| a | b |` tables with per-column alignment from the `:--:` separator;
  inline formatting inside cells. 217 frontend tests.
- **194 — Fenced code blocks** ✓ (iter 197): ```` ``` ````-delimited
  literal code blocks in text cells, optional language tag, no inline
  parsing inside. Complements inline `code`. 222 frontend tests.
- **195 — Round-trip fix: literal `\n`** ✓ (iter 198): directive encoder
  now escapes backslashes, so a reveal/note/callout containing a literal
  backslash-n survives save→load byte-for-byte. FILE_FORMAT_VERSION 3→4,
  version-gated decoder keeps every old file parsing. 37 backend tests.
- **196 — Round-trip fix: `# %%` in a body** ✓ (iter 199): a code body
  containing a Jupyter-style `# %%` marker (or a deck explaining this
  format) no longer splits into two cells — v4 escapes/peels marker-like
  body lines reversibly. 39 backend tests.
- **197 — Release v2.8.0** ✓ (iter 200): bundled markdown tables + fenced
  code, `doodle.stack/group` helpers, and the two file-format round-trip
  fixes (FILE_FORMAT_VERSION 3→4). Lockstep bump 2.7.0 → 2.8.0, tagged.
  CI-equivalent green (tsc, 222 FE tests, build, 39 BE tests).
- **198 — Markdown task lists** ✓ (iter 201): `- [ ]` / `- [x]` render
  read-only checkboxes (done items strike through); plain + task bullets
  mix in one list. For tutorial checklists. 225 frontend tests.
- **199 — Markdown reference docs** ✓ (iter 202): README gains a
  "Markdown in text cells" table covering every supported construct +
  an explicit not-supported note; docs back in lockstep with renderer.
- **200 — `doodle.table()` helper** ✓ (iter 203): kernel helper emits
  markdown-table source from a mapping / list-of-dicts / rows, pipes
  escaped — pairs with the iter-196 table renderer. 18 helper tests.
- **201 — Chart aria data summaries** ✓ (iter 204): every chart's
  `aria-label` now spells out its values (e.g. "Bar chart: Scores —
  Python 8, Rust 4") so screen readers convey the data, not just the
  chart type. 230 frontend tests.
- **202 — Flow aria + table header scope** ✓ (iter 205): flowcharts list
  their edges in the aria-label; markdown table `<th>` gain `scope="col"`
  for screen-reader header association. 232 frontend tests.

Other candidate areas: richer diagram presets, an in-app onboarding
tour, animated-GIF slide export (needs a GIF-encoder dep — deferred).

This file is updated as items land or priorities shift.
