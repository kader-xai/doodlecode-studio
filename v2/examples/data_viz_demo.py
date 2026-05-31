# doodlecode format-version: 3
# notebook: Data-viz suite — every doodle chart

# %% kind=markdown id=c0 x=120.0 y=80.0 w=640.0
# @title: Welcome
# @note: Open with the one-sentence promise: every chart kind, hand-drawn, in one file.
# @link_to: c1

# The DoodleCode data-viz suite 📊

One `.py` file, seven hand-drawn chart kinds, speaker notes, and code you
build live. Everything below round-trips through this single file.

1. **Bar** — compare categories
2. **Line** — trends over time (axis titles + a target line)
3. **Area** — a quantity growing over x
4. **Pie / donut** — part-to-whole
5. **Scatter** — x/y relationships
6. **Stacked bar** — part-to-whole across categories
7. **Reveal steps** — type code in during the talk

Press **F5 / Shift+P** to present, **→** to advance. Press **N** on any
cell to read its speaker note (only you see it, bottom-left).

# %% kind=diagram id=c1 x=120.0 y=480.0 w=600.0 h=340.0
# @title: Bar — categories
# @diagram_kind: doodle
# @note: Bars are the safe default. Lead with the tallest and name the gap.
# @link_to: c2

chart: Lines of code by language
Python: 8
TypeScript: 10
Rust: 4
Go: 6

# %% kind=diagram id=c2 x=120.0 y=880.0 w=640.0 h=400.0
# @title: Line — trend + target line
# @diagram_kind: doodle
# @note: Point at the crossover, then the moment both lines dip under the target.
# @link_to: c3

chart: Training vs validation loss
xlabel: Epoch
ylabel: Loss
hline Target: 0.3
line Train: 0.92, 0.61, 0.43, 0.31, 0.24, 0.2
line Val: 0.95, 0.7, 0.55, 0.46, 0.42, 0.4

# %% kind=diagram id=c3 x=120.0 y=1340.0 w=640.0 h=380.0
# @title: Area — growth over time
# @diagram_kind: doodle
# @note: The filled wash says "accumulation" in a way a bare line can't.
# @link_to: c4

chart: Weekly active users (thousands)
xlabel: Week
ylabel: Users
area Active: 2, 5, 9, 14, 20, 27

# %% kind=diagram id=c4 x=120.0 y=1780.0 w=620.0 h=360.0
# @title: Pie — part to whole
# @diagram_kind: doodle
# @note: Keep slices under five. Percentages live in the legend already.
# @link_to: c5

pie: Where the runtime goes
pie Parsing: 15
pie Rendering: 45
pie Layout: 25
pie Idle: 15

# %% kind=diagram id=c5 x=120.0 y=2200.0 w=620.0 h=380.0
# @title: Scatter — x/y intuition
# @diagram_kind: doodle
# @note: Gesture along the diagonal — the upward drift IS the correlation.
# @link_to: c8

scatter: Cell size vs render time
xlabel: Cells
ylabel: ms
point: 1, 2
point: 2, 3
point: 3, 5
point: 4, 6
point: 5, 8
point: 6, 9

# %% kind=diagram id=c8 x=120.0 y=2640.0 w=640.0 h=380.0
# @title: Stacked — part-to-whole over time
# @diagram_kind: doodle
# @note: Read the legend first, then trace one band across the rows to show it growing.
# @link_to: c6

stack: Engineering hours by quarter
series: Features, Bugs, Docs
stack Q1: 18, 9, 4
stack Q2: 22, 7, 6
stack Q3: 27, 6, 8

# %% kind=code id=c6 x=120.0 y=3100.0 w=600.0
# @title: Build it live (press ✨ Reveal)
# @note: Run the base first. Reveal the helper, then the loop. Narrate each line.
# @explain: Run shows the base. Press ✨ Reveal (or Shift+R) to add each step.
# @reveal: def share(part, total):\n    return round(100 * part / total, 1)
# @reveal: for name, n in [("Rendering", 45), ("Layout", 25)]:\n    print(f"{name}: {share(n, 100)}%")
# @link_to: c7

# We'll turn the pie numbers into percentages, live.
print("Base ready — press ✨ Reveal")

# %% kind=markdown id=c7 x=120.0 y=3560.0 w=640.0
# @title: Recap

## Seven charts, one file 🎉

- **Bar / Line / Area / Pie / Scatter / Stacked** cover every shape of
  question; add `hline:` for a target and `xlabel:` / `ylabel:` for axes.
- **Speaker notes** (press **N**) kept the script off the slide.
- **Reveal steps** built the code up one line at a time.

Next steps:

1. Drop this `.py` back into DoodleCode — the whole deck returns exactly.
2. Wire a chart to live data with `live: <codeCellId>`.
3. Read the [chart syntax in the README](README.md) for every directive.

> One file, fully self-contained — notes, charts, and all.
