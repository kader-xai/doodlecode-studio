# %% [markdown]
# # Module 5 — Pandas for Machine Learning
# Tabular data is 90% of real-world ML. Pandas is the toolbox for
# loading, cleaning, transforming, and joining it.

# %% kind=install color=rose title="Install Pandas"
# @explain: Run once. pandas pulls in NumPy automatically.
import importlib, subprocess, sys
if importlib.util.find_spec("pandas") is None:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "pandas"])
print("pandas ready.")


# %% kind=import color=sky title="Imports"
import numpy as np
import pandas as pd
pd.set_option("display.width", 100)
pd.set_option("display.max_columns", 20)


# %% kind=intro color=sky title="Two main objects: Series & DataFrame"
# @explain: Series = 1D labelled array (one column). DataFrame = 2D
# @explain: labelled table (rows × columns). Both share the same index.
# @tags: intro


# %% kind=assign color=peach title="Building a DataFrame"
# @explain: From a dict, lists, or numpy arrays. Column names come from
# @explain: the dict keys; the index defaults to 0..N-1.
df = pd.DataFrame({
    "name": ["Ada", "Linus", "Grace", "Yusuf"],
    "age":  [27, 41, 30, 35],
    "city": ["London", "Helsinki", "NY", "Berlin"],
    "score":[0.91, 0.84, 0.88, 0.79],
})
print(df)


# %% kind=expr color=peach title="Inspecting a frame"
# @explain: .head/.tail show top/bottom rows. .info shows dtypes + nulls.
# @explain: .describe gives a numeric summary — the first thing you run
# @explain: on any new dataset.
print(df.head(2))
print()
print(df.info())
print()
print(df.describe())


# %% kind=expr color=peach title="Selecting columns and rows"
# @explain: df['col'] returns a Series. df[['a','b']] returns a frame.
# @explain: .loc uses LABELS, .iloc uses INTEGER positions.
print("series :", df["name"].tolist())
print()
print("two cols:\n", df[["name", "score"]])
print()
print("row 0   :", df.iloc[0].to_dict())
print()
print("by label:", df.loc[2, "city"])


# %% kind=expr color=peach title="Filtering with boolean masks"
# @explain: Same idea as NumPy — build a mask, index by it. Combine
# @explain: with & / | (parens required). isin filters to a list.
print(df[df["age"] > 30])
print()
print(df[(df["score"] >= 0.85) & (df["age"] < 40)])
print()
print(df[df["city"].isin(["NY", "Berlin"])])


# %% kind=assign color=peach title="New columns and computed features"
# @explain: Assigning a new column name creates it. Use vectorised ops
# @explain: on existing columns — never iterate row by row.
df["age_group"] = pd.cut(df["age"], bins=[0, 30, 40, 100],
                         labels=["young", "mid", "senior"])
df["score_pct"] = (df["score"] * 100).round(1)
print(df)


# %% [markdown]
# ## Loading and saving data


# %% kind=function color=mint title="read_csv / to_csv"
# @explain: read_csv is the workhorse for tabular data. We round-trip
# @explain: to a temp file so the example runs in any kernel.
import io
csv_text = "id,name,age,score\n1,Ada,27,0.91\n2,Linus,41,0.84\n3,Grace,30,0.88\n"
loaded = pd.read_csv(io.StringIO(csv_text))
print(loaded)


# %% [markdown]
# ## Missing data — the silent killer
# Real datasets have NaNs (Not-a-Number / missing). Pandas tracks them
# automatically and offers a few strategies to handle them.


# %% kind=assign color=peach title="Detecting and dropping"
# @explain: .isna() returns a boolean frame. .dropna() removes rows with
# @explain: ANY NaN by default — be careful with very sparse data.
mess = pd.DataFrame({
    "a": [1, np.nan, 3, 4],
    "b": [10, 20, np.nan, 40],
    "c": ["x", "y", "z", np.nan],
})
print(mess)
print()
print("any NaN:\n", mess.isna())
print()
print("dropna:\n", mess.dropna())


# %% kind=function color=mint title="Filling missing values (imputation)"
# @explain: fillna with the column mean (numeric) or the mode (string)
# @explain: is a simple, fast baseline. Tree models tolerate NaNs;
# @explain: linear models / NNs usually don't.
imputed = mess.copy()
imputed["a"] = imputed["a"].fillna(imputed["a"].mean())
imputed["b"] = imputed["b"].fillna(imputed["b"].mean())
imputed["c"] = imputed["c"].fillna("unknown")
print(imputed)


# %% [markdown]
# ## groupby — the split-apply-combine pattern


# %% kind=function color=mint title="Aggregating by group"
# @explain: groupby splits rows by a column's values, applies an
# @explain: aggregation, then combines back into a frame.
sales = pd.DataFrame({
    "city":  ["NY", "NY", "LA", "LA", "Berlin"],
    "month": ["Jan", "Feb", "Jan", "Feb", "Jan"],
    "rev":   [100, 120, 80, 95, 60],
})
print(sales.groupby("city")["rev"].sum())
print()
print(sales.groupby("city").agg(total=("rev", "sum"),
                                  avg=("rev", "mean"),
                                  n=("rev", "size")))


# %% kind=function color=mint title="value_counts — distribution at a glance"
# @explain: One of the most useful methods in EDA. Tells you the class
# @explain: balance of any categorical column.
labels = pd.Series(["spam", "spam", "ham", "ham", "ham", "spam", "ham"])
print(labels.value_counts())
print(labels.value_counts(normalize=True))


# %% [markdown]
# ## Merging tables — joining datasets together


# %% kind=function color=mint title="Inner / left / right joins"
# @explain: pd.merge joins two frames on a key column. how='inner'
# @explain: keeps only matching rows; 'left' keeps every row from the
# @explain: left side and fills missing right side with NaN.
people = pd.DataFrame({"id": [1, 2, 3], "name": ["Ada", "Linus", "Grace"]})
scores = pd.DataFrame({"id": [1, 2, 4], "score": [0.91, 0.84, 0.55]})
print(pd.merge(people, scores, on="id", how="inner"))
print()
print(pd.merge(people, scores, on="id", how="left"))


# %% [markdown]
# ## Pivot tables and cross-tabs


# %% kind=function color=mint title="pivot_table"
# @explain: Reshape long data to wide. Indices become rows, columns
# @explain: become columns, values get aggregated. Excel pivot tables
# @explain: are a special case.
long = pd.DataFrame({
    "city":  ["NY", "NY", "LA", "LA"],
    "month": ["Jan", "Feb", "Jan", "Feb"],
    "rev":   [100, 120, 80, 95],
})
wide = long.pivot_table(index="city", columns="month", values="rev")
print(wide)


# %% [markdown]
# ## Plug-and-play with NumPy and scikit-learn


# %% kind=function color=mint title="DataFrame to NumPy array"
# @explain: Most ML models take NumPy arrays. .values or .to_numpy()
# @explain: extracts the underlying matrix.
features = pd.DataFrame({
    "x1": [1, 2, 3, 4],
    "x2": [10, 20, 30, 40],
})
labels = pd.Series([0, 1, 0, 1])
X = features.to_numpy()
y = labels.to_numpy()
print("X shape:", X.shape, "dtype:", X.dtype)
print("y      :", y)


# %% [markdown]
# ## Practice
# 1. Compute the average score per city in the `df` from the top.
# 2. Build a 4-row frame and add a column "rank" using `.rank()`.
# 3. Read this string as CSV and group by category, summing values:
#    `"category,value\nA,5\nB,3\nA,2\nC,7\nB,1\n"`


# %% kind=function color=mint title="Practice 1 — avg score per city"
# @explain: groupby + .mean() is the classic two-liner.
result = df.groupby("city")["score"].mean().sort_values(ascending=False)
print(result)


# %% kind=function color=mint title="Practice 2 — rank a column"
# @explain: .rank assigns 1.0 to the smallest value by default. method
# @explain: controls tie-breaking.
small = pd.DataFrame({"name": list("ABCD"), "score": [40, 95, 70, 70]})
small["rank"] = small["score"].rank(method="dense", ascending=False)
print(small)


# %% kind=function color=mint title="Practice 3 — group-sum from CSV"
# @explain: io.StringIO turns a string into something read_csv can parse.
import io
text = "category,value\nA,5\nB,3\nA,2\nC,7\nB,1\n"
g = pd.read_csv(io.StringIO(text)).groupby("category")["value"].sum()
print(g)


# %% [markdown]
# ## Recap
# - ✅ Series and DataFrame
# - ✅ Selection, filtering, computed columns
# - ✅ Missing-data handling
# - ✅ groupby + agg + value_counts
# - ✅ Merge, pivot, conversion to numpy
#
# **Next:** Module 6 — Data Visualization.
