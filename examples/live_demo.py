# doodlecode format-version: 2
# A live-presentation walkthrough of DoodleCode Studio.
# Open with 📂 Open → press 🎬 Present → use → / ← to step through.


# %% [markdown] color=rose title="The problem"
# # 🤔 The problem
#
# **It is very hard to interactively showcase simple Python code
# using Jupyter notebooks.**
#
# - Plain Jupyter cells are vertical, monochrome, and built for the
#   author — not the audience.
# - There is no obvious way to attach a written explanation BESIDE
#   each piece of code.
# - Presenting the same notebook to a room means scrolling endlessly
#   while people lose their place.
# - There is no presenter mode, no laser-pointer-style highlight,
#   no "fit this cell to the screen" — you just zoom your browser.
#
# **So I built this doodle app that sits on top of those ideas and
# lets you show Python code in a nice, visual format.** 👇


# %% [markdown] color=sky title="Welcome"
# # 👋 Welcome
#
# **This is the app to present Python into a doodle-style format.**
#
# A local-first notebook where every Python cell becomes a colored
# hand-drawn card, with your own explanations beside it. You can run
# the code, save the file, and present the result — all in one place.
#
# *Press the right arrow → to begin the tour.*


# %% [markdown] color=mint title="The canvas"
# # 🎨 The canvas — what you can do
#
# - **Drag a box** with the **✥ Move** tool (top-left toggle) to
#   reposition it.
# - **Drag the canvas** with the **✋ Hand** tool to pan around.
# - Click **🌙 Dark / ☀ Light** in the top-right to flip the theme.
# - Click **📐 Auto-Space [Presentation]** in the toolbar to spread
#   every cell out one-per-slide. Click **🔗 Together** to bring them
#   back close-packed for editing.
#
# *Try them now, then come back and press → to continue.*


# %% kind=intro color=peach title="Callouts — your voice on the right"
# @explain: The bubble on the right is the CALLOUT — it lives in this
# @explain: file as `# @explain:` comments. You can edit it by clicking
# @explain: the ✎ button on the cell header, or by double-clicking the
# @explain: cell. Try editing this callout to say whatever you want.
# @explain: Then click ▶ to run the code; the output drops in below.
print("hello, world")


# %% kind=function color=mint title="Two callouts on one cell"
# @explain: A cell can have many callouts. Click ✎ then ＋ add to make
# @explain: a second bubble. Useful for layered explanations.
# @callout title="Tip" color=lavender
# @explain: Every callout has its own color. The colored strip on the
# @explain: cell header is the primary callout's color.
def greet(name):
    return f"Hello, {name}!"


print(greet("Kader"))


# %% [markdown] color=rose title="📦 Install matplotlib (one-time)"
# # 📦 Install a library
#
# The next cell draws a plot, which needs **matplotlib** + **numpy**.
# Most fresh kernels don't have them yet — let's install:
#
# 1. Click **📦 Install** in the toolbar.
# 2. In the prompt, type: `matplotlib numpy`
# 3. Click **▶ Install** and wait ~30 seconds.
# 4. The dialog will say "✅ Installed". Close it (✕).
# 5. Press → and run the next cell.
#
# > Same trick works for any PyPI package: `pandas`, `seaborn`,
# > `scikit-learn`, `torch`. The 📦 Install button is your friend.


# %% kind=function color=mint title="Visualization — sine + noise"
# @explain: This cell uses matplotlib + numpy. Click ▶ Run after
# @explain: installing them. The output panel below the editor renders
# @explain: the chart inline — no extra setup needed (the kernel
# @explain: auto-enables %matplotlib inline at startup).
import matplotlib.pyplot as plt
import numpy as np

np.random.seed(0)
x = np.linspace(0, 10, 200)
y = np.sin(x) + np.random.randn(200) * 0.15

fig, ax = plt.subplots(figsize=(6, 3))
ax.plot(x, y, color="#1971c2", linewidth=1.5)
ax.set_title("A noisy sine wave")
ax.grid(alpha=0.3)
plt.show()

print(f"y mean = {y.mean():.3f}")


# %% kind=assign color=peach title="One more — a tiny pandas table"
# @explain: Pandas comes along when you install matplotlib (numpy is a
# @explain: shared dep). The result renders as a plain-text table in
# @explain: the output panel.
import pandas as pd

df = pd.DataFrame(
    {"city": ["NY", "LA", "Berlin", "Tokyo"],
     "users":[120, 84, 67, 145],
     "growth":[0.08, 0.12, 0.04, 0.21]}
)
print(df.sort_values("growth", ascending=False).to_string(index=False))


# %% [markdown] color=violet title="During the talk"
# # 🎤 While presenting
#
# Once you're in **🎬 Present** mode:
#
# - **→ / ← arrows** step between slides; the canvas auto-fits each one.
# - **✒️ Pen (P)** — drag to draw red ink that fades in ~1.5 seconds.
#   Perfect for circling something to draw the audience's eye.
# - **🖍 Highlighter (H)** — thick yellow ink, fades in ~4 seconds.
#   Use it to leave a note on a slide while you talk.
# - The **✋ Hand** tool still pans the canvas mid-talk if you need to
#   move around freely.
# - **Esc** exits presentation; all ink strokes auto-clear.


# %% [markdown] color=yellow title="🎉 Thanks for watching"
# # 🎉 Thanks for watching!
#
# That's DoodleCode Studio in a few minutes.
#
# **To get the project**, click the **ⓘ About** button in the top
# right — the project URL is the big yellow card with the 👉 hand
# pointing at it.
#
# - ⭐ Star it on GitHub
# - 🍴 Fork it / clone it locally
# - 🐞 Issues and PRs welcome
#
# *Co-AI Developed by Kader Mohideen.*
