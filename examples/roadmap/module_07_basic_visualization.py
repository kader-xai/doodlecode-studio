# doodlecode format-version: 2
# Auto-converted from module_07_basic_visualization.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 07 Basic Visualization"
# # Module 07 Basic Visualization
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 7 — Basic Visualization Tools"
# # Module 7 — Basic Visualization Tools
#
# *IBM Data Visualization · Module 2 of 5 (Module 7 of 16)*
#
# Seven core chart types. Pick the chart from the **question** you're answering, not from the chart list.
#
# | Question | Chart |
# |---|---|
# | What does the trend look like? | **line** (M6) |
# …


# %% color=mint title="Demo dataset reused below"
# @explain: Demo dataset reused below
!pip -q install pandas numpy matplotlib seaborn

import numpy as np, pandas as pd, matplotlib.pyplot as plt
rng = np.random.default_rng(0)

# Demo dataset reused below
df = pd.DataFrame({
    "category": rng.choice(list("ABCD"), 200),
    "x": rng.normal(0, 1, 200),
    "y": rng.normal(0, 1, 200),
    "size": rng.integers(20, 200, 200),
})
df["y"] = df["x"] * 1.2 + rng.normal(0, .5, 200)   # make x and y correlated
df.head()


# %% [markdown] color=peach title="1. Bar chart — comparing categories"
# # 1. Bar chart — comparing categories
#
# Use a bar when you're comparing a numeric value across categories. Vertical bars are usual; horizontal (`barh`) when category names are long.


# %% color=violet title="counts = df['category'].value_counts()"
# @explain: Run this cell to see the output.
counts = df["category"].value_counts()
fig, ax = plt.subplots(1, 2, figsize=(10, 3))
counts.plot.bar(ax=ax[0], title="Vertical bar — counts by category", rot=0, color="steelblue")
counts.plot.barh(ax=ax[1], title="Horizontal bar", color="darkorange")
plt.tight_layout(); plt.show()


# %% [markdown] color=amber title="Grouped bars — two series side-by-side"
# # Grouped bars — two series side-by-side
#


# %% color=rose title="Stacked = sum the bars on top of each other"
# @explain: Stacked = sum the bars on top of each other
sales = pd.DataFrame({
    "Q1": [100, 80, 65, 90],
    "Q2": [120, 95, 75, 110],
}, index=["A","B","C","D"])
sales.plot.bar(figsize=(7,3), title="Sales by quarter (grouped)", rot=0); plt.show()

# Stacked = sum the bars on top of each other
sales.plot.bar(stacked=True, figsize=(7,3), title="Sales (stacked)", rot=0); plt.show()


# %% [markdown] color=lime title="2. Histogram — distribution"
# # 2. Histogram — distribution
#
# A histogram chops the range into **bins** and counts how many values fall in each. Bin count matters: too few hides shape, too many is noise.


# %% color=teal title="fig"
# @explain: Run this cell to see the output.
fig, ax = plt.subplots(1, 3, figsize=(12, 3))
df["x"].plot.hist(bins=5,   ax=ax[0], title="bins=5 (too few)",   color="grey", alpha=.7)
df["x"].plot.hist(bins=20,  ax=ax[1], title="bins=20 (good)",     color="steelblue")
df["x"].plot.hist(bins=100, ax=ax[2], title="bins=100 (too many)",color="darkorange", alpha=.7)
plt.tight_layout(); plt.show()


# %% [markdown] color=sky title="Density (KDE) overlay — smoother view of the distribution"
# # Density (KDE) overlay — smoother view of the distribution
#


# %% color=mint title="import seaborn as sns"
# @explain: Run this cell to see the output.
import seaborn as sns
fig, ax = plt.subplots(figsize=(7, 3))
sns.histplot(df["x"], bins=20, kde=True, ax=ax)
ax.set_title("Histogram + KDE"); plt.show()


# %% [markdown] color=peach title="3. Pie chart — share of a whole (use sparingly)"
# # 3. Pie chart — share of a whole (use sparingly)
#
# Pies are hard to compare visually. A bar is almost always clearer. Use a pie only when:
# - there are **few** slices (≤5),
# - you want to communicate "share of total" emphatically,
# - exact ranking doesn't matter.


# %% color=violet title="counts = df['category'].value_counts()"
# @explain: Run this cell to see the output.
counts = df["category"].value_counts()
fig, ax = plt.subplots(1, 2, figsize=(9, 3))
counts.plot.pie(ax=ax[0], autopct="%.0f%%", title="Pie (basic)")
ax[0].set_ylabel("")
counts.plot.pie(ax=ax[1], autopct="%.0f%%", explode=[.05]*len(counts),
                shadow=True, startangle=90, title="Pie (decorated)")
ax[1].set_ylabel("")
plt.tight_layout(); plt.show()


# %% [markdown] color=amber title="4. Box plot — the 5-number summary"
# # 4. Box plot — the 5-number summary
#
# A box plot encodes:
# - **box** = 25th to 75th percentile (the IQR)
# - **line in the box** = median
# - **whiskers** = typically 1.5×IQR
# - **dots** beyond the whiskers = potential outliers
#
# …


# %% color=rose title="fig"
# @explain: Run this cell to see the output.
fig, ax = plt.subplots(figsize=(7, 3))
df.boxplot(column="x", by="category", ax=ax)
ax.set_title("x by category"); plt.suptitle(""); plt.show()


# %% [markdown] color=lime title="5. Scatter plot — relationship between two numeric variables"
# # 5. Scatter plot — relationship between two numeric variables
#
# When you want to know "do X and Y move together?", scatter is the chart.


# %% color=teal title="fig"
# @explain: Run this cell to see the output.
fig, ax = plt.subplots(figsize=(6, 5))
ax.scatter(df["x"], df["y"], alpha=.5, color="steelblue")
ax.set(xlabel="x", ylabel="y", title="Scatter — x vs y")
ax.grid(alpha=.3); plt.show()


# %% [markdown] color=sky title="Colour points by a category"
# # Colour points by a category
#


# %% color=mint title="import seaborn as sns"
# @explain: Run this cell to see the output.
import seaborn as sns
sns.scatterplot(data=df, x="x", y="y", hue="category", alpha=.7)
plt.title("Scatter coloured by category"); plt.show()


# %% [markdown] color=peach title="6. Bubble chart — scatter with a 3rd dimension via size"
# # 6. Bubble chart — scatter with a 3rd dimension via size
#


# %% color=violet title="fig"
# @explain: Run this cell to see the output.
fig, ax = plt.subplots(figsize=(7, 5))
ax.scatter(df["x"], df["y"], s=df["size"], alpha=.4, color="darkorange",
           edgecolors="black", linewidth=.5)
ax.set(xlabel="x", ylabel="y", title="Bubble — size encodes a 3rd variable")
plt.show()


# %% [markdown] color=amber title="7. Area plot — stacked over time"
# # 7. Area plot — stacked over time
#
# An area plot is a line plot with the area below filled. Stack multiple to show **composition over time**.


# %% color=rose title="years = pd.date_range('2018'"
# @explain: Run this cell to see the output.
years = pd.date_range("2018", periods=6, freq="YE").year
sales = pd.DataFrame({
    "Online":   [10, 14, 22, 35, 45, 60],
    "Retail":   [40, 38, 30, 25, 20, 18],
    "Wholesale":[25, 27, 30, 28, 32, 35],
}, index=years)

fig, ax = plt.subplots(1, 2, figsize=(12, 3))
sales.plot.area(ax=ax[0], title="Stacked area — channel mix over time")
sales.plot.area(stacked=False, alpha=.5, ax=ax[1], title="Unstacked area")
plt.tight_layout(); plt.show()


# %% [markdown] color=lime title="8. Putting all 7 on one figure (the cheat-sheet view)"
# # 8. Putting all 7 on one figure (the cheat-sheet view)
#


# %% color=teal title="fig"
# @explain: Run this cell to see the output.
fig, axes = plt.subplots(2, 4, figsize=(15, 7))
df["category"].value_counts().plot.bar(ax=axes[0,0], title="bar", rot=0)
df["x"].plot.hist(bins=20, ax=axes[0,1], title="hist")
df["category"].value_counts().plot.pie(ax=axes[0,2], autopct="%.0f%%", title="pie")
axes[0,2].set_ylabel("")
df.boxplot(column="x", by="category", ax=axes[0,3]); axes[0,3].set_title("box")
axes[1,0].scatter(df.x, df.y, alpha=.5); axes[1,0].set_title("scatter")
axes[1,1].scatter(df.x, df.y, s=df["size"], alpha=.4); axes[1,1].set_title("bubble")
sales.plot.area(ax=axes[1,2], title="area"); axes[1,2].legend(fontsize=8)
df.plot.line(x="x", y="y", ax=axes[1,3], title="line (sorted)", legend=False, alpha=.4)
plt.suptitle("")
plt.tight_layout(); plt.show()


# %% [markdown] color=sky title="9. Practice"
# # 9. Practice
#
# 1. Make a horizontal bar chart of average `y` for each `category` in `df`.
# 2. Plot a histogram of `df["x"]` with the mean shown as a vertical red line.
# 3. Make a scatter of `x` vs `y` with point colour by `category` AND point size proportional to `size`.
# 4. Build a stacked area plot of `sales` re-indexed so the first row is `0` (everything starts at the same baseline).


# %% color=mint title="1)"
# @explain: 1)
# @explain: 2)
# @explain: 3)
# @explain: 4)
import matplotlib.pyplot as plt
# 1)
df.groupby("category")["y"].mean().plot.barh(title="Avg y per category"); plt.show()

# 2)
fig, ax = plt.subplots(figsize=(7,3))
df["x"].plot.hist(bins=20, ax=ax, title="x with mean")
ax.axvline(df["x"].mean(), color="red", linestyle="--", label=f"mean={df.x.mean():.2f}")
ax.legend(); plt.show()

# 3)
import seaborn as sns
sns.scatterplot(data=df, x="x", y="y", hue="category", size="size",
                sizes=(20, 300), alpha=.6); plt.show()

# 4)
baselined = sales - sales.iloc[0]
baselined.plot.area(stacked=True, title="Sales — change since 2018"); plt.show()


# %% [markdown] color=peach title="Recap"
# # Recap
#
# ✅ Use bar/horiz-bar/grouped/stacked for category comparisons
# ✅ Read a histogram and pick a sensible bin count
# ✅ Resist the pie chart unless it's clearly the right call
# ✅ Read a box plot's 5 numbers + outliers
# ✅ Use scatter and bubble for relationships and 3rd-dim encoding
# ✅ Stack areas for composition-over-time
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


