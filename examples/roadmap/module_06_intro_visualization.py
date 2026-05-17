# doodlecode format-version: 2
# Auto-converted from module_06_intro_visualization.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 06 Intro Visualization"
# # Module 06 Intro Visualization
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 6 — Introduction to Data Visualization"
# # Module 6 — Introduction to Data Visualization
#
# *IBM Data Visualization with Python · Module 1 of 5 (Module 6 of 16)*
#
# A two-line plot can reveal a pattern that hours of `.describe()` miss. This module gives you the **mental model** of charting in Python and gets you fluent in `matplotlib` — the foundation everything else (pandas plotting, seaborn, plotly) sits on top of.
#
# ### What you'll cover
# 1. What data viz is for — three jobs of a chart
# 2. Matplotlib's two APIs (pyplot vs object-oriented) — pick OO
# …


# %% color=mint title="!pip -q install matplotlib pandas numpy"
# @explain: Run this cell to see the output.
!pip -q install matplotlib pandas numpy


# %% [markdown] color=peach title="1. The three jobs of a chart"
# # 1. The three jobs of a chart
#
# | Job | Example chart | Question it answers |
# |---|---|---|
# | **Compare** | bar chart | which is biggest? |
# | **Show distribution** | histogram, boxplot | what's the spread? |
# | **Show relationship** | scatter, line | does X track Y? |
#
# …


# %% [markdown] color=violet title="2. Matplotlib has two APIs — use the OO one"
# # 2. Matplotlib has two APIs — use the OO one
#
# | API | Looks like | When |
# |---|---|---|
# | `pyplot` (state machine) | `plt.plot(...); plt.title(...)` | quick throwaway |
# | **Object-oriented** | `fig, ax = plt.subplots(); ax.plot(...); ax.set_title(...)` | always, in real work |
#
# The OO version scales to subplots and is what you'll see in any serious codebase.


# %% color=amber title="pyplot style"
# @explain: pyplot style — fine for a quick look
# @explain: OO style — same chart, but you hold the Axes
import numpy as np, matplotlib.pyplot as plt

# pyplot style — fine for a quick look
plt.plot([1,2,3,4], [10,20,15,30])
plt.title("pyplot style"); plt.show()

# OO style — same chart, but you hold the Axes
fig, ax = plt.subplots()
ax.plot([1,2,3,4], [10,20,15,30])
ax.set_title("OO style"); plt.show()


# %% [markdown] color=rose title="3. Figure & Axes — the object model"
# # 3. Figure & Axes — the object model
#
# - **Figure** — the whole window/canvas. One Figure can have many Axes.
# - **Axes** — one plotting area (with x-axis, y-axis, title, etc.). This is the thing you draw on.
# - **Axis** — singular, the actual x or y axis line/ticks/labels.
#
# 99% of the time you talk to **Axes** (`ax`).


# %% color=lime title="fig"
# @explain: Run this cell to see the output.
fig, ax = plt.subplots(figsize=(7, 3))
print("figure:", fig)
print("axes  :", ax)


# %% [markdown] color=teal title="4. Line plots — the canonical chart"
# # 4. Line plots — the canonical chart
#
# Every styling concept introduces itself on a line plot first.


# %% color=sky title="import numpy as np"
# @explain: Run this cell to see the output.
import numpy as np, matplotlib.pyplot as plt

x  = np.linspace(0, 4*np.pi, 200)
y1 = np.sin(x)
y2 = np.cos(x)

fig, ax = plt.subplots(figsize=(8, 3))
ax.plot(x, y1, label="sin", color="#1f77b4", linewidth=2)
ax.plot(x, y2, label="cos", color="#d62728", linestyle="--", linewidth=1.5)

ax.set_title("sin & cos")
ax.set_xlabel("x (radians)")
ax.set_ylabel("y")
ax.legend()
ax.grid(alpha=.3)

plt.show()


# %% [markdown] color=mint title="Common style options to remember"
# # Common style options to remember
#
# | Option | Values |
# |---|---|
# | `color=` | name (`"red"`), hex (`"#ff7b00"`), or shorthand (`"r"`) |
# | `linestyle=` | `"-"`, `"--"`, `":"`, `"-."` |
# | `linewidth=` | float (default 1.5) |
# | `marker=` | `"o"`, `"s"`, `"^"`, `"x"` |
# …


# %% color=peach title="x = np.linspace(0"
# @explain: Run this cell to see the output.
x = np.linspace(0, 10, 30)
fig, ax = plt.subplots(figsize=(8, 3))
ax.plot(x, np.sin(x),     marker="o", linestyle="-",  label="sin")
ax.plot(x, np.sin(x)+0.5, marker="s", linestyle="--", label="sin+0.5")
ax.plot(x, np.sin(x)-0.5, marker="^", linestyle=":",  label="sin-0.5", alpha=.6)
ax.legend(); ax.set_title("markers + linestyles"); plt.show()


# %% [markdown] color=violet title="5. Saving a figure"
# # 5. Saving a figure
#


# %% color=amber title="Save to disk"
# @explain: Save to disk — PNG, PDF, SVG all supported
import matplotlib.pyplot as plt, numpy as np
fig, ax = plt.subplots(figsize=(6, 3))
ax.plot(np.arange(10), np.arange(10) ** 0.5)
ax.set_title("Saved chart")

# Save to disk — PNG, PDF, SVG all supported
fig.savefig("/tmp/chart.png", dpi=150, bbox_inches="tight")
print("saved /tmp/chart.png")
plt.show()


# %% [markdown] color=rose title="6. Plotting straight from pandas"
# # 6. Plotting straight from pandas
#
# Pandas wraps matplotlib. `series.plot()` and `df.plot()` are the fastest path from data to chart.


# %% color=lime title="import pandas as pd"
# @explain: Run this cell to see the output.
import pandas as pd, numpy as np
rng = np.random.default_rng(0)

df = pd.DataFrame({
    "month": pd.date_range("2024-01-01", periods=12, freq="ME"),
    "sales": rng.integers(80, 200, 12),
    "ads":   rng.integers(10, 50, 12),
}).set_index("month")

ax = df["sales"].plot(figsize=(8,3), title="Monthly sales", marker="o")
ax.set_ylabel("units"); plt.show()


# %% color=teal title="Two columns"
# @explain: Two columns, same axes
# @explain: Two columns, separate sub-axes
# Two columns, same axes
ax = df.plot(figsize=(8,3), title="Sales vs ads spend")
ax.set_ylabel("count"); plt.show()

# Two columns, separate sub-axes
df.plot(subplots=True, figsize=(8, 4)); plt.tight_layout(); plt.show()


# %% [markdown] color=sky title="7. Reading a real dataset and plotting it"
# # 7. Reading a real dataset and plotting it
#
# Quick end-to-end: pull a CSV from the web, pick a column, plot the trend.


# %% color=mint title="import pandas as pd"
# @explain: Run this cell to see the output.
import pandas as pd
url = "https://raw.githubusercontent.com/datasets/co2-ppm/master/data/co2-mm-mlo.csv"
co2 = pd.read_csv(url, parse_dates=["Date"]).set_index("Date")
print(co2.head())

ax = co2["Average"].plot(figsize=(9,3), title="Atmospheric CO₂ at Mauna Loa")
ax.set_ylabel("ppm"); ax.grid(alpha=.3); plt.show()


# %% [markdown] color=peach title="8. Practice"
# # 8. Practice
#
# 1. Plot `y = x²` and `y = x³` for x in [-3, 3] on the same axes, with a legend, gridlines, and clear axis labels.
# 2. From the CO₂ dataset above, plot the **rolling 12-month mean** alongside the raw monthly value.
# 3. Generate a DataFrame with 100 days of two random walks (`np.cumsum(np.random.randn(...))`) and plot them.


# %% color=violet title="1)"
# @explain: 1)
# @explain: 2)
# @explain: 3)
import numpy as np, pandas as pd, matplotlib.pyplot as plt

# 1)
x = np.linspace(-3, 3, 200)
fig, ax = plt.subplots(figsize=(7,3))
ax.plot(x, x**2, label="x²")
ax.plot(x, x**3, label="x³", linestyle="--")
ax.set(title="x² vs x³", xlabel="x", ylabel="y"); ax.grid(alpha=.3); ax.legend(); plt.show()

# 2)
co2["roll12"] = co2["Average"].rolling(12).mean()
co2[["Average","roll12"]].plot(figsize=(9,3), title="CO₂ raw vs 12-mo rolling mean"); plt.show()

# 3)
days = pd.date_range("2024-01-01", periods=100)
walks = pd.DataFrame({
    "A": np.cumsum(np.random.randn(100)),
    "B": np.cumsum(np.random.randn(100)),
}, index=days)
walks.plot(figsize=(9,3), title="Two random walks"); plt.show()


# %% [markdown] color=amber title="Recap"
# # Recap
#
# ✅ Pick the right chart for the question
# ✅ Use the OO matplotlib API (`fig, ax = plt.subplots()`)
# ✅ Style lines with colour, linestyle, linewidth, marker, alpha
# ✅ Save figures with `fig.savefig`
# ✅ Plot directly from pandas
#
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


