# doodlecode format-version: 3
# notebook: DoodleCode Studio v2 — tour

# %% kind=markdown id=t0 x=80.0 y=80.0 w=720.0 h=240.0
# @title: Welcome
# @explain: Every block in this tour is a real `# %%` cell in one .py file. Drag, edit, save. The file goes with you.

# Welcome to DoodleCode Studio v2 🎨

This tour walks through every cell type. Try **double-clicking** any cell to
edit, or hit **F5** / **Shift+P** to present the whole deck as slides.

- Code that runs in Python
- Rich markdown
- Images, video, YouTube
- Live browser pages
- A whiteboard you can draw on
- Doodle-style flowcharts + bar charts
- Math equations in LaTeX
- Multi-callout bubbles with images

# %% kind=code id=c1 x=80.0 y=360.0 w=580.0 h=260.0
# @title: Hello, Python
# @explain: Press R while presenting (or click ▶) to run this cell live.

print("Hello from DoodleCode v2 🎉")
import math
print(f"pi ≈ {math.pi:.5f}")
print(f"2^10 = {2 ** 10}")

# %% kind=markdown id=t1 x=720.0 y=360.0 w=560.0 h=260.0
# @title: Markdown shortcuts
# @explain: # ## ### for headings · **bold** · *italic* · `code` · - or * for bullets · > for quotes · --- for a rule.

## A heading

A paragraph with **bold**, *italic*, and some `inline code`.

- bullet one
- bullet two
- bullet three

> Single-line blockquote works too.

---

# %% kind=media id=m1 x=80.0 y=680.0 w=560.0 h=360.0
# Image cell — paste a URL. The cell fills its frame and you can
# drag the bottom-right corner to resize.

https://placehold.co/600x400/png?text=Drop+an+image+URL

# %% kind=media id=m2 x=720.0 y=680.0 w=560.0 h=360.0
# YouTube embeds work too — paste any youtube.com/watch?v=… link.

https://www.youtube.com/watch?v=dQw4w9WgXcQ

# %% kind=browser id=b1 x=80.0 y=1100.0 w=720.0 h=480.0
# @title: Live browser cell
# @explain: Click "Click to interact" (or press B) to use the page. The 🛡 toggle proxies through the server to bypass X-Frame blocks.

https://example.com

# %% kind=whiteboard id=w1 x=880.0 y=1100.0 w=640.0 h=480.0
# @title: Whiteboard
# @explain: ✒ pen · 🖍 highlighter · 🧽 stroke-eraser · 5 colors · 3 backgrounds.

{"bg":"light","strokes":[]}

# %% kind=diagram id=d1 x=80.0 y=1640.0 w=720.0 h=520.0
# @title: Doodle flow + bar chart
# @diagram_kind: doodle
# @explain: One source = a flowchart AND a bar chart. `A --> B` lines for arrows, `Label: number` lines for bars, `chart: title` for the chart heading.

flowchart
Idea --> Sketch
Sketch --> Try it
Try it --> Ship 🚀

chart: Demo energy
Idea: 6
Sketch: 8
Try it: 9
Ship 🚀: 10

# %% kind=diagram id=d2 x=880.0 y=1640.0 w=560.0 h=360.0
# @title: Mermaid sequence
# @diagram_kind: mermaid
# @explain: All of Mermaid's flow / sequence / state diagrams work — pick "Mermaid" from the cell's dropdown.

sequenceDiagram
  participant U as User
  participant A as App
  U->>A: F5
  A-->>U: Present mode
  U->>A: → → →
  A-->>U: Slides!

# %% kind=diagram id=d3 x=80.0 y=2240.0 w=560.0 h=300.0
# @title: Math
# @diagram_kind: math
# @explain: LaTeX rendered with KaTeX. Pick "Math" from the cell's dropdown.

\int_{-\infty}^{\infty} e^{-x^2}\, dx = \sqrt{\pi}

# %% kind=markdown id=cb1 x=720.0 y=2240.0 w=560.0 h=300.0
# @title: Callouts
# @explain: Callouts can hold text AND images. Paste a screenshot into a bubble.
# @callout
# @explain: Multiple bubbles per cell stack vertically. Drag the parent — they all follow.
# @callout
# @explain: Save the .py and your callouts (+ embedded images as data URLs) round-trip exactly.

# Callouts

Click any cell, then **💬 Callouts** in the toolbar (or press **C**) to open
the editor. You can add many bubbles, reorder them, and drop an image into
any of them.

# %% kind=markdown id=end x=80.0 y=2580.0 w=1200.0 h=200.0
# @title: That's the tour
# @explain: Try Space (S) to lay cells one-per-slide, then F5 to present. P / H / X for pen / highlighter / fixed pen during a talk.

## You've seen everything

Press **S** to spread these cells one-per-slide, then **F5** to present.
During the talk: **P / H / X** draw ink, **E** wipes it, **R** runs a code
cell, **F** fullscreens. Have fun!
