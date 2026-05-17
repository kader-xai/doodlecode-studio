# doodlecode format-version: 2
# Auto-converted from module_04_working_with_data.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 04 Working With Data"
# # Module 04 Working With Data
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 4 — Working with Data"
# # Module 4 — Working with Data
#
# *IBM Python for Data Science · Module 4 of 16*
#
# This is the module where Python turns into a **data-science** language. You'll move from variables in memory to **datasets on disk**, learn the two libraries that 90% of analysis runs on (`numpy`, `pandas`), and finish with your first plot.
#
# ### What you'll cover
# 1. File I/O — reading and writing text, with the `with` statement
# 2. CSV — `csv` module + the pandas one-liner
# …


# %% color=mint title="!pip -q install pandas numpy matplotlib"
# @explain: Run this cell to see the output.
!pip -q install pandas numpy matplotlib


# %% [markdown] color=peach title="1. File I/O — the `with` statement"
# # 1. File I/O — the `with` statement
#
# Always open files using `with`. It guarantees the file is closed even if an error happens.


# %% color=violet title="Write a text file"
# @explain: Write a text file
# @explain: Read it back — three patterns
import os, tempfile, pathlib
TMP = pathlib.Path(tempfile.gettempdir())

# Write a text file
path = TMP / "notes.txt"
with open(path, "w") as f:
    f.write("line 1\n")
    f.writelines(["line 2\n", "line 3\n"])

# Read it back — three patterns
with open(path) as f:
    text = f.read()                  # whole file as one string
print("--- read() ---"); print(text)

with open(path) as f:
    lines = f.readlines()            # list of lines (with trailing \n)
print("--- readlines() ---", lines)

with open(path) as f:
    for line in f:                   # the memory-friendly pattern
        print("line:", line.rstrip())


# %% [markdown] color=amber title="Append vs overwrite"
# # Append vs overwrite
#


# %% color=rose title="'w' overwrites; 'a' appends; 'r' is read"
# @explain: 'w' overwrites; 'a' appends; 'r' is read (default)
# 'w' overwrites; 'a' appends; 'r' is read (default)
with open(path, "a") as f:
    f.write("line 4 (appended)\n")

print(path.read_text())


# %% [markdown] color=lime title="2. CSV — comma-separated values"
# # 2. CSV — comma-separated values
#
# Two ways: the **stdlib `csv` module** for total control, or **pandas** for the one-liner.


# %% color=teal title="Write with csv module"
# @explain: Write with csv module
# @explain: Read with csv.DictReader — each row = dict keyed by column
import csv

people_csv = TMP / "people.csv"

# Write with csv module
rows = [["name","age","city"],
        ["Ada", 36, "London"],
        ["Linus", 54, "Helsinki"],
        ["Grace", 85, "New York"]]
with open(people_csv, "w", newline="") as f:
    csv.writer(f).writerows(rows)

# Read with csv.DictReader — each row = dict keyed by column
with open(people_csv) as f:
    for row in csv.DictReader(f):
        print(row)


# %% color=sky title="The pandas one-liner"
# @explain: The pandas one-liner
# The pandas one-liner
import pandas as pd
df = pd.read_csv(people_csv)
print(df)


# %% [markdown] color=mint title="3. JSON — JavaScript Object Notation"
# # 3. JSON — JavaScript Object Notation
#
# JSON is the lingua-franca of APIs. It maps cleanly to Python:
# - object `{}` ↔ `dict`
# - array `[]` ↔ `list`
# - string/number/true/false/null ↔ Python equivalents
#
# Two functions to remember: `json.dumps` (Python → string) / `json.loads` (string → Python). With files: `json.dump` / `json.load`.


# %% color=peach title="Python -> string"
# @explain: Python -> string (and back)
# @explain: To a file
# @explain: From a file
import json

data = {
    "user": "Kader",
    "active": True,
    "scores": [85, 92, 78],
    "address": {"city": "Riyadh", "country": "Saudi Arabia"}
}

# Python -> string (and back)
s = json.dumps(data, indent=2)
print(s)
print("--- parsed back ---")
print(json.loads(s)["address"]["city"])

# To a file
jpath = TMP / "user.json"
jpath.write_text(json.dumps(data, indent=2))

# From a file
loaded = json.loads(jpath.read_text())
print(loaded["scores"])


# %% [markdown] color=violet title="4. NumPy — the engine under everything"
# # 4. NumPy — the engine under everything
#
# A NumPy `ndarray` is a **fixed-size, typed, n-dimensional array** stored in contiguous memory. Operations on arrays run in C, so they're 10–100× faster than equivalent Python loops.
#
# Three reasons to learn NumPy first:
# 1. Pandas is built on top of it.
# 2. Vectorised code is shorter *and* faster than loop code.
# 3. Every ML library expects array-shaped inputs.


# %% color=amber title="1D array"
# @explain: 1D array
# @explain: Useful constructors
import numpy as np

# 1D array
a = np.array([1, 2, 3, 4, 5])
print(a, a.dtype, a.shape, a.ndim)

# Useful constructors
print(np.zeros(5))                  # array of zeros
print(np.ones((2, 3)))              # 2x3 of ones
print(np.arange(0, 10, 2))          # like range, returns ndarray
print(np.linspace(0, 1, 5))         # 5 evenly spaced points 0..1
print(np.eye(3))                    # identity matrix
print(np.random.default_rng(0).normal(0, 1, 5))   # 5 random normals


# %% [markdown] color=rose title="Vector arithmetic — element-wise, no loops"
# # Vector arithmetic — element-wise, no loops
#


# %% color=lime title="Aggregations"
# @explain: Aggregations
a = np.array([1, 2, 3, 4, 5])
b = np.array([10, 20, 30, 40, 50])

print(a + b)        # element-wise add
print(a * b)        # element-wise multiply
print(a ** 2)       # element-wise square
print(a + 100)      # broadcasting — scalar onto array
print(a @ b)        # dot product (sum of element-wise products)

# Aggregations
print("sum:",  a.sum(),  "mean:", a.mean(),
      "std:", a.std(), "max:", a.max(), "argmax:", a.argmax())


# %% [markdown] color=teal title="2D arrays — matrices"
# # 2D arrays — matrices
#


# %% color=sky title="Linear algebra"
# @explain: Linear algebra
M = np.array([[1, 2, 3],
              [4, 5, 6],
              [7, 8, 9]])
print(M.shape)             # (3, 3)
print(M[0])                # first row
print(M[:, 1])             # second column
print(M[1:, 1:])            # bottom-right 2x2

print("transpose:")
print(M.T)
print("sum of each column:", M.sum(axis=0))   # axis=0 → down columns
print("sum of each row   :", M.sum(axis=1))   # axis=1 → across rows

# Linear algebra
A = np.array([[1, 2], [3, 4]])
print("inverse:")
print(np.linalg.inv(A))
print("det:", np.linalg.det(A))
print("eigenvalues:", np.linalg.eigvals(A))


# %% [markdown] color=mint title="Broadcasting — the trick that makes NumPy elegant"
# # Broadcasting — the trick that makes NumPy elegant
#
# Smaller arrays are stretched to match larger ones, when shapes line up. No copies.


# %% color=peach title="Subtract the mean of each column from each row"
# @explain: Subtract the mean of each column from each row — one line
# Subtract the mean of each column from each row — one line
data = np.array([[10, 20, 30],
                 [40, 50, 60],
                 [70, 80, 90]], dtype=float)

centered = data - data.mean(axis=0)     # mean has shape (3,) — broadcasts onto (3,3)
print(centered)
print("each column now sums to ~0:", centered.sum(axis=0))


# %% [markdown] color=violet title="Boolean indexing — filter without a loop"
# # Boolean indexing — filter without a loop
#


# %% color=amber title="a = np.array([3"
# @explain: Run this cell to see the output.
a = np.array([3, 1, 4, 1, 5, 9, 2, 6, 5, 3])
mask = a > 3
print(mask)
print(a[mask])              # keep only values > 3
print(a[(a > 2) & (a < 6)]) # AND — note the parens, & not and


# %% [markdown] color=rose title="5. Pandas Series — the labelled array"
# # 5. Pandas Series — the labelled array
#
# A `Series` is **a 1D array with an index**. Think of it as one column of a spreadsheet, where each row has a label.


# %% color=lime title="import pandas as pd"
# @explain: Run this cell to see the output.
import pandas as pd

s = pd.Series([85, 92, 78], index=["Ada", "Linus", "Grace"], name="score")
print(s)
print(s["Linus"])           # label-based lookup
print(s.iloc[0])             # positional
print(s[s > 80])             # boolean filter
print(s.mean(), s.max(), s.idxmax())


# %% [markdown] color=teal title="6. Pandas DataFrame — the spreadsheet you can program against"
# # 6. Pandas DataFrame — the spreadsheet you can program against
#
# A `DataFrame` is a 2D table — rows × columns, each column is a Series. It's the centre of gravity of Python data work.


# %% color=sky title="From a dict of lists"
# @explain: From a dict of lists
import pandas as pd

# From a dict of lists
df = pd.DataFrame({
    "name":  ["Ada", "Linus", "Grace", "Guido", "Yukihiro"],
    "lang":  ["Math", "C",    "COBOL", "Python","Ruby"],
    "year":  [1815,  1969,    1906,    1956,    1965],
    "score": [85,    92,      78,      95,      88],
})
print(df)
print(df.dtypes)


# %% [markdown] color=mint title="First-look toolkit — five lines that prevent five hours of confusion"
# # First-look toolkit — five lines that prevent five hours of confusion
#


# %% color=peach title="print(df.shape)        #"
# @explain: Run this cell to see the output.
print(df.shape)        # (rows, cols)
print(df.head(2))      # first 2 rows
print(df.tail(2))      # last 2
df.info()              # types and missing-count
print(df.describe())   # stats for numeric columns


# %% [markdown] color=violet title="Selecting data — three patterns to memorise"
# # Selecting data — three patterns to memorise
#


# %% color=amber title="1) Column(s)"
# @explain: 1) Column(s)
# @explain: 2) Rows by label  (.loc)  vs by position  (.iloc)
# @explain: 3) Boolean filter
# @explain: Combining: rows + columns with .loc
# 1) Column(s)
print(df["name"])              # Series
print(df[["name", "score"]])   # DataFrame (note the double brackets)

# 2) Rows by label  (.loc)  vs by position  (.iloc)
print(df.loc[0])               # row at LABEL 0
print(df.iloc[1:3])            # positional slice rows 1..2

# 3) Boolean filter
print(df[df["score"] >= 90])
print(df[(df["score"] >= 80) & (df["year"] > 1950)])

# Combining: rows + columns with .loc
print(df.loc[df["score"] >= 90, ["name", "lang"]])


# %% [markdown] color=rose title="Mutating a DataFrame"
# # Mutating a DataFrame
#


# %% color=lime title="Add a column"
# @explain: Add a column (computed from existing ones)
# @explain: Rename
# @explain: Sort
# @explain: Drop a row or column (returns a NEW df by default)
# Add a column (computed from existing ones)
df["decade"] = (df["year"] // 10) * 10

# Rename
df = df.rename(columns={"lang": "language"})

# Sort
df_sorted = df.sort_values("score", ascending=False)
print(df_sorted)

# Drop a row or column (returns a NEW df by default)
print(df.drop(columns=["decade"]))


# %% [markdown] color=teal title="Save back to disk"
# # Save back to disk
#


# %% color=sky title="out = TMP / 'people_out.csv'"
# @explain: Run this cell to see the output.
out = TMP / "people_out.csv"
df.to_csv(out, index=False)
df.to_json(TMP / "people_out.json", orient="records", indent=2)
print(out.read_text()[:200])


# %% [markdown] color=mint title="7. Group-by — split, apply, combine"
# # 7. Group-by — split, apply, combine
#
# The single most-used tool in data work. Pattern:
#
# 1. **Split** the rows into groups by some column.
# 2. **Apply** a function to each group (mean, count, custom fn).
# 3. **Combine** the results into a new DataFrame.


# %% color=peach title="Multiple aggregations"
# @explain: Multiple aggregations
# @explain: Two-level grouping
sales = pd.DataFrame({
    "store":   ["A","A","B","B","A","B","A","B"],
    "product": ["x","y","x","y","x","x","y","y"],
    "qty":     [10, 5, 7, 3, 12, 8, 4, 6],
    "price":   [2.0,1.5,2.0,1.5,2.0,2.0,1.5,1.5],
})
sales["revenue"] = sales["qty"] * sales["price"]

print(sales.groupby("store")["revenue"].sum())

# Multiple aggregations
print(sales.groupby("store").agg(
    total_qty=("qty", "sum"),
    avg_qty=("qty", "mean"),
    n_orders=("qty", "count"),
))

# Two-level grouping
print(sales.groupby(["store", "product"])["revenue"].sum())


# %% [markdown] color=violet title="8. Joining DataFrames — `merge`"
# # 8. Joining DataFrames — `merge`
#
# When data lives across two tables (think two CSVs, or two SQL tables), `merge` joins them on a shared key — the same way a SQL JOIN works.


# %% color=amber title="inner"
# @explain: inner — only rows that match on both sides
# @explain: left — keep all customers; orders that match come along
# @explain: outer — keep everything from both
customers = pd.DataFrame({"cust_id":[1,2,3], "name":["Ada","Linus","Grace"]})
orders    = pd.DataFrame({"order_id":[10,11,12,13],
                          "cust_id":[1,1,2,99],
                          "amount":[20,30,15,40]})

# inner — only rows that match on both sides
print(pd.merge(customers, orders, on="cust_id"))

# left — keep all customers; orders that match come along
print(pd.merge(customers, orders, on="cust_id", how="left"))

# outer — keep everything from both
print(pd.merge(customers, orders, on="cust_id", how="outer"))


# %% [markdown] color=rose title="9. Quick visualization — a preview"
# # 9. Quick visualization — a preview
#
# Pandas plots are matplotlib under the hood. One-liners get you 80% of the way to a chart.


# %% color=lime title="Bar chart of revenue by store"
# @explain: Bar chart of revenue by store
# @explain: Histogram of qty
# @explain: Scatter
import matplotlib.pyplot as plt

# Bar chart of revenue by store
sales.groupby("store")["revenue"].sum().plot.bar(title="Revenue by store")
plt.show()

# Histogram of qty
sales["qty"].plot.hist(bins=10, title="Distribution of quantity")
plt.show()

# Scatter
sales.plot.scatter(x="qty", y="revenue", title="qty vs revenue")
plt.show()


# %% [markdown] color=teal title="10. Practice — try before you peek"
# # 10. Practice — try before you peek
#
# 1. Read `people_out.csv` you just wrote. Print the rows where score ≥ 85, sorted by year, oldest first.
# 2. From the `sales` table, compute the **average revenue per product** (across stores).
# 3. Build a NumPy 5×5 matrix of random integers 0..99, then print: (a) its mean per column, (b) all values greater than 50, (c) the matrix with each row standardised to mean 0.
# 4. Given two dicts `{1:"Ada", 2:"Linus"}` and `{1:90, 2:85, 3:78}`, build a DataFrame keyed by id with columns `name` and `score`, with NaN where missing.


# %% color=sky title="1)"
# @explain: 1)
# @explain: 2)
# @explain: 3)
# @explain: 4)
import pandas as pd, numpy as np

# 1)
df = pd.read_csv(TMP / "people_out.csv")
print(df[df["score"] >= 85].sort_values("year"))

# 2)
print(sales.groupby("product")["revenue"].mean())

# 3)
rng = np.random.default_rng(0)
M = rng.integers(0, 100, (5, 5))
print("matrix:\n", M)
print("col means:", M.mean(axis=0))
print(">50:", M[M > 50])
print("row-centered:\n", M - M.mean(axis=1, keepdims=True))

# 4)
names  = pd.Series({1:"Ada", 2:"Linus"}, name="name")
scores = pd.Series({1:90, 2:85, 3:78}, name="score")
out = pd.concat([names, scores], axis=1)
print(out)


# %% [markdown] color=mint title="Recap — what you can now do"
# # Recap — what you can now do
#
# ✅ Read/write text, CSV, JSON files safely with `with`
# ✅ Use NumPy for vectorised math and matrix algebra
# ✅ Build, inspect, select, filter, mutate, and save Pandas DataFrames
# ✅ Use `.loc` vs `.iloc` correctly
# ✅ Group-by + aggregate to summarise large tables
# ✅ Merge two tables on a key (inner/left/outer)
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


