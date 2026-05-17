# doodlecode format-version: 2
# Auto-converted from module_15_model_evaluation.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 15 Model Evaluation"
# # Module 15 Model Evaluation
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 15 — Model Evaluation & Refinement"
# # Module 15 — Model Evaluation & Refinement
#
# *IBM Data Analysis · Module 5 of 6 (Module 15 of 16)*
#
# A model that scores 99% on training data and 50% on new data is **worse than useless** — it's giving false confidence. This module is about **honest evaluation** and the techniques used to improve a model without lying to yourself.
#
# ### What you'll cover
# 1. Regression metrics — MSE, RMSE, MAE, R²
# 2. Over-fitting vs under-fitting (the bias-variance tradeoff)
# …


# %% color=mint title="!pip -q install pandas numpy scikit-learn…"
# @explain: Run this cell to see the output.
!pip -q install pandas numpy scikit-learn matplotlib seaborn
import pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns

url  = "https://archive.ics.uci.edu/ml/machine-learning-databases/auto-mpg/auto-mpg.data"
cols = ["mpg","cylinders","displacement","horsepower","weight",
        "acceleration","model_year","origin","car_name"]
cars = pd.read_csv(url, sep=r"\s+", names=cols, na_values="?")
cars["horsepower"] = cars["horsepower"].fillna(cars["horsepower"].median())
cars["origin"] = cars["origin"].map({1:"USA",2:"Europe",3:"Japan"})

num_features = ["cylinders","displacement","horsepower","weight","acceleration","model_year"]
cat_features = ["origin"]
X, y = cars[num_features + cat_features], cars["mpg"].values
print(X.shape, y.shape)


# %% [markdown] color=peach title="1. Regression metrics — four to know"
# # 1. Regression metrics — four to know
#
# | Metric | Formula | Reads as |
# |---|---|---|
# | **MSE** | $\frac{1}{n}\sum (y_i - \hat y_i)^2$ | "average squared error" — penalises big errors heavily |
# | **RMSE** | $\sqrt{\text{MSE}}$ | same units as $y$ — most readable |
# | **MAE** | $\frac{1}{n}\sum |y_i - \hat y_i|$ | "average absolute error" — robust to outliers |
# | **R²** | $1 - \frac{\text{SS}_{\text{res}}}{\text{SS}_{\text{tot}}}$ | fraction of variance explained; 1 = perfect, 0 = no better than mean |


# %% color=violet title="from sklearn.linear_model import LinearRegression"
# @explain: Run this cell to see the output.
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

pre = ColumnTransformer([
    ("num", "passthrough", num_features),
    ("cat", OneHotEncoder(drop="first"), cat_features),
])
pipe = Pipeline([("pre", pre), ("lr", LinearRegression())])

X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)
pipe.fit(X_tr, y_tr)
y_pred = pipe.predict(X_te)

mse = mean_squared_error(y_te, y_pred)
rmse = np.sqrt(mse)
mae = mean_absolute_error(y_te, y_pred)
r2 = r2_score(y_te, y_pred)

print(f"MSE  : {mse:.2f}")
print(f"RMSE : {rmse:.2f}  (mpg)")
print(f"MAE  : {mae:.2f}  (mpg)")
print(f"R²   : {r2:.3f}")


# %% [markdown] color=amber title="2. Over-fitting vs under-fitting — the bias-variance tradeoff"
# # 2. Over-fitting vs under-fitting — the bias-variance tradeoff
#
# | State | Train score | Test score | Cause |
# |---|---|---|---|
# | **Underfit** | low | low | model too simple |
# | **Good fit** | high | high (≈ train) | just right |
# | **Overfit** | very high | low (≪ train) | model memorised noise |
#
# …


# %% color=rose title="from sklearn.preprocessing import PolynomialFeatures"
# @explain: Run this cell to see the output.
from sklearn.preprocessing import PolynomialFeatures
X1 = cars[["weight"]].values
y  = cars["mpg"].values
Xtr, Xte, ytr, yte = train_test_split(X1, y, test_size=0.2, random_state=42)

degrees, train_scores, test_scores = list(range(1, 16)), [], []
for d in degrees:
    p = Pipeline([("p", PolynomialFeatures(d, include_bias=False)),
                  ("lr", LinearRegression())]).fit(Xtr, ytr)
    train_scores.append(p.score(Xtr, ytr))
    test_scores.append(p.score(Xte, yte))

plt.plot(degrees, train_scores, "o-", label="train R²")
plt.plot(degrees, test_scores,  "s-", label="test R²")
plt.xlabel("polynomial degree"); plt.ylabel("R²")
plt.title("Underfit (left) → sweet spot → overfit (right)")
plt.axhline(0, color="grey", lw=.5); plt.legend(); plt.grid(alpha=.3); plt.show()


# %% [markdown] color=lime title="3. Cross-validation — k-fold"
# # 3. Cross-validation — k-fold
#
# A single train/test split can be lucky or unlucky. **k-fold CV** splits the data into k parts, trains on k-1, tests on the remaining 1, rotates through all k, and averages the scores. Standard k = 5 or 10.


# %% color=teal title="from sklearn.model_selection import cross_val_score"
# @explain: Run this cell to see the output.
from sklearn.model_selection import cross_val_score, KFold
cv = KFold(n_splits=5, shuffle=True, random_state=0)
scores = cross_val_score(pipe, X, y, cv=cv, scoring="r2")
print("fold R²:", scores.round(3))
print(f"mean R² = {scores.mean():.3f} ± {scores.std():.3f}")


# %% [markdown] color=sky title="4. Regularisation — Ridge & Lasso"
# # 4. Regularisation — Ridge & Lasso
#
# Both add a **penalty** to coefficients to discourage overfitting:
#
# | Method | Penalty | Effect |
# |---|---|---|
# | **Ridge** | $\alpha \sum b_j^2$ (L2) | shrinks coefficients toward zero |
# | **Lasso** | $\alpha \sum |b_j|$ (L1) | shrinks AND zeros out — feature selection for free |
# …


# %% color=mint title="from sklearn.linear_model import Ridge"
# @explain: Run this cell to see the output.
from sklearn.linear_model import Ridge, Lasso

for name, model in [("Ridge α=1",  Ridge(alpha=1.0)),
                    ("Ridge α=10", Ridge(alpha=10.0)),
                    ("Lasso α=0.1", Lasso(alpha=0.1, max_iter=10000))]:
    p = Pipeline([("pre", pre), ("m", model)])
    s = cross_val_score(p, X, y, cv=5, scoring="r2").mean()
    print(f"{name:<14} cv R² = {s:.3f}")


# %% [markdown] color=peach title="5. Hyperparameter tuning — `GridSearchCV`"
# # 5. Hyperparameter tuning — `GridSearchCV`
#
# `alpha` is a hyperparameter — you choose it, the model doesn't learn it. Use `GridSearchCV` to try a list of values via cross-validation and pick the best.


# %% color=violet title="from sklearn.model_selection import GridSearchCV"
# @explain: Run this cell to see the output.
from sklearn.model_selection import GridSearchCV

p = Pipeline([("pre", pre), ("m", Ridge())])
grid = GridSearchCV(p, {"m__alpha": [0.01, 0.1, 1, 10, 100, 1000]},
                    cv=5, scoring="r2")
grid.fit(X, y)
print("best alpha:", grid.best_params_)
print(f"best CV R²: {grid.best_score_:.3f}")
print(pd.DataFrame(grid.cv_results_)[["param_m__alpha","mean_test_score","std_test_score"]])


# %% [markdown] color=amber title="6. Diagnostic plots"
# # 6. Diagnostic plots
#


# %% color=rose title="best = grid.best_estimator_"
# @explain: Run this cell to see the output.
best = grid.best_estimator_
y_pred = best.predict(X_te)

fig, axes = plt.subplots(1, 2, figsize=(11, 4))
axes[0].scatter(y_te, y_pred, alpha=.5)
axes[0].plot([y_te.min(), y_te.max()], [y_te.min(), y_te.max()], "r--")
axes[0].set(xlabel="actual mpg", ylabel="predicted mpg",
            title=f"Predicted vs actual (R² = {r2_score(y_te, y_pred):.2f})")

residuals = y_te - y_pred
axes[1].scatter(y_pred, residuals, alpha=.5)
axes[1].axhline(0, color="red", linestyle="--")
axes[1].set(xlabel="predicted", ylabel="residual",
            title="Residuals — should look like random noise")
plt.tight_layout(); plt.show()


# %% [markdown] color=lime title="7. Learning curves — does more data help?"
# # 7. Learning curves — does more data help?
#
# A learning curve plots train and validation score as the **training set size** grows. If both are converging from below, more data will help. If they've plateaued and there's a gap, you have a model problem (over/underfit), not a data problem.


# %% color=teal title="from sklearn.model_selection import learning_curve"
# @explain: Run this cell to see the output.
from sklearn.model_selection import learning_curve

train_sizes, train_scores, val_scores = learning_curve(
    best, X, y, cv=5, train_sizes=np.linspace(0.1, 1.0, 8), scoring="r2",
    random_state=0)

plt.plot(train_sizes, train_scores.mean(axis=1), "o-", label="train R²")
plt.plot(train_sizes, val_scores.mean(axis=1),   "s-", label="validation R²")
plt.xlabel("training set size"); plt.ylabel("R²")
plt.title("Learning curve"); plt.legend(); plt.grid(alpha=.3); plt.show()


# %% [markdown] color=sky title="8. Practice"
# # 8. Practice
#
# 1. Compute MSE, RMSE, MAE, R² on the test set for the multiple LR pipeline. Which metric do you find most intuitive?
# 2. Fit a Ridge regression with α=1 using cross-validation. Compare the mean CV R² to the plain LR.
# 3. GridSearch α in `[0.001, 0.01, 0.1, 1, 10, 100]` for both Ridge and Lasso. Which performs better and at what α?
# 4. Plot the residual histogram of your best model. It should look roughly normal around 0.


# %% color=mint title="1)"
# @explain: 1)
# @explain: 2)
# @explain: 3)
# @explain: 4)
# 1)
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)
pipe.fit(X_tr, y_tr)
y_pred = pipe.predict(X_te)
print(f"MSE={mean_squared_error(y_te,y_pred):.2f}, "
      f"RMSE={np.sqrt(mean_squared_error(y_te,y_pred)):.2f}, "
      f"MAE={mean_absolute_error(y_te,y_pred):.2f}, "
      f"R²={r2_score(y_te,y_pred):.3f}")

# 2)
ridge = Pipeline([("pre", pre), ("m", Ridge(alpha=1.0))])
print("plain LR cv R²:", cross_val_score(pipe, X, y, cv=5).mean().round(3))
print("ridge α=1 cv R²:", cross_val_score(ridge, X, y, cv=5).mean().round(3))

# 3)
for cls, name in [(Ridge, "Ridge"), (Lasso, "Lasso")]:
    g = GridSearchCV(Pipeline([("pre", pre), ("m", cls(max_iter=10000))]),
                     {"m__alpha": [0.001, 0.01, 0.1, 1, 10, 100]},
                     cv=5, scoring="r2").fit(X, y)
    print(f"{name}: best α={g.best_params_['m__alpha']}, R²={g.best_score_:.3f}")

# 4)
y_pred = best.predict(X_te)
plt.hist(y_te - y_pred, bins=30, edgecolor="white"); plt.axvline(0, color="red")
plt.title("Residuals — best model"); plt.show()


# %% [markdown] color=peach title="Recap"
# # Recap
#
# ✅ Read MSE / RMSE / MAE / R² and pick the right one for the audience
# ✅ Spot under- vs over-fitting from train/test gaps
# ✅ Use k-fold cross-validation for honest scoring
# ✅ Add Ridge or Lasso to fight overfitting
# ✅ Tune hyperparameters with GridSearchCV
# ✅ Read residuals and learning curves
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


