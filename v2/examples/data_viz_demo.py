# doodlecode format-version: 3
# notebook: Data-viz suite — every doodle chart

# %% kind=markdown id=c0 x=120.0 y=80.0 w=640.0
# @title: Welcome
# @note: Open with the one-sentence promise: every chart kind, hand-drawn, in one file.
# @link_to: c1

# The DoodleCode data-viz suite 📊

One `.py` file, five hand-drawn chart kinds, speaker notes, and code you
build live. Everything below round-trips through this single file.

- **Bar** — compare categories
- **Line** — trends over time (with axis titles)
- **Pie / donut** — part-to-whole
- **Scatter** — x/y relationships
- **Reveal steps** — type code in during the talk

Press **F5 / Shift+P** to present, **→** to advance. Press **N** on any
cell to read its speaker note (only you see it, bottom-left).

# %% kind=diagram id=c1 x=120.0 y=460.0 w=600.0 h=340.0
# @title: Bar — categories
# @diagram_kind: doodle
# @note: Bars are the safe default. Lead with the tallest and name the gap.
# @link_to: c2

chart: Lines of code by language
Python: 8
TypeScript: 10
Rust: 4
Go: 6

# %% kind=diagram id=c2 x=120.0 y=860.0 w=640.0 h=400.0
# @title: Line — trend with axis titles
# @diagram_kind: doodle
# @note: Point at the crossover. The eye reads slope before it reads numbers.
# @link_to: c3

chart: Training vs validation loss
xlabel: Epoch
ylabel: Loss
line Train: 0.92, 0.61, 0.43, 0.31, 0.24, 0.2
line Val: 0.95, 0.7, 0.55, 0.46, 0.42, 0.4

# %% kind=diagram id=c3 x=120.0 y=1320.0 w=620.0 h=360.0
# @title: Pie — part to whole
# @diagram_kind: doodle
# @note: Keep slices under five. Percentages live in the legend already.
# @link_to: c4

pie: Where the runtime goes
pie Parsing: 15
pie Rendering: 45
pie Layout: 25
pie Idle: 15

# %% kind=diagram id=c4 x=120.0 y=1740.0 w=620.0 h=380.0
# @title: Scatter — x/y intuition
# @diagram_kind: doodle
# @note: Gesture along the diagonal — the upward drift IS the correlation.
# @link_to: c5

scatter: Cell size vs render time
xlabel: Cells
ylabel: ms
point: 1, 2
point: 2, 3
point: 3, 5
point: 4, 6
point: 5, 8
point: 6, 9

# %% kind=code id=c5 x=120.0 y=2180.0 w=600.0
# @title: Build it live (press ✨ Reveal)
# @note: Run the base first. Reveal the helper, then the loop. Narrate each line.
# @explain: Run shows the base. Press ✨ Reveal (or Shift+R) to add each step.
# @reveal: def share(part, total):\n    return round(100 * part / total, 1)
# @reveal: for name, n in [("Rendering", 45), ("Layout", 25)]:\n    print(f"{name}: {share(n, 100)}%")
# @link_to: c6

# We'll turn the pie numbers into percentages, live.
print("Base ready — press ✨ Reveal")

# %% kind=markdown id=c6 x=120.0 y=2560.0 w=640.0
# @title: Recap

## Five charts, one file 🎉

- **Bar** for categories, **Line** for trends (named axes),
  **Pie** for parts, **Scatter** for relationships.
- **Speaker notes** (press **N**) kept the script off the slide.
- **Reveal steps** built the code up one line at a time.

> Drag this `.py` back into DoodleCode any time — the whole deck,
> notes and all, comes back exactly.
