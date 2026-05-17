# doodlecode format-version: 2
# Auto-converted from module_14_model_development.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 14 Model Development"
# # Module 14 Model Development
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 14 — Model Development (Regression)"
# # Module 14 — Model Development (Regression)
#
# *IBM Data Analysis · Module 4 of 6 (Module 14 of 16)*
#
# You've cleaned and explored the data. Now you **predict** something — your first machine-learning model.
#
# We start with **regression** (predicting a continuous number) because it's the simplest, most-interpretable family. Most business questions ("how much will we sell?", "what should this house list for?") are regression.
#
# ### What you'll cover
# …


# %% color=mint title="Reload the cleaned dataset"
# @explain: Reload the cleaned dataset (M11+M12 setup)
!pip -q install pandas numpy scikit-learn matplotlib seaborn
import pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns

# Reload the cleaned dataset (M11+M12 setup)
url  = "https://archive.ics.uci.edu/ml/machine-learning-databases/auto-mpg/auto-mpg.data"
cols = ["mpg","cylinders","displacement","horsepower","weight",
        "acceleration","model_year","origin","car_name"]
cars = pd.read_csv(url, sep=r"\s+", names=cols, na_values="?")
cars["horsepower"] = cars["horsepower"].fillna(cars["horsepower"].median())
cars["origin"] = cars["origin"].map({1:"USA",2:"Europe",3:"Japan"})
cars.head()


# %% [markdown] color=peach title="1. Simple linear regression — one feature"
# # 1. Simple linear regression — one feature
#
# Equation:
#
# $$\hat{y} = b_0 + b_1 x$$
#
# - $\hat y$ — predicted value
# - $b_0$ — intercept (where the line crosses y-axis)
# …


# %% color=violet title="from sklearn.linear_model import LinearRegression"
# @explain: Run this cell to see the output.
from sklearn.linear_model import LinearRegression

X = cars[["weight"]].values     # shape (n, 1) — sklearn expects 2D for X
y = cars["mpg"].values

model = LinearRegression().fit(X, y)
print(f"intercept (b0): {model.intercept_:.3f}")
print(f"slope     (b1): {model.coef_[0]:.5f}")
print(f"R²            : {model.score(X, y):.3f}")


# %% color=amber title="Plot the data + fitted line"
# @explain: Plot the data + fitted line
# Plot the data + fitted line
xs = np.linspace(cars.weight.min(), cars.weight.max(), 100).reshape(-1, 1)
plt.scatter(cars["weight"], cars["mpg"], alpha=.4)
plt.plot(xs, model.predict(xs), color="red", linewidth=2)
plt.xlabel("weight (lb)"); plt.ylabel("mpg")
plt.title(f"y = {model.intercept_:.1f} + {model.coef_[0]:.5f}·weight (R² = {model.score(X,y):.2f})")
plt.show()


# %% [markdown] color=rose title="2. Train / test split — the cardinal rule"
# # 2. Train / test split — the cardinal rule
#
# You **never** judge a model on the data it was trained on. Always:
# 1. Hold out a random 20% as a **test set**.
# 2. Fit on the 80% **train**.
# 3. Score on the **test**.
#
# Why: a model that memorised the training data would score perfectly on it but fail on new data. Holding out tells you the truth.


# %% color=lime title="from sklearn.model_selection import train_test_split"
# @explain: Run this cell to see the output.
from sklearn.model_selection import train_test_split

X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)
m = LinearRegression().fit(X_tr, y_tr)
print(f"train R²: {m.score(X_tr, y_tr):.3f}")
print(f"test  R²: {m.score(X_te, y_te):.3f}")


# %% [markdown] color=teal title="3. Multiple linear regression"
# # 3. Multiple linear regression
#
# Use more than one feature:
#
# $$\hat{y} = b_0 + b_1 x_1 + b_2 x_2 + \dots + b_p x_p$$
#
# Same algorithm, just more dimensions.


# %% color=sky title="from sklearn.preprocessing import OneHotEncoder"
# @explain: Run this cell to see the output.
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

num_features = ["cylinders","displacement","horsepower","weight","acceleration","model_year"]
cat_features = ["origin"]

X = cars[num_features + cat_features]
y = cars["mpg"].values

pre = ColumnTransformer([
    ("num", "passthrough", num_features),
    ("cat", OneHotEncoder(drop="first"), cat_features),
])

pipe = Pipeline([("pre", pre), ("lr", LinearRegression())])

X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)
pipe.fit(X_tr, y_tr)
print(f"train R²: {pipe.score(X_tr, y_tr):.3f}")
print(f"test  R²: {pipe.score(X_te, y_te):.3f}")


# %% [markdown] color=mint title="Inspect the coefficients"
# # Inspect the coefficients
#
# A coefficient of `-0.006` for `weight` means: holding everything else equal, each extra pound costs **0.006 mpg**. Interpretable models ftw.


# %% color=peach title="lr = pipe.named_steps['lr']"
# @explain: Run this cell to see the output.
lr = pipe.named_steps["lr"]
feature_names = pipe.named_steps["pre"].get_feature_names_out()
coefs = pd.Series(lr.coef_, index=feature_names).sort_values()
print(coefs.round(4))


# %% [markdown] color=violet title="4. Polynomial regression — non-linear via feature expansion"
# # 4. Polynomial regression — non-linear via feature expansion
#
# A linear model can capture curves if you feed it polynomial features ($x, x^2, x^3, \ldots$). It's *still* linear in the parameters; just the features are now powers.


# %% color=amber title="Polynomial of weight only"
# @explain: Polynomial of weight only, degree 2
# @explain: Visualise
from sklearn.preprocessing import PolynomialFeatures

# Polynomial of weight only, degree 2
X1 = cars[["weight"]].values
y  = cars["mpg"].values
Xtr, Xte, ytr, yte = train_test_split(X1, y, test_size=0.2, random_state=42)

poly = Pipeline([("p", PolynomialFeatures(degree=2, include_bias=False)),
                 ("lr", LinearRegression())])
poly.fit(Xtr, ytr)
print(f"poly-2 test R²: {poly.score(Xte, yte):.3f}")

# Visualise
xs = np.linspace(cars.weight.min(), cars.weight.max(), 200).reshape(-1, 1)
plt.scatter(cars.weight, cars.mpg, alpha=.4)
plt.plot(xs, poly.predict(xs), color="red", linewidth=2, label="poly-2 fit")
plt.legend(); plt.title("Polynomial regression — captures curvature"); plt.show()


# %% [markdown] color=rose title="Beware over-fitting with high-degree polynomials"
# # Beware over-fitting with high-degree polynomials
#


# %% color=lime title="fig"
# @explain: Run this cell to see the output.
fig, axes = plt.subplots(1, 4, figsize=(16, 3))
xs = np.linspace(cars.weight.min(), cars.weight.max(), 300).reshape(-1, 1)
for ax, d in zip(axes, [1, 2, 5, 15]):
    p = Pipeline([("p", PolynomialFeatures(degree=d, include_bias=False)),
                  ("lr", LinearRegression())])
    p.fit(Xtr, ytr)
    ax.scatter(cars.weight, cars.mpg, alpha=.3)
    ax.plot(xs, p.predict(xs), color="red")
    ax.set_title(f"degree={d}, test R²={p.score(Xte, yte):.2f}")
plt.tight_layout(); plt.show()


# %% [markdown] color=teal title="5. Pipelines — preprocessing + model in one object"
# # 5. Pipelines — preprocessing + model in one object
#
# Why pipelines: in real projects you'll fit on train, score on test, and deploy. Without a pipeline, your `StandardScaler.fit_transform` would silently leak test-set statistics into training. A pipeline calls `fit` only on train and `transform` on test.


# %% color=sky title="from sklearn.preprocessing import StandardScaler"
# @explain: Run this cell to see the output.
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression

full = Pipeline([
    ("pre", ColumnTransformer([
        ("num", StandardScaler(), num_features),
        ("cat", OneHotEncoder(drop="first"), cat_features),
    ])),
    ("model", LinearRegression()),
])

X = cars[num_features + cat_features]
y = cars["mpg"].values
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)

full.fit(X_tr, y_tr)
print(f"test R²: {full.score(X_te, y_te):.3f}")


# %% [markdown] color=mint title="6. Predicting on new data"
# # 6. Predicting on new data
#


# %% color=peach title="new_car = pd.DataFrame([{"
# @explain: Run this cell to see the output.
new_car = pd.DataFrame([{
    "cylinders": 4, "displacement": 140, "horsepower": 90, "weight": 2500,
    "acceleration": 16, "model_year": 80, "origin": "Japan",
}])
print(f"predicted mpg: {full.predict(new_car)[0]:.1f}")


# %% [markdown] color=violet title="7. Practice"
# # 7. Practice
#
# 1. Fit a simple LR using only `horsepower`. What's the test R²?
# 2. Fit a multiple LR using **all** numeric features (no `origin`). Does R² beat the single-feature version?
# 3. Try a polynomial of `weight` at degrees 1, 2, 3 — print the test R² for each.
# 4. Train a pipeline on 80% of the data and predict the **first 5 rows** of the held-out test set; print actual vs predicted side by side.


# %% color=amber title="1)"
# @explain: 1)
# @explain: 2)
# @explain: 3)
# @explain: 4)
# 1)
X_tr, X_te, y_tr, y_te = train_test_split(cars[["horsepower"]], cars["mpg"], test_size=0.2, random_state=42)
print("hp only:", LinearRegression().fit(X_tr, y_tr).score(X_te, y_te).round(3))

# 2)
X_tr, X_te, y_tr, y_te = train_test_split(cars[num_features], cars["mpg"], test_size=0.2, random_state=42)
print("all numeric:", LinearRegression().fit(X_tr, y_tr).score(X_te, y_te).round(3))

# 3)
X_tr, X_te, y_tr, y_te = train_test_split(cars[["weight"]], cars["mpg"], test_size=0.2, random_state=42)
for d in [1, 2, 3]:
    p = Pipeline([("p", PolynomialFeatures(d, include_bias=False)),
                  ("lr", LinearRegression())]).fit(X_tr, y_tr)
    print(f"poly-{d} test R²: {p.score(X_te, y_te):.3f}")

# 4)
X = cars[num_features + cat_features]; y = cars["mpg"].values
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)
full.fit(X_tr, y_tr)
preds = full.predict(X_te[:5])
print(pd.DataFrame({"actual": y_te[:5], "predicted": preds.round(1)}))


# %% [markdown] color=rose title="Recap"
# # Recap
#
# ✅ Fit a simple linear regression and read its intercept + slope
# ✅ Always train/test split before scoring
# ✅ Use multiple LR + one-hot encoding for mixed features
# ✅ Add polynomial features for non-linear patterns
# ✅ Wrap preprocessing + model in a `Pipeline` to avoid leakage
# ✅ Predict on new data
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


