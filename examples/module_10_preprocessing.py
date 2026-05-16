# %% [markdown]
# # Module 10 — Data Preprocessing
# Raw data is messy. Before any model can learn from it you usually need
# to: handle missing values, encode categoricals, scale numerics, and
# split into train/validation/test sets.

# %% kind=install color=rose title="Install scikit-learn"
import importlib, subprocess, sys
if importlib.util.find_spec("sklearn") is None:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "scikit-learn"])
print("sklearn ready.")


# %% kind=import color=sky title="Imports"
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import (
    StandardScaler, MinMaxScaler, RobustScaler,
    OneHotEncoder, LabelEncoder, OrdinalEncoder,
)
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
np.random.seed(0)


# %% kind=assign color=peach title="A messy toy dataset"
# @explain: Two numeric features with missing values, two categorical
# @explain: features (one ordinal, one nominal), and a binary target.
df = pd.DataFrame({
    "age":     [25, 32, np.nan, 45, 51, 28, np.nan, 60],
    "income":  [40, 55, 70, np.nan, 90, 45, 65, 120],
    "edu":     ["HS", "BS", "MS", "PhD", "BS", "HS", "MS", "PhD"],
    "city":    ["NY", "LA", "NY", "Berlin", "NY", "LA", "Berlin", "LA"],
    "bought":  [0, 1, 1, 1, 1, 0, 1, 1],
})
print(df)


# %% [markdown]
# ## Missing values — imputation


# %% kind=function color=mint title="SimpleImputer (mean / median / most_frequent)"
# @explain: Fit on training data only; reuse the learnt statistic on
# @explain: new data. Median is robust to outliers; mean is faster.
num = df[["age", "income"]]
imp = SimpleImputer(strategy="median")
filled = imp.fit_transform(num)
print(pd.DataFrame(filled, columns=num.columns))
print("learnt medians:", imp.statistics_)


# %% [markdown]
# ## Scaling — putting features on the same range


# %% kind=function color=mint title="StandardScaler — z-score"
# @explain: x' = (x - mean) / std → mean 0, std 1. Required for linear
# @explain: models, SVMs, KNN, neural nets. Trees don't care.
filled_df = pd.DataFrame(filled, columns=["age", "income"])
scaler = StandardScaler()
scaled = scaler.fit_transform(filled_df)
print(pd.DataFrame(scaled, columns=filled_df.columns).round(2))
print("learnt means:", scaler.mean_.round(2))
print("learnt stds :", scaler.scale_.round(2))


# %% kind=function color=mint title="MinMaxScaler and RobustScaler"
# @explain: MinMax → [0, 1]. Use when you need bounded inputs (e.g.
# @explain: neural nets with sigmoid). Robust uses median/IQR — good
# @explain: when outliers would dominate mean/std.
print("MinMax  :\n", MinMaxScaler().fit_transform(filled_df).round(2))
print()
print("Robust  :\n", RobustScaler().fit_transform(filled_df).round(2))


# %% [markdown]
# ## Encoding categoricals


# %% kind=function color=mint title="OrdinalEncoder for ordered categories"
# @explain: 'HS' < 'BS' < 'MS' < 'PhD' is a real ordering — use Ordinal.
# @explain: Trees can use ordinal directly; linear models often can't.
order = [["HS", "BS", "MS", "PhD"]]
enc = OrdinalEncoder(categories=order)
edu_enc = enc.fit_transform(df[["edu"]])
print(pd.DataFrame(edu_enc, columns=["edu_ord"]))


# %% kind=function color=mint title="OneHotEncoder for nominal categories"
# @explain: 'NY', 'LA', 'Berlin' have no order — one-hot creates one
# @explain: binary column per category. drop='first' avoids the
# @explain: dummy-variable trap in linear models.
enc = OneHotEncoder(sparse_output=False, drop="first")
city_enc = enc.fit_transform(df[["city"]])
print(pd.DataFrame(city_enc, columns=enc.get_feature_names_out(["city"])))


# %% kind=function color=mint title="LabelEncoder for the target"
# @explain: For y only — turns class names into 0..K-1 integers. Don't
# @explain: use it on features (it imposes false ordering).
le = LabelEncoder()
y = le.fit_transform(["spam", "ham", "spam", "ham"])
print("encoded:", y)
print("classes:", le.classes_)


# %% [markdown]
# ## Train / validation / test split — the cardinal rule
# Never look at the test set until the very end. Validation is what you
# tune on; test is the final estimate of generalisation.


# %% kind=function color=mint title="train_test_split with stratify"
# @explain: Stratify keeps the class proportions identical in both sets.
# @explain: Critical for imbalanced classification.
X = df[["age", "income", "edu", "city"]]
y = df["bought"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=0, stratify=y
)
print("train shape:", X_train.shape, "labels:", y_train.tolist())
print("test  shape:", X_test.shape,  "labels:", y_test.tolist())


# %% [markdown]
# ## Pipeline — the right way to compose preprocessing


# %% kind=function color=mint title="ColumnTransformer + Pipeline"
# @explain: Different columns need different preprocessing. ColumnTransformer
# @explain: routes numeric columns through scaler, categoricals through
# @explain: encoder, then merges them. Wrap in Pipeline so it's a single
# @explain: fit/predict object.
numeric_features = ["age", "income"]
categorical_features = ["edu", "city"]

num_pipe = Pipeline([
    ("impute", SimpleImputer(strategy="median")),
    ("scale", StandardScaler()),
])
cat_pipe = Pipeline([
    ("impute", SimpleImputer(strategy="most_frequent")),
    ("encode", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
])

preproc = ColumnTransformer([
    ("num", num_pipe, numeric_features),
    ("cat", cat_pipe, categorical_features),
])

X_train_t = preproc.fit_transform(X_train)
X_test_t = preproc.transform(X_test)        # use FIT on test — NEVER refit!
print("processed train:", X_train_t.shape)
print(X_train_t.round(2))


# %% [markdown]
# ## Leakage — the #1 silent killer of ML projects
# Anything you fit on test data leaks information about it back into
# training. Always: fit on train → transform train AND test. ColumnTransformer
# + train_test_split makes this hard to get wrong.


# %% [markdown]
# ## Practice
# 1. Fit StandardScaler on `[1,2,3,4,5]` and transform `[6,7]`. The
#    mean and std come from the training data only.
# 2. One-hot encode `["red","green","blue","red"]` with drop=None and
#    drop="first".


# %% kind=function color=mint title="Practice 1 — fit on train, transform on test"
# @explain: scaler.scale_ and .mean_ are frozen after fit. Calling
# @explain: .transform(test) reuses them.
import numpy as np
scaler = StandardScaler().fit([[1], [2], [3], [4], [5]])
print("mean :", scaler.mean_, "std:", scaler.scale_)
print("test scaled:", scaler.transform([[6], [7]]).ravel())


# %% kind=function color=mint title="Practice 2 — drop=None vs drop='first'"
# @explain: drop='first' removes one category to avoid perfect
# @explain: multicollinearity (it's redundant).
colors = [["red"], ["green"], ["blue"], ["red"]]
print("full     :\n", OneHotEncoder(sparse_output=False).fit_transform(colors))
print()
print("drop first:\n", OneHotEncoder(sparse_output=False, drop="first").fit_transform(colors))


# %% [markdown]
# ## Recap
# - ✅ Imputation (mean / median / most_frequent)
# - ✅ Scaling (Standard / MinMax / Robust)
# - ✅ Encoding (Label / Ordinal / OneHot)
# - ✅ train/val/test split with stratification
# - ✅ ColumnTransformer + Pipeline = leak-free preprocessing
#
# **Next:** Module 11 — scikit-learn basics.
