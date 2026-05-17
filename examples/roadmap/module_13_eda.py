# doodlecode format-version: 2
# Auto-converted from module_13_eda.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 13 Eda"
# # Module 13 Eda
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 13 — Exploratory Data Analysis (EDA)"
# # Module 13 — Exploratory Data Analysis (EDA)
#
# *IBM Data Analysis · Module 3 of 6 (Module 13 of 16)*
#
# EDA is the **chart-driven hunt for patterns** before any modelling. The goal is to walk away with three sentences:
#
# > "Here's how the target is distributed. Here are the 2-3 features that matter most. Here's the weird thing we should fix or watch."
#
# ### What you'll cover
# …


# %% color=mint title="!pip -q install pandas numpy seaborn matplotlib scipy"
# @explain: Run this cell to see the output.
!pip -q install pandas numpy seaborn matplotlib scipy
import pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns

url  = "https://archive.ics.uci.edu/ml/machine-learning-databases/auto-mpg/auto-mpg.data"
cols = ["mpg","cylinders","displacement","horsepower","weight",
        "acceleration","model_year","origin","car_name"]
cars = pd.read_csv(url, sep=r"\s+", names=cols, na_values="?")
cars["horsepower"] = cars["horsepower"].fillna(cars["horsepower"].median())
cars["origin"] = cars["origin"].map({1:"USA",2:"Europe",3:"Japan"}).astype("category")
cars.head()


# %% [markdown] color=peach title="1. Univariate — one variable at a time"
# # 1. Univariate — one variable at a time
#
# For each numeric column, look at its distribution. For each categorical column, look at the value counts.


# %% color=violet title="Numeric distributions in one figure"
# @explain: Numeric distributions in one figure
# Numeric distributions in one figure
fig, axes = plt.subplots(2, 3, figsize=(13, 6))
for ax, col in zip(axes.flat, ["mpg","horsepower","weight","displacement","acceleration","model_year"]):
    cars[col].plot.hist(bins=20, ax=ax, color="steelblue", edgecolor="white")
    ax.set_title(col)
plt.tight_layout(); plt.show()

print(cars.describe().round(2).T)


# %% color=amber title="Categorical: origin"
# @explain: Categorical: origin
# Categorical: origin
sns.countplot(data=cars, x="origin"); plt.title("Cars per origin"); plt.show()
print(cars["origin"].value_counts())


# %% [markdown] color=rose title="2. Bivariate — pairs of variables"
# # 2. Bivariate — pairs of variables
#
# Three useful pair patterns:
#
# | X type | Y type | Chart |
# |---|---|---|
# | numeric | numeric | scatter (+ regplot for trend) |
# | categorical | numeric | boxplot or violin |
# …


# %% color=lime title="numeric vs numeric"
# @explain: numeric vs numeric
# numeric vs numeric
sns.regplot(data=cars, x="weight", y="mpg", scatter_kws={"alpha":.4},
            line_kws={"color":"red"})
plt.title("Heavier cars get worse mpg — strong negative slope"); plt.show()


# %% color=teal title="categorical vs numeric"
# @explain: categorical vs numeric
# @explain: violin = box + density
# categorical vs numeric
sns.boxplot(data=cars, x="origin", y="mpg")
plt.title("Japanese cars have the highest mpg distribution"); plt.show()

# violin = box + density
sns.violinplot(data=cars, x="origin", y="mpg"); plt.title("Same data, violin"); plt.show()


# %% color=sky title="categorical vs categorical"
# @explain: categorical vs categorical
# categorical vs categorical
ct = pd.crosstab(cars["origin"], cars["cylinders"])
print(ct)
sns.heatmap(ct, annot=True, fmt="d", cmap="Blues")
plt.title("Counts: origin vs cylinders"); plt.show()


# %% [markdown] color=mint title="3. Correlation — which features move together?"
# # 3. Correlation — which features move together?
#
# Correlation $r \in [-1, 1]$:
# - $r = +1$ → perfect positive
# - $r = -1$ → perfect negative
# - $r \approx 0$ → no linear relationship
#
# ⚠️ Correlation only catches **linear** relationships. Always look at scatter plots too.


# %% color=peach title="corr = cars.select_dtypes('number').corr()"
# @explain: Run this cell to see the output.
corr = cars.select_dtypes("number").corr()
print(corr.round(2))

fig, ax = plt.subplots(figsize=(7, 5))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0,
            square=True, ax=ax)
ax.set_title("Correlation heatmap"); plt.show()


# %% [markdown] color=violet title="Pearson vs Spearman"
# # Pearson vs Spearman
#
# - **Pearson** (default) — linear correlation.
# - **Spearman** — rank correlation, robust to non-linear monotonic relationships and outliers.


# %% color=amber title="print('Pearson:')"
# @explain: Run this cell to see the output.
print("Pearson:")
print(cars[["mpg","weight","horsepower"]].corr(method="pearson").round(2))
print("\nSpearman (rank):")
print(cars[["mpg","weight","horsepower"]].corr(method="spearman").round(2))


# %% [markdown] color=rose title="4. Group-by analysis"
# # 4. Group-by analysis
#


# %% color=lime title="Average mpg per origin"
# @explain: Average mpg per origin
# @explain: Multiple aggs at once
# Average mpg per origin
g = cars.groupby("origin", observed=True)["mpg"].agg(["mean","median","std","count"])
print(g.round(2))

# Multiple aggs at once
print(cars.groupby("cylinders").agg(
    avg_mpg=("mpg","mean"),
    avg_weight=("weight","mean"),
    n=("mpg","count"),
).round(1))


# %% [markdown] color=teal title="5. Pivot tables — group-by on two dimensions"
# # 5. Pivot tables — group-by on two dimensions
#


# %% color=sky title="pivot = cars.pivot_table(values='mpg'"
# @explain: Run this cell to see the output.
pivot = cars.pivot_table(values="mpg", index="origin", columns="cylinders",
                          aggfunc="mean", observed=True)
print(pivot.round(1))

sns.heatmap(pivot, annot=True, fmt=".1f", cmap="YlGnBu")
plt.title("Average mpg by origin × cylinders"); plt.show()


# %% [markdown] color=mint title="6. Pair plot / scatter matrix — see all pairs at once"
# # 6. Pair plot / scatter matrix — see all pairs at once
#
# A grid of scatterplots, one per pair of numeric columns; histograms on the diagonal. Best for small numbers of variables (<8).


# %% color=peach title="sns.pairplot(cars[['mpg','weight','horsepower','acce…"
# @explain: Run this cell to see the output.
sns.pairplot(cars[["mpg","weight","horsepower","acceleration","origin"]],
             hue="origin", corner=True, plot_kws={"alpha":.5})
plt.show()


# %% [markdown] color=violet title="7. Putting it together — the EDA report"
# # 7. Putting it together — the EDA report
#
# After running the above, three takeaways for the auto-mpg dataset:
#
# 1. **Distribution of mpg** is roughly bell-shaped, mean ≈ 23, range 9–47.
# 2. **Strongest predictors** of mpg are `weight` (r ≈ -0.83) and `horsepower` (r ≈ -0.78). Both negative — heavier and more powerful → worse mpg.
# 3. **Origin matters**: Japanese cars cluster around 30 mpg, USA around 20. Worth keeping `origin` as a feature.
#
# …


# %% [markdown] color=amber title="8. Practice"
# # 8. Practice
#
# 1. Plot the distribution of `mpg` split by `origin` (overlay or facet).
# 2. Compute the correlation between `mpg` and each numeric feature, sorted from strongest to weakest negative.
# 3. Build a pivot table of `mean horsepower` by `origin` × decade (use `(model_year//10)*10`).
# 4. Use `pairplot` on just `["mpg","weight","horsepower","acceleration"]`. Which pair has the cleanest relationship?


# %% color=rose title="1)"
# @explain: 1)
# @explain: 2)
# @explain: 3)
# @explain: 4)
# 1)
sns.kdeplot(data=cars, x="mpg", hue="origin", fill=True, alpha=.4)
plt.title("mpg by origin"); plt.show()

# 2)
print(cars.select_dtypes("number").corrwith(cars["mpg"]).sort_values())

# 3)
cars["decade"] = (cars["model_year"] // 10) * 10
print(cars.pivot_table(values="horsepower", index="origin", columns="decade",
                       aggfunc="mean", observed=True).round(1))

# 4)
sns.pairplot(cars[["mpg","weight","horsepower","acceleration"]], corner=True,
             plot_kws={"alpha":.5}); plt.show()


# %% [markdown] color=lime title="Recap"
# # Recap
#
# ✅ Univariate look at every column
# ✅ Bivariate by data-type pairs (num/num, cat/num, cat/cat)
# ✅ Pearson + Spearman correlations and the heatmap view
# ✅ Group-by + pivot table for two-dimensional summaries
# ✅ Pair plot for the all-pairs view
#
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


