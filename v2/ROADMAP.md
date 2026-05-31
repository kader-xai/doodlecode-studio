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
- **167 — Entrance animation for revealed slides** (gentle fade/slide).
- **168 — Release**: bundle the visual-intuition batch.

This file is updated as items land or priorities shift.
