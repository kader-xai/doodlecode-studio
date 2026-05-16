# %% [markdown]
# # Module 6 — Data Visualization for ML
# Charts you'll draw a hundred times: line, scatter, histogram, bar,
# heatmap. Then a quick tour of seaborn for higher-level stats plots.

# %% kind=install color=rose title="Install matplotlib + seaborn"
# @explain: Run once.
import importlib, subprocess, sys
for pkg in ["matplotlib", "seaborn"]:
    if importlib.util.find_spec(pkg) is None:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", pkg])
print("viz libs ready.")


# %% kind=import color=sky title="Imports"
# @explain: %matplotlib inline isn't needed — DoodleCode captures
# @explain: matplotlib output as image/png automatically.
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

np.random.seed(0)
sns.set_theme(style="whitegrid")


# %% kind=function color=mint title="Line plot"
# @explain: Use for time series or any continuous x. Multiple lines on
# @explain: the same axes makes them easy to compare.
x = np.linspace(0, 4 * np.pi, 200)
plt.figure(figsize=(6, 3))
plt.plot(x, np.sin(x), label="sin")
plt.plot(x, np.cos(x), label="cos", linestyle="--")
plt.legend()
plt.title("Sine vs cosine")
plt.xlabel("x")
plt.ylabel("value")
plt.show()


# %% kind=function color=mint title="Scatter plot — relationship between two features"
# @explain: Each dot is one sample. Color/size encode extra dimensions
# @explain: (here: class label).
n = 200
x = np.random.randn(n)
y = 2 * x + 0.5 * np.random.randn(n)
labels = (x + y > 0).astype(int)

plt.figure(figsize=(5, 4))
plt.scatter(x, y, c=labels, cmap="coolwarm", alpha=0.7, edgecolor="k")
plt.title("Two features, coloured by class")
plt.xlabel("feature 1")
plt.ylabel("feature 2")
plt.show()


# %% kind=function color=mint title="Histogram + KDE — looking at a distribution"
# @explain: Histogram bins counts; KDE smooths them. Tells you whether
# @explain: a feature is roughly normal, skewed, or multi-modal.
data = np.concatenate([np.random.normal(-2, 1, 500), np.random.normal(3, 1.5, 500)])

plt.figure(figsize=(6, 3))
sns.histplot(data, bins=40, kde=True, color="#5c7cfa")
plt.title("A bimodal distribution")
plt.show()


# %% kind=function color=mint title="Bar chart — category counts"
# @explain: Common for class balance plots. value_counts → bar.
labels = pd.Series(np.random.choice(["A", "B", "C", "D"], size=200, p=[0.4, 0.3, 0.2, 0.1]))

plt.figure(figsize=(5, 3))
labels.value_counts().sort_index().plot(kind="bar", color="#82c91e")
plt.title("Category counts")
plt.ylabel("count")
plt.show()


# %% kind=function color=mint title="Boxplot — distribution per group"
# @explain: Boxes show quartiles; whiskers show range; dots are outliers.
# @explain: The fastest way to compare distributions across groups.
df = pd.DataFrame({
    "group": np.repeat(list("ABC"), 100),
    "value": np.concatenate([
        np.random.normal(0, 1, 100),
        np.random.normal(1, 1.5, 100),
        np.random.normal(-1, 0.7, 100),
    ]),
})
plt.figure(figsize=(5, 3))
sns.boxplot(x="group", y="value", data=df, palette="Set2")
plt.title("Per-group distribution")
plt.show()


# %% kind=function color=mint title="Heatmap — correlation matrix"
# @explain: After a corr() on a DataFrame, heatmap shows it as a colour
# @explain: grid. The first thing to look at before regression.
x1 = np.random.randn(500)
x2 = x1 * 0.8 + np.random.randn(500) * 0.5
x3 = np.random.randn(500)
x4 = -x1 * 0.4 + np.random.randn(500) * 0.7
feats = pd.DataFrame({"x1": x1, "x2": x2, "x3": x3, "x4": x4})

plt.figure(figsize=(4, 3.5))
sns.heatmap(feats.corr(), annot=True, fmt=".2f", cmap="vlag", center=0, vmin=-1, vmax=1)
plt.title("Feature correlations")
plt.show()


# %% kind=function color=mint title="Subplots — multiple charts in one figure"
# @explain: plt.subplots(rows, cols) gives an axes grid. Each cell takes
# @explain: its own plot. Useful for dashboards and comparisons.
fig, axes = plt.subplots(1, 3, figsize=(10, 3))

t = np.linspace(0, 10, 200)
axes[0].plot(t, np.sin(t))
axes[0].set_title("sin")

axes[1].plot(t, np.cos(t), color="orange")
axes[1].set_title("cos")

axes[2].plot(t, np.tan(t), color="green")
axes[2].set_ylim(-5, 5)
axes[2].set_title("tan (clipped)")

plt.tight_layout()
plt.show()


# %% kind=function color=mint title="Pair plot — every feature vs every other"
# @explain: seaborn.pairplot draws scatter matrices coloured by class.
# @explain: An instant overview of pairwise feature relationships.
iris_like = pd.DataFrame({
    "sepal_len": np.random.normal(5, 0.5, 150),
    "sepal_wid": np.random.normal(3, 0.4, 150),
    "petal_len": np.random.normal(4, 1.5, 150),
    "petal_wid": np.random.normal(1.2, 0.7, 150),
    "species":   np.repeat(["setosa", "versicolor", "virginica"], 50),
})
sns.pairplot(iris_like, hue="species", height=1.6, plot_kws={"alpha": 0.6})
plt.show()


# %% [markdown]
# ## Practice
# 1. Plot the first 50 cumulative sums of standard-normal noise as a line.
# 2. Plot the histogram of 10 000 samples from a Beta(2, 5) distribution.


# %% kind=function color=mint title="Practice 1 — random walk line"
# @explain: cumsum on standard-normal noise = a 1D random walk. The
# @explain: classic stochastic-process plot.
steps = np.random.randn(50).cumsum()
plt.figure(figsize=(5, 3))
plt.plot(steps, marker="o", linewidth=1)
plt.title("Cumulative sum of noise")
plt.show()


# %% kind=function color=mint title="Practice 2 — Beta(2,5) histogram"
# @explain: Beta lives on [0,1]; (2,5) skews left. Useful for modelling
# @explain: probabilities and proportions.
samples = np.random.beta(2, 5, size=10_000)
plt.figure(figsize=(5, 3))
plt.hist(samples, bins=40, color="#fab005", edgecolor="black")
plt.title("Beta(2, 5)")
plt.show()


# %% [markdown]
# ## Recap
# - ✅ Line, scatter, histogram, bar, box, heatmap, pair, subplots
# - ✅ Both matplotlib (control) and seaborn (convenience)
#
# **Next:** Module 7 — Statistics for ML.
