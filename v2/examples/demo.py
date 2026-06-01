# doodlecode format-version: 4
# notebook: DoodleCode Studio v2 — tour

# %% kind=markdown id=t0 x=80.0 y=80.0 w=720.0 h=240.0
# @title: Welcome
# @explain: Every block in this tour is a real `# %%` cell in one .py file. Drag, edit, save. The file goes with you.
# @link_to: c1

# Welcome to DoodleCode Studio v2 🎨

This tour walks through every cell type, stacked top-to-bottom in one
column and connected in a line. Double-click any cell to edit, or hit
**F5** / **Shift+P** to present the whole deck as slides.

- Code that runs in Python
- Rich markdown
- Images, video, YouTube
- Live browser pages
- A whiteboard you can draw on
- Doodle-style flowcharts + bar charts
- Math equations in LaTeX
- Multi-callout bubbles with images

# %% kind=code id=c1 x=80.0 y=392.0 w=720.0 h=260.0
# @title: Hello, Python
# @explain: Press R while presenting (or click ▶) to run this cell live.
# @link_to: t1

print("Hello from DoodleCode v2 🎉")
import math
print(f"pi ≈ {math.pi:.5f}")
print(f"2^10 = {2 ** 10}")

# %% kind=markdown id=t1 x=80.0 y=724.0 w=720.0 h=260.0
# @title: Markdown shortcuts
# @explain: # ## ### for headings · **bold** · *italic* · `code` · - or * for bullets · > for quotes · --- for a rule.
# @link_to: m1

## A heading

A paragraph with **bold**, *italic*, and some `inline code`.

- bullet one
- bullet two
- bullet three

> Single-line blockquote works too.

---

# %% kind=media id=m1 x=80.0 y=1056.0 w=720.0 h=360.0
# @title: Image
# @explain: Paste any image URL. The cell fills its frame; drag the corner to resize.
# @link_to: m2

https://placehold.co/600x400/png?text=Drop+an+image+URL

# %% kind=media id=m2 x=80.0 y=1488.0 w=720.0 h=360.0
# @title: Video
# @explain: YouTube and Vimeo embeds work too — paste any watch link.
# @link_to: b1

https://www.youtube.com/watch?v=dQw4w9WgXcQ

# %% kind=browser id=b1 x=80.0 y=1920.0 w=720.0 h=480.0
# @title: Live browser cell
# @explain: Click "Click to interact" (or press B) to use the page. The 🛡 toggle proxies through the server to bypass X-Frame blocks.
# @link_to: w1

https://example.com

# %% kind=whiteboard id=w1 x=80.0 y=2472.0 w=720.0 h=480.0
# @title: Whiteboard
# @explain: ✒ pen · 🖍 highlighter · 🧽 stroke-eraser · 5 colors · 3 backgrounds.
# @link_to: d1

{"bg":"light","strokes":[]}

# %% kind=diagram id=d1 x=80.0 y=3024.0 w=720.0 h=520.0
# @title: Doodle flow + bar chart
# @diagram_kind: doodle
# @explain: One source = a flowchart AND a bar chart. `A --> B` lines for arrows, `Label: number` lines for bars, `chart: title` for the chart heading.
# @link_to: d2

flowchart
Idea --> Sketch
Sketch --> Try it
Try it --> Ship 🚀

chart: Demo energy
Idea: 6
Sketch: 8
Try it: 9
Ship 🚀: 10

# %% kind=diagram id=d2 x=80.0 y=3616.0 w=720.0 h=360.0
# @title: Mermaid sequence
# @diagram_kind: mermaid
# @explain: All of Mermaid's flow / sequence / state diagrams work — pick "Mermaid" from the cell's dropdown.
# @link_to: d3

sequenceDiagram
  participant U as User
  participant A as App
  U->>A: F5
  A-->>U: Present mode
  U->>A: → → →
  A-->>U: Slides!

# %% kind=diagram id=d3 x=80.0 y=4048.0 w=720.0 h=300.0
# @title: Math
# @diagram_kind: math
# @explain: LaTeX rendered with KaTeX. Pick "Math" from the cell's dropdown.
# @link_to: an1

\int_{-\infty}^{\infty} e^{-x^2}\, dx = \sqrt{\pi}

# %% kind=animation id=an1 x=80.0 y=4420.0 w=720.0 h=240.0
# @title: Animation cell
# @transition: draw-on
# @explain: One frame per line. In presentation, → / Space reveals the next frame in place before the slide advances. The 🎞 chip cycles the transition.
# @link_to: cb1

Input goes in →
Something happens inside
← Output comes out

# %% kind=markdown id=cb1 x=80.0 y=4732.0 w=720.0 h=300.0
# @title: Callouts
# @explain: Callouts can hold text AND images. Paste a screenshot into a bubble.
# @callout
# @explain: Multiple bubbles per cell stack vertically. Drag the parent — they all follow.
# @callout
# @explain: Save the .py and your callouts (+ embedded images as data URLs) round-trip exactly.
# @link_to: end

# Callouts

Click any cell, then **💬 Callouts** in the toolbar (or press **C**) to open
the editor. Bubbles sit to the right of the cell, aligned with its top.

# %% kind=markdown id=end x=80.0 y=5434.0 w=720.0 h=200.0
# @title: That's the tour
# @explain: Use ⤵ Tidy to re-stack any deck into one clean line. Space (S) spreads cells one-per-slide; F5 presents.

## You've seen everything

Hit **⤵ Tidy** to re-stack any deck into one connected column. Press **S**
to spread cells one-per-slide, then **F5** to present. During the talk:
**P / H / X** draw ink, **E** wipes it, **R** runs a code cell.
