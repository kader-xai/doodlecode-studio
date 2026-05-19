# doodlecode format-version: 2
# All-in-one demo — exercises every UI capability shipped in the
# latest stable. Open with 📂 Open → 🎬 Present.


# %% [markdown] color=rose title="What this demo covers"
# # 🧭 What you'll see
#
# - Selection-driven **Edit** & **Delete** in the toolbar
# - Three media-only slides (GIF / video / image — full-bleed, no header)
# - A regular text slide with an inline image you can resize
# - A code cell with **three callouts** — delete any one from the toolbar
# - Live Python (▶ Run still works the same way)
# - Recap


# %% [markdown] color=sky title="How selection works"
# # 🖱 Click → Toolbar shows Edit / Delete
#
# - **Click any cell or callout** → a "Selected: …" row appears in
#   the top toolbar with **✏️ Edit** and **🗑 Delete**.
# - **Click empty canvas** → selection clears, the row hides.
# - Cards no longer carry their own per-card buttons → cleaner look
#   during presentation.


# %% [markdown] color=mint title="GIF (media-only)"
# ![bouncing demo](/demo/bouncing_ball.gif)


# %% [markdown] color=peach title="MP4 video (media-only)"
# ![wave](/demo/wave_visualization.mp4)


# %% [markdown] color=violet title="PNG image (media-only)"
# ![chart](/demo/chart_screenshot.png)


# %% [markdown] color=amber title="Mixed: text + inline image"
# # 🖼 Inline image inside a text card
#
# Regular markdown cells can carry an image **inline** anywhere in
# the body. Drag the bottom-right corner to resize.
#
# ![architecture](/demo/architecture_diagram.png)
#
# Text continues here — the card grows to fit the image.


# %% color=lime title="Three callouts on one code cell"
# @title: 1️⃣ Build a small list
# @explain: A list comprehension squaring 1..5 — the primary callout.
# @callout
# @title: 2️⃣ sum() folds it
# @explain: sum(iterable) is built in — no need for a manual for-loop.
# @callout
# @title: 3️⃣ Try deleting THIS callout
# @explain: Click this bubble → look at the toolbar → 🗑 Delete.
# @explain: Only this one disappears; the other two stay.
# @explain: Same flow works in presentation + fullscreen.
squares = [n * n for n in range(1, 6)]
print("squares:", squares)
print("sum:    ", sum(squares))


# %% color=teal title="Live arithmetic"
# @explain: Same kernel as always — ▶ Run on the card to execute.
# @explain: The output appears below the editor, never inside a callout.
a, b = 23, 4
print("a + b  =", a + b)
print("a * b  =", a * b)
print("a / b  =", a / b)
print("a ** b =", a ** b)


# %% color=sky title="Matplotlib chart"
# @explain: The chart renders below the cell, not in the callout column.
# @explain: ResizeObserver keeps the next slide pushed down so nothing overlaps.
import matplotlib.pyplot as plt
import math

xs = [i / 10 for i in range(0, 63)]
ys1 = [math.sin(x) for x in xs]
ys2 = [math.cos(x) for x in xs]

plt.figure(figsize=(7, 3.5))
plt.plot(xs, ys1, label="sin", lw=2)
plt.plot(xs, ys2, label="cos", lw=2, linestyle="--")
plt.title("sin / cos")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()


# %% [markdown] color=rose title="Recap"
# # 🎉 Everything in one deck
#
# 1. Clean cards — no per-card buttons.
# 2. Toolbar shows ✏️ Edit / 🗑 Delete for the **selected** item.
# 3. Media-only slides (GIF, video, image) render frameless.
# 4. **＋ Image** and **＋ Video** toolbar buttons insert media-only
#    cells in one click.
# 5. Inline images inside text cells render at natural size and are
#    resizable by dragging the corner.
# 6. Live Python still runs the same way; outputs go below the editor.
