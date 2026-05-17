# doodlecode format-version: 2
# Auto-converted from module_09_advanced_visualization.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 09 Advanced Visualization"
# # Module 09 Advanced Visualization
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 9 — Advanced Visualization"
# # Module 9 — Advanced Visualization
#
# *IBM Data Visualization · Module 4 of 5 (Module 9 of 16)*
#
# You can produce charts; this module is about producing **publication-quality** charts. We cover:
#
# 1. Subplots — many small charts vs one big one
# 2. Time-series visualisation patterns (rolling means, resample, range fill)
# 3. Animation (`FuncAnimation`)
# …


# %% color=mint title="!pip -q install matplotlib pandas numpy seaborn plotly"
# @explain: Run this cell to see the output.
!pip -q install matplotlib pandas numpy seaborn plotly


# %% [markdown] color=peach title="1. Subplots — `plt.subplots(rows, cols)`"
# # 1. Subplots — `plt.subplots(rows, cols)`
#
# A grid of small charts often communicates more than one giant chart. The pattern: one figure, many `Axes` returned in a 2D NumPy array.


# %% color=violet title="import numpy as np"
# @explain: Run this cell to see the output.
import numpy as np, pandas as pd, matplotlib.pyplot as plt
rng = np.random.default_rng(0)

fig, axes = plt.subplots(2, 3, figsize=(12, 6))
for i, ax in enumerate(axes.flat):
    ax.plot(np.linspace(0, 10, 100), np.sin(np.linspace(0, 10, 100) + i))
    ax.set_title(f"phase shift {i}")
plt.tight_layout(); plt.show()


# %% [markdown] color=amber title="Sharing axes — `sharex` / `sharey`"
# # Sharing axes — `sharex` / `sharey`
#


# %% color=rose title="fig"
# @explain: Run this cell to see the output.
fig, axes = plt.subplots(3, 1, figsize=(8, 5), sharex=True)
x = np.linspace(0, 10, 200)
for i, ax in enumerate(axes):
    ax.plot(x, np.sin(x * (i+1)))
    ax.set_ylabel(f"f×{i+1}")
axes[-1].set_xlabel("x")
plt.tight_layout(); plt.show()


# %% [markdown] color=lime title="Mixed grid with `gridspec`"
# # Mixed grid with `gridspec`
#


# %% color=teal title="import matplotlib.gridspec as gs"
# @explain: Run this cell to see the output.
import matplotlib.gridspec as gs
fig = plt.figure(figsize=(10, 5))
g = gs.GridSpec(2, 3, figure=fig)

ax1 = fig.add_subplot(g[0, :])      # full top row
ax2 = fig.add_subplot(g[1, 0])
ax3 = fig.add_subplot(g[1, 1:])

x = np.linspace(0, 10, 200)
ax1.plot(x, np.sin(x), color="steelblue"); ax1.set_title("wide top")
ax2.hist(rng.normal(0,1,200), bins=20); ax2.set_title("hist")
ax3.scatter(rng.normal(0,1,200), rng.normal(0,1,200), alpha=.5); ax3.set_title("scatter")
plt.tight_layout(); plt.show()


# %% [markdown] color=sky title="2. Time-series patterns"
# # 2. Time-series patterns
#
# Three patterns you'll use over and over:
#
# 1. **Rolling mean** — smooth out noise.
# 2. **Resample** — aggregate to a coarser frequency.
# 3. **Range fill** — show a band (e.g. ±1 std) around a line.


# %% color=mint title="dates = pd.date_range('2024-01-01'"
# @explain: Run this cell to see the output.
dates = pd.date_range("2024-01-01", periods=180)
ts = pd.DataFrame({"sales": np.cumsum(rng.standard_normal(180)) + 50}, index=dates)

fig, ax = plt.subplots(figsize=(10, 3))
ts["sales"].plot(ax=ax, alpha=.4, label="raw")
ts["sales"].rolling(7).mean().plot(ax=ax, label="7-day MA", linewidth=2)
ts["sales"].rolling(30).mean().plot(ax=ax, label="30-day MA", linewidth=2)
ax.legend(); ax.set_title("Rolling means smooth noise"); plt.show()


# %% color=peach title="Resample"
# @explain: Resample — daily → weekly mean
# Resample — daily → weekly mean
weekly = ts.resample("W").mean()
fig, ax = plt.subplots(figsize=(10, 3))
ts.plot(ax=ax, alpha=.3, label="daily", legend=False)
weekly.plot(ax=ax, color="darkorange", label="weekly mean")
ax.legend(["daily","weekly mean"]); ax.set_title("Resample to weekly"); plt.show()


# %% color=violet title="Range fill"
# @explain: Range fill — line with ±1 std band
# Range fill — line with ±1 std band
roll = ts["sales"].rolling(14)
mu, sd = roll.mean(), roll.std()
fig, ax = plt.subplots(figsize=(10, 3))
ax.plot(ts.index, ts["sales"], alpha=.3, color="grey", label="raw")
ax.plot(ts.index, mu, color="steelblue", label="14-day mean")
ax.fill_between(ts.index, mu - sd, mu + sd, color="steelblue", alpha=.2, label="±1 std")
ax.legend(); ax.set_title("Mean with ±1σ band"); plt.show()


# %% [markdown] color=amber title="3. Animation — `FuncAnimation`"
# # 3. Animation — `FuncAnimation`
#
# A function-based animation re-renders one frame at a time. In Colab/Jupyter it renders as inline JS+HTML.


# %% color=rose title="from matplotlib.animation import FuncAnimation"
# @explain: Run this cell to see the output.
from matplotlib.animation import FuncAnimation
from IPython.display import HTML

fig, ax = plt.subplots(figsize=(7, 3))
x = np.linspace(0, 2*np.pi, 200)
line, = ax.plot(x, np.sin(x))
ax.set_ylim(-1.2, 1.2); ax.set_title("y = sin(x − t)")

def update(t):
    line.set_ydata(np.sin(x - t/5))
    return line,

ani = FuncAnimation(fig, update, frames=60, interval=80, blit=True)
plt.close(fig)
HTML(ani.to_jshtml())


# %% [markdown] color=lime title="4. Customisation — making it look professional"
# # 4. Customisation — making it look professional
#
# Six things that take a chart from "Excel default" to "publication ready":
#
# 1. **Remove top/right spines** — visual clutter.
# 2. **Annotate** the point you want the eye to land on.
# 3. **Pick a deliberate colour palette** instead of the default.
# 4. **Title / subtitle hierarchy** — different weights and sizes.
# …


# %% color=teal title="Strip top/right spines"
# @explain: Strip top/right spines
# @explain: Title hierarchy
# @explain: Annotation
x = np.linspace(0, 10, 200)
fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(x, np.sin(x), color="#1f77b4", linewidth=2, label="sin")
ax.fill_between(x, np.sin(x), alpha=.15, color="#1f77b4")
ax.axhline(0, color="grey", linewidth=.6)

# Strip top/right spines
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

# Title hierarchy
ax.set_title("Sine wave", fontsize=14, fontweight="bold", loc="left")
ax.text(0, 1.18, "with explicit annotation and band", fontsize=10, color="grey", transform=ax.transAxes)

ax.set_xlabel("time (s)"); ax.set_ylabel("amplitude")
ax.grid(alpha=.25)
ax.legend(frameon=False)

# Annotation
ax.annotate("first peak", xy=(np.pi/2, 1), xytext=(2.5, 1.1),
            arrowprops=dict(arrowstyle="->", color="grey"))
plt.show()


# %% [markdown] color=sky title="Twin axis — two y-scales"
# # Twin axis — two y-scales
#


# %% color=mint title="fig"
# @explain: Run this cell to see the output.
fig, ax = plt.subplots(figsize=(9, 3))
ax.plot(ts.index, ts["sales"], color="steelblue", label="sales")
ax.set_ylabel("sales", color="steelblue")

ax2 = ax.twinx()
ax2.plot(ts.index, ts["sales"].pct_change()*100, color="darkorange", alpha=.6, label="pct change")
ax2.set_ylabel("daily % change", color="darkorange")
ax.set_title("Two series, two y-scales"); plt.show()


# %% [markdown] color=peach title="5. Interactive charts with Plotly Express"
# # 5. Interactive charts with Plotly Express
#
# A Plotly chart is interactive by default — hover, zoom, pan. One-line API.


# %% color=violet title="import plotly.express as px"
# @explain: Run this cell to see the output.
import plotly.express as px

fig = px.scatter(ts.reset_index().rename(columns={"index":"date"}),
                 x="date", y="sales", title="Plotly — sales (interactive)")
fig.show()


# %% color=amber title="rng = np.random.default_rng(0)"
# @explain: Run this cell to see the output.
rng = np.random.default_rng(0)
df_plot = pd.DataFrame({
    "x": rng.normal(0,1,200),
    "y": rng.normal(0,1,200),
    "size": rng.integers(20, 200, 200),
    "category": rng.choice(list("ABCD"), 200),
})
fig = px.scatter(df_plot, x="x", y="y", color="category", size="size",
                 hover_data=["category"], title="Plotly — bubble by category")
fig.show()


# %% [markdown] color=rose title="6. Practice"
# # 6. Practice
#
# 1. Build a 2×2 subplot of: raw sales, 7-day MA, daily change histogram, scatter of sales vs lagged sales (`shift(1)`).
# 2. Animate a histogram so the data shifts right by 0.1 each frame for 30 frames (use `np.random.normal(loc=t*0.1, scale=1, size=500)`).
# 3. Make a Plotly line chart of TSLA close price for the last year (use yfinance).


# %% color=lime title="1)"
# @explain: 1)
# @explain: 3) — uncomment if running in Colab
# @explain: import yfinance as yf, plotly.express as px
# @explain: h = yf.Ticker("TSLA").history(period="1y")[["Close"]].reset_index()
# @explain: px.line(h, x="Date", y="Close", title="TSLA — interactive").show()
import numpy as np, pandas as pd, matplotlib.pyplot as plt

# 1)
rng = np.random.default_rng(0)
ts2 = pd.DataFrame({"sales": np.cumsum(rng.standard_normal(180)) + 50},
                   index=pd.date_range("2024-01-01", periods=180))

fig, ax = plt.subplots(2, 2, figsize=(11, 6))
ts2.plot(ax=ax[0,0], title="raw", legend=False)
ts2.rolling(7).mean().plot(ax=ax[0,1], title="7-day MA", legend=False)
ts2.diff().plot.hist(bins=30, ax=ax[1,0], title="daily change")
ax[1,1].scatter(ts2["sales"].shift(1), ts2["sales"], alpha=.5)
ax[1,1].set(title="lag plot", xlabel="sales(t-1)", ylabel="sales(t)")
plt.tight_layout(); plt.show()

# 3) — uncomment if running in Colab
# import yfinance as yf, plotly.express as px
# h = yf.Ticker("TSLA").history(period="1y")[["Close"]].reset_index()
# px.line(h, x="Date", y="Close", title="TSLA — interactive").show()

print("Animation example: see the FuncAnimation cell above for the pattern.")


# %% [markdown] color=teal title="Recap"
# # Recap
#
# ✅ Layout grids of charts with `subplots` and `gridspec`
# ✅ Visualise time-series with rolling means, resample, range fills
# ✅ Animate with `FuncAnimation`
# ✅ Customise spines, annotations, twin axes, palette, titles
# ✅ Drop into Plotly Express for interactivity in one line
#
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


