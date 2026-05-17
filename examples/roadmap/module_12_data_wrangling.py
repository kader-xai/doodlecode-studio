# doodlecode format-version: 2
# Auto-converted from module_12_data_wrangling.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 12 Data Wrangling"
# # Module 12 Data Wrangling
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 12 — Data Wrangling"
# # Module 12 — Data Wrangling
#
# *IBM Data Analysis · Module 2 of 6 (Module 12 of 16)*
#
# Wrangling = **fixing what's broken** so the analysis or model can run. It's unglamorous and usually >50% of the work in any project.
#
# For each column, ask:
# 1. Right **type**?
# 2. Any **missing** values?
# …


# %% color=mint title="!pip -q install pandas numpy scikit-learn…"
# @explain: Run this cell to see the output.
!pip -q install pandas numpy scikit-learn matplotlib seaborn
import pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns

url  = "https://archive.ics.uci.edu/ml/machine-learning-databases/auto-mpg/auto-mpg.data"
cols = ["mpg","cylinders","displacement","horsepower","weight",
        "acceleration","model_year","origin","car_name"]
cars = pd.read_csv(url, sep=r"\s+", names=cols, na_values="?")
cars.head()


# %% [markdown] color=peach title="1. Missing values — find, then decide"
# # 1. Missing values — find, then decide
#
# Three strategies:
#
# | Strategy | When |
# |---|---|
# | **Drop rows** with NaN | few missing, lots of data |
# | **Drop the column** | column is mostly empty |
# …


# %% color=violet title="Detect"
# @explain: Detect
# Detect
print(cars.isna().sum())
print("\nany missing?", cars.isna().any().any())
print("rows with any NaN:", cars.isna().any(axis=1).sum())


# %% color=amber title="Strategy 1"
# @explain: Strategy 1 — drop rows
# @explain: Strategy 2 — drop a column
# @explain: Strategy 3 — impute (most common)
# Strategy 1 — drop rows
clean1 = cars.dropna()
print("after dropna:", clean1.shape)

# Strategy 2 — drop a column
print(cars.drop(columns="car_name").shape)

# Strategy 3 — impute (most common)
cars["horsepower"] = cars["horsepower"].fillna(cars["horsepower"].median())
print("missing now:", cars.isna().sum().sum())


# %% [markdown] color=rose title="Forward / backward fill (for ordered data like time series)"
# # Forward / backward fill (for ordered data like time series)
#


# %% color=lime title="ts = pd.Series([1"
# @explain: Run this cell to see the output.
ts = pd.Series([1, np.nan, np.nan, 4, np.nan, 6])
print("ffill:", ts.ffill().tolist())
print("bfill:", ts.bfill().tolist())


# %% [markdown] color=teal title="2. Type fixes"
# # 2. Type fixes
#
# Two big ones:
# 1. **Numbers stuck as strings** — fix with `pd.to_numeric` or `astype`.
# 2. **Categories stored as ints** — map to readable labels and convert to `category` dtype (saves memory).


# %% color=sky title="Map origin codes -> country names"
# @explain: Map origin codes -> country names; convert to category
# Map origin codes -> country names; convert to category
cars["origin"] = cars["origin"].map({1:"USA", 2:"Europe", 3:"Japan"}).astype("category")
print(cars["origin"].dtype, cars["origin"].cat.categories)


# %% color=mint title="String cleaning"
# @explain: String cleaning — trim whitespace, lowercase, etc
# String cleaning — trim whitespace, lowercase, etc.
cars["car_name"] = cars["car_name"].str.strip().str.lower()
print(cars["car_name"].head())


# %% [markdown] color=peach title="3. Scaling — normalisation vs standardisation"
# # 3. Scaling — normalisation vs standardisation
#
# Why scale at all? Many ML models (linear regression with regularisation, SVM, kNN, neural nets) treat large numbers as "more important" if features are on different scales. Scaling levels the playing field.
#
# | Method | Formula | Range | When |
# |---|---|---|---|
# | **Min-max (normalisation)** | $(x - \min) / (\max - \min)$ | $[0,1]$ | bounded; sensitive to outliers |
# | **Z-score (standardisation)** | $(x - \mu) / \sigma$ | mean 0, std 1 | works with normal-ish data; preferred default |


# %% color=violet title="from sklearn.preprocessing import MinMaxScaler"
# @explain: Run this cell to see the output.
from sklearn.preprocessing import MinMaxScaler, StandardScaler

cars["weight_minmax"] = MinMaxScaler().fit_transform(cars[["weight"]])
cars["weight_std"]    = StandardScaler().fit_transform(cars[["weight"]])
print(cars[["weight","weight_minmax","weight_std"]].describe().T[["min","max","mean","std"]])


# %% [markdown] color=amber title="4. Binning — continuous → categorical"
# # 4. Binning — continuous → categorical
#
# Sometimes you want categories like *Low / Medium / High* instead of a continuous number. Pandas has two functions:
#
# | Function | Splits by |
# |---|---|
# | `pd.cut(x, bins=...)` | **value** — fixed cutoffs |
# | `pd.qcut(x, q=...)` | **quantile** — equal-sized buckets |


# %% color=rose title="cars['mpg_bin'] = pd.cut(cars['mpg']"
# @explain: Run this cell to see the output.
cars["mpg_bin"] = pd.cut(cars["mpg"], bins=[0, 18, 26, 50],
                          labels=["Low","Mid","High"])
cars["mpg_quartile"] = pd.qcut(cars["mpg"], q=4, labels=["Q1","Q2","Q3","Q4"])

print(cars[["mpg","mpg_bin","mpg_quartile"]].head(10))
print(cars["mpg_bin"].value_counts())


# %% [markdown] color=lime title="5. One-hot encoding — categorical → numeric"
# # 5. One-hot encoding — categorical → numeric
#
# Most ML algorithms only accept numbers. **One-hot encoding** turns a category column into N binary columns.
#
# Use `drop_first=True` to avoid the "dummy variable trap" (perfect multicollinearity in regression).


# %% color=teal title="encoded = pd.get_dummies(cars[['origin']]"
# @explain: Run this cell to see the output.
encoded = pd.get_dummies(cars[["origin"]], drop_first=True)
print(encoded.head())
print("columns added:", encoded.columns.tolist())


# %% color=sky title="Alternative: scikit-learn's OneHotEncoder"
# @explain: Alternative: scikit-learn's OneHotEncoder (returns a 2D array, used inside Pipelines)
# Alternative: scikit-learn's OneHotEncoder (returns a 2D array, used inside Pipelines)
from sklearn.preprocessing import OneHotEncoder
oh = OneHotEncoder(drop="first", sparse_output=False)
print(oh.fit_transform(cars[["origin"]])[:5])
print(oh.get_feature_names_out())


# %% [markdown] color=mint title="6. Outliers — find them, decide what to do"
# # 6. Outliers — find them, decide what to do
#
# Two common detection rules:
#
# | Rule | Definition |
# |---|---|
# | **IQR rule** | outside $[Q1 - 1.5 \cdot IQR,\ Q3 + 1.5 \cdot IQR]$ |
# | **Z-score rule** | $|z| > 3$ |


# %% color=peach title="Visualise"
# @explain: Visualise
def iqr_outliers(s):
    q1, q3 = s.quantile([.25, .75])
    iqr = q3 - q1
    lo, hi = q1 - 1.5*iqr, q3 + 1.5*iqr
    return s[(s < lo) | (s > hi)]

print("HP outliers (IQR rule):")
print(iqr_outliers(cars["horsepower"]).head())

# Visualise
sns.boxplot(x=cars["horsepower"]); plt.title("horsepower — outliers as dots"); plt.show()


# %% [markdown] color=violet title="7. Feature engineering — make new columns the model loves"
# # 7. Feature engineering — make new columns the model loves
#
# A feature engineered well often beats a fancier model. Three patterns:
#
# 1. **Ratio features** — `weight / horsepower`, `revenue / cost`.
# 2. **Date parts** — extract year/month/day-of-week from a date.
# 3. **Interaction** — multiply two features that should combine non-linearly.


# %% color=amber title="Ratio"
# @explain: Ratio
# @explain: Date parts (synthetic example)
# @explain: Interaction
# Ratio
cars["power_to_weight"] = cars["horsepower"] / cars["weight"]

# Date parts (synthetic example)
dates = pd.date_range("2020-01-01", periods=10)
df = pd.DataFrame({"date": dates})
df["year"]    = df["date"].dt.year
df["month"]   = df["date"].dt.month
df["weekday"] = df["date"].dt.day_name()
print(df)

# Interaction
cars["disp_x_cyl"] = cars["displacement"] * cars["cylinders"]
print(cars[["horsepower","weight","power_to_weight","displacement","cylinders","disp_x_cyl"]].head())


# %% [markdown] color=rose title="8. Pulling it all together with `ColumnTransformer`"
# # 8. Pulling it all together with `ColumnTransformer`
#
# In real projects you don't apply each step manually — you wire them into a **ColumnTransformer** so the same transformations run on train and test data.


# %% color=lime title="from sklearn.compose import ColumnTransformer"
# @explain: Run this cell to see the output.
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

num_features = ["cylinders","displacement","horsepower","weight","acceleration","model_year"]
cat_features = ["origin"]

pre = ColumnTransformer([
    ("num", StandardScaler(), num_features),
    ("cat", OneHotEncoder(drop="first"), cat_features),
])

X = pre.fit_transform(cars)
print("transformed shape:", X.shape)
print("output column names:", pre.get_feature_names_out())


# %% [markdown] color=teal title="9. Practice"
# # 9. Practice
#
# 1. The auto-mpg `horsepower` column had 6 NaN. Re-load the dataset and impute them with the **mean grouped by origin** instead of the global median. (Hint: `groupby('origin')['horsepower'].transform(lambda s: s.fillna(s.mean()))`.)
# 2. Bin `weight` into quartiles and produce a count plot for each.
# 3. Use `pd.get_dummies` to one-hot encode both `origin` and the new `mpg_bin` from section 4.
# 4. Detect outliers in `acceleration` using the z-score rule (|z|>3) and print them.


# %% color=sky title="1)"
# @explain: 1)
# @explain: 2)
# @explain: 3)
# @explain: 4)
# 1)
fresh = pd.read_csv(url, sep=r"\s+", names=cols, na_values="?")
fresh["origin"] = fresh["origin"].map({1:"USA",2:"Europe",3:"Japan"})
fresh["horsepower"] = fresh.groupby("origin")["horsepower"].transform(lambda s: s.fillna(s.mean()))
print("missing now:", fresh["horsepower"].isna().sum())

# 2)
fresh["w_q"] = pd.qcut(fresh["weight"], 4, labels=["Q1","Q2","Q3","Q4"])
sns.countplot(x="w_q", data=fresh); plt.title("weight quartiles"); plt.show()

# 3)
print(pd.get_dummies(cars[["origin","mpg_bin"]], drop_first=True).head())

# 4)
z = (fresh["acceleration"] - fresh["acceleration"].mean()) / fresh["acceleration"].std()
print(fresh.loc[z.abs() > 3, ["car_name","acceleration"]])


# %% [markdown] color=mint title="Recap"
# # Recap
#
# ✅ Detect missing values; pick drop / impute / forward-fill
# ✅ Fix dtypes; clean strings
# ✅ Scale features (min-max or z-score)
# ✅ Bin continuous columns; one-hot encode categoricals
# ✅ Spot outliers with IQR or z-score
# ✅ Engineer ratio, date-part, and interaction features
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


