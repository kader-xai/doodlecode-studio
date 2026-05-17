# doodlecode format-version: 2
# A 7-slide presentation deck for DoodleCode Studio.
# Open with 📂 Open → press 🎬 Present → use → / ← to step through.


# %% [markdown] color=rose title="The Problem"
# # 🤔 The Problem
#
# **Jupyter notebooks are built for the author, not for the audience.**
#
# - Code lives in tall vertical scrolls — fine for editing, painful to present.
# - There is no obvious place to attach a written explanation **beside** each
#   piece of code, so the speaker either talks over it or pre-bakes slides.
# - Switching between code, slides, and a whiteboard during a live talk
#   breaks the flow and loses the audience.
# - Presenting Python today means choosing: real running code, OR good
#   visuals — never both.


# %% [markdown] color=sky title="About this Project"
# # 🎨 About DoodleCode Studio
#
# **A doodle-powered Python notebook & presentation canvas.**
#
# - Every Python cell becomes a colored hand-drawn card on a pannable board.
# - Each card carries its own callout bubble — written by you, not by an AI.
# - A real Jupyter kernel runs under the hood, so `import pandas`, `plt.show()`,
#   `pip install …` all work.
# - Save your work and it becomes a single `.py` file you can email,
#   commit to git, or hand to a teammate.
# - Local-first. Open-source. MIT-licensed.


# %% color=mint title="Print + Arithmetic"
# @explain: The simplest possible Python — print + math.
# @explain: Useful as a sanity check that the kernel is alive.
print("Hello from DoodleCode!")

a = 7
b = 5

print("a + b  =", a + b)
print("a - b  =", a - b)
print("a * b  =", a * b)
print("a / b  =", a / b)
print("a ** b =", a ** b)


# %% color=violet title="Visualization"
# @explain: Live matplotlib chart — the image renders inside this cell.
# @explain: I'll annotate it on the canvas while presenting.
import matplotlib.pyplot as plt
import math

xs = [i / 10 for i in range(0, 63)]
sin = [math.sin(x) for x in xs]
cos = [math.cos(x) for x in xs]

plt.figure(figsize=(7, 3.5))
plt.plot(xs, sin, label="sin(x)", linewidth=2)
plt.plot(xs, cos, label="cos(x)", linewidth=2, linestyle="--")
plt.title("A first live chart")
plt.xlabel("x")
plt.ylabel("y")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()


# %% color=teal title="Visualization — Bar Chart"
# @explain: A categorical comparison. Same kernel, different chart type.
# @explain: I'll point out the tallest bar with the presenter pen.
import matplotlib.pyplot as plt

languages = ["Python", "JavaScript", "Rust", "Go", "Java"]
stars_k = [82, 74, 38, 41, 29]  # rough open-source popularity, in thousands

colors = ["#fcc419", "#74c0fc", "#ff8787", "#69db7c", "#b197fc"]

plt.figure(figsize=(7, 3.6))
bars = plt.bar(languages, stars_k, color=colors, edgecolor="#2a2a2a", linewidth=1.5)
plt.title("Popularity (illustrative)")
plt.ylabel("Stars (thousands)")
for bar, val in zip(bars, stars_k):
    plt.text(bar.get_x() + bar.get_width() / 2, val + 1.5, str(val),
             ha="center", va="bottom", fontsize=10)
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.show()


# %% color=sky title="Table Output"
# @explain: Tabular data printed straight from a list of dicts.
# @explain: No pandas needed — the kernel handles plain print just fine.
rows = [
    {"name": "Alice",   "role": "Designer",     "score": 92},
    {"name": "Bob",     "role": "Engineer",     "score": 87},
    {"name": "Carol",   "role": "Researcher",   "score": 95},
    {"name": "Diego",   "role": "Engineer",     "score": 78},
    {"name": "Eun-Ji",  "role": "Product",      "score": 89},
]

# Column widths sized to the longest value in each column.
cols = ["name", "role", "score"]
widths = {c: max(len(c), *(len(str(r[c])) for r in rows)) for c in cols}

header = " | ".join(c.upper().ljust(widths[c]) for c in cols)
sep    = "-+-".join("-" * widths[c] for c in cols)
print(header)
print(sep)
for r in rows:
    print(" | ".join(str(r[c]).ljust(widths[c]) for c in cols))

avg = sum(r["score"] for r in rows) / len(rows)
print(sep)
print(f"\nAverage score: {avg:.1f} across {len(rows)} people.")


# %% [markdown] color=amber title="What is a Slide Deck?"
# # 📑 The Deck, in One Card
#
# This file IS the deck:
#
# 1. **The Problem** — why notebooks alone don't present well.
# 2. **About** — what DoodleCode Studio is.
# 3. **Arithmetic** — live Python: print + add + multiply.
# 4. **Visualization** — sin / cos line chart with callouts.
# 5. **Visualization — Bar Chart** — categorical comparison.
# 6. **Table Output** — formatted text table from a list of dicts.
# 7. **This card** — the slide deck explaining the slide deck.
# 8. **Markdown + Images** — text + visuals from a single block.
# 9. **Thanks for watching** — closing card with the links.
#
# Every slide is a doodled card. Tap → / ← to walk through them, or jump
# by clicking a callout. Pen and highlighter live in the presenter bar.


# %% [markdown] color=peach title="Markdown + Images"
# # 🖼 Markdown can carry images
#
# Drop any URL or local image into a markdown cell and it renders inline.
#
# ![doodlecode studio logo](https://kader-xai.github.io/assets/doodlecode-banner.png)
#
# - Images load from any URL.
# - They scale to the cell width automatically.
# - Combine with bullets, headings, and `code spans` in the same card.
#
# > Use this slide style for diagrams, screenshots, or quick visual breaks
# > between code-heavy slides.


# %% [markdown] color=lime title="Thanks for Watching"
# # 🙏 Thanks for Watching
#
# **DoodleCode Studio**
#
# - Repo: <https://github.com/kader-xai/doodlecode-studio>
# - Website: <https://kader-xai.github.io>
# - LinkedIn: <https://linkedin.com/in/kader-xai>
# - GitHub: <https://github.com/kader-xai>
# - Meetup (Riyadh ML Group): <https://www.meetup.com/machine-learning-group-riyadh>
