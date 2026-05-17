# doodlecode format-version: 2
# Auto-converted from module_11_importing_data.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 11 Importing Data"
# # Module 11 Importing Data
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 11 — Importing Data Sets"
# # Module 11 — Importing Data Sets
#
# *IBM Data Analysis with Python · Module 1 of 6 (Module 11 of 16)*
#
# The data analysis track starts here. Every analysis begins the same way: **load the data, look at it, write down what's broken**. This module is about the first two steps.
#
# We'll use a **shared dataset** across modules 11–16: the classic *auto-mpg* dataset (1970s–80s cars: mpg, weight, horsepower, etc.). Every later module reuses it, so the steps connect end-to-end.
#
# ### What you'll cover
# …


# %% color=mint title="!pip -q install pandas numpy openpyxl"
# @explain: Run this cell to see the output.
!pip -q install pandas numpy openpyxl
import pandas as pd, numpy as np


# %% [markdown] color=peach title="1. Where data lives — five sources"
# # 1. Where data lives — five sources
#
# | Source | Tool |
# |---|---|
# | Local CSV | `pd.read_csv(path)` |
# | Excel | `pd.read_excel(path)` |
# | JSON | `pd.read_json(path)` |
# | SQL database | `pd.read_sql(query, conn)` |
# …


# %% [markdown] color=violet title="2. The shared dataset — auto-mpg"
# # 2. The shared dataset — auto-mpg
#


# %% color=amber title="url  =…"
# @explain: Run this cell to see the output.
url  = "https://archive.ics.uci.edu/ml/machine-learning-databases/auto-mpg/auto-mpg.data"
cols = ["mpg","cylinders","displacement","horsepower","weight",
        "acceleration","model_year","origin","car_name"]
cars = pd.read_csv(url, sep=r"\s+", names=cols, na_values="?")
print(cars.shape)
cars.head()


# %% [markdown] color=rose title="`pd.read_csv` — the 10 options worth knowing"
# # `pd.read_csv` — the 10 options worth knowing
#
# | Option | Meaning |
# |---|---|
# | `sep=` | column separator (default `,`; tab is `\t`) |
# | `names=` | provide column names if missing |
# | `header=` | row number of header (default 0; `None` if none) |
# | `na_values=` | extra strings to treat as NaN (`"?"`, `"NA"`, ...) |
# …


# %% color=lime title="Just read 5 rows + selected columns"
# @explain: Just read 5 rows + selected columns — useful for inspecting a huge file
# Just read 5 rows + selected columns — useful for inspecting a huge file
small = pd.read_csv(url, sep=r"\s+", names=cols, na_values="?",
                    usecols=["mpg","weight","horsepower"], nrows=5)
print(small)


# %% [markdown] color=teal title="3. Reading Excel and JSON"
# # 3. Reading Excel and JSON
#


# %% color=sky title="Make and read a small Excel file"
# @explain: Make and read a small Excel file
# Make and read a small Excel file
import pathlib, tempfile
TMP = pathlib.Path(tempfile.gettempdir())
xlsx = TMP / "demo.xlsx"
cars.head(20).to_excel(xlsx, sheet_name="cars", index=False)

back = pd.read_excel(xlsx, sheet_name="cars")
print(back.head())


# %% color=mint title="JSON: one record per dict"
# @explain: JSON: one record per dict (records orient is the most natural)
# JSON: one record per dict (records orient is the most natural)
jpath = TMP / "cars.json"
cars.head(5).to_json(jpath, orient="records", indent=2)
print(jpath.read_text()[:300])
print(pd.read_json(jpath, orient="records"))


# %% [markdown] color=peach title="4. Reading from a SQLite database"
# # 4. Reading from a SQLite database
#
# Most production data lives in databases. The pattern: open a connection, hand a query to `pd.read_sql`.


# %% color=violet title="Now query it back like SQL"
# @explain: Now query it back like SQL
import sqlite3
db = TMP / "cars.db"
con = sqlite3.connect(db)
cars.to_sql("cars", con, if_exists="replace", index=False)

# Now query it back like SQL
q = """SELECT origin, AVG(mpg) AS avg_mpg, COUNT(*) AS n
       FROM cars
       GROUP BY origin
       ORDER BY avg_mpg DESC"""
result = pd.read_sql(q, con)
print(result)
con.close()


# %% [markdown] color=amber title="5. The first-inspection toolkit"
# # 5. The first-inspection toolkit
#
# Five lines you should run on **every** new dataset, in order. Each answers one specific question.


# %% color=rose title="print('shape:'"
# @explain: Run this cell to see the output.
print("shape:", cars.shape)            # how big?


# %% color=lime title="cars.head()                          # what does a…"
# @explain: Run this cell to see the output.
cars.head()                          # what does a row look like?


# %% color=teal title="cars.dtypes                          # are types right?"
# @explain: Run this cell to see the output.
cars.dtypes                          # are types right?


# %% color=sky title="cars.info()                          # how many…"
# @explain: Run this cell to see the output.
cars.info()                          # how many missing per column?


# %% color=mint title="cars.describe(include='all').T       # what are the…"
# @explain: Run this cell to see the output.
cars.describe(include="all").T       # what are the ranges + categories?


# %% [markdown] color=peach title="6. Features vs target — naming what you have"
# # 6. Features vs target — naming what you have
#
# In supervised learning, columns split into:
# - **Target** (a.k.a. label, dependent variable, `y`) — the thing you want to predict.
# - **Features** (a.k.a. independent variables, `X`) — everything you'll use to predict it.
#
# For auto-mpg the target is **mpg** (we want to predict fuel efficiency). Everything else is a candidate feature.


# %% color=violet title="Make this explicit"
# @explain: Make this explicit — it carries through the next 5 modules
# Make this explicit — it carries through the next 5 modules
target   = "mpg"
features = ["cylinders","displacement","horsepower","weight","acceleration","model_year","origin"]

print("target  :", target)
print("features:", features)
print("rows×cols of X:", cars[features].shape, "  y:", cars[target].shape)


# %% [markdown] color=amber title="7. Practice"
# # 7. Practice
#
# 1. Use `pd.read_csv` to load the famous Iris dataset from
#    `https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data` (no header). Use the column names `["sepal_len","sepal_wid","petal_len","petal_wid","class"]`. Print the shape and the first 5 rows.
# 2. Save your auto-mpg cars dataframe to a SQLite db, then write a SQL query that returns the **5 most-fuel-efficient cars** by `mpg`.
# 3. Read just the columns `["mpg","horsepower","weight"]` from the auto-mpg URL with `usecols=`. Then print the row with the highest `weight`.


# %% color=rose title="1)"
# @explain: 1)
# @explain: 2)
# @explain: 3)
# 1)
iris = pd.read_csv(
    "https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data",
    header=None, names=["sepal_len","sepal_wid","petal_len","petal_wid","class"])
print(iris.shape); print(iris.head())

# 2)
import sqlite3, tempfile, pathlib
db = pathlib.Path(tempfile.gettempdir()) / "cars2.db"
con = sqlite3.connect(db); cars.to_sql("cars", con, if_exists="replace", index=False)
print(pd.read_sql("SELECT car_name, mpg FROM cars ORDER BY mpg DESC LIMIT 5", con))
con.close()

# 3)
small = pd.read_csv(url, sep=r"\s+", names=cols, na_values="?",
                    usecols=["mpg","horsepower","weight"])
print(small.iloc[small["weight"].idxmax()])


# %% [markdown] color=lime title="Recap"
# # Recap
#
# ✅ Load CSV, Excel, JSON, SQL — same `read_*` family
# ✅ Use `pd.read_csv`'s 10 options (sep, names, na_values, dtype, parse_dates, index_col, usecols, nrows, chunksize, header)
# ✅ Run the 5-line first-inspection ritual on any new dataset
# ✅ Name what's the target and what are the features
#
# ### Next
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


