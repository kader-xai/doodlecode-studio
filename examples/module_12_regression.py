# %% [markdown]
# # Module 12 — Linear & Logistic Regression
# Two foundational models that every ML practitioner should know cold:
# **linear regression** for predicting a number, **logistic regression**
# for predicting a class probability.

# %% kind=import color=sky title="Imports"
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_regression, make_classification, load_diabetes
from sklearn.linear_model import LinearRegression, Ridge, Lasso, LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    mean_squared_error, mean_absolute_error, r2_score,
    accuracy_score, roc_auc_score, classification_report,
)
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.pipeline import Pipeline
np.random.seed(0)


# %% [markdown]
# # Part 1 — Linear regression


# %% kind=intro color=sky title="What linear regression learns"
# @explain: y ≈ w₁·x₁ + w₂·x₂ + … + wₙ·xₙ + b. It finds the weights
# @explain: that minimise sum of squared errors. Fast, interpretable,
# @explain: and a great baseline for any regression task.


# %% kind=function color=mint title="Tiny demo on synthetic data"
# @explain: One feature, true slope = 2.5, true intercept = 7. We add
# @explain: gaussian noise to make it realistic.
X, y = make_regression(n_samples=80, n_features=1, noise=10, random_state=0, bias=7)

model = LinearRegression().fit(X, y)
print(f"learned slope    : {model.coef_[0]:.3f}")
print(f"learned intercept: {model.intercept_:.3f}")

xs = np.linspace(X.min(), X.max(), 100).reshape(-1, 1)
plt.figure(figsize=(5, 3))
plt.scatter(X, y, alpha=0.6)
plt.plot(xs, model.predict(xs), color="crimson")
plt.title("Linear fit"); plt.show()


# %% kind=function color=mint title="Metrics — MSE, MAE, R²"
# @explain: MSE = avg squared error (sensitive to outliers).
# @explain: MAE = avg absolute error (more robust).
# @explain: R²  = fraction of variance explained, 0 to 1.
preds = model.predict(X)
print(f"MSE : {mean_squared_error(y, preds):.2f}")
print(f"MAE : {mean_absolute_error(y, preds):.2f}")
print(f"R²  : {r2_score(y, preds):.3f}")


# %% kind=function color=mint title="A real dataset — diabetes"
# @explain: 442 patients, 10 features (age, BMI, blood markers).
# @explain: Target: disease progression one year out.
data = load_diabetes()
X, y = data.data, data.target
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=0)

model = LinearRegression().fit(X_tr, y_tr)
print(f"train R²: {model.score(X_tr, y_tr):.3f}")
print(f"test  R²: {model.score(X_te, y_te):.3f}")
for name, w in zip(data.feature_names, model.coef_):
    print(f"  {name:8s}: {w:+.1f}")


# %% [markdown]
# ## Regularisation — Ridge and Lasso
# When features are correlated or sample size is small, plain least
# squares overfits. **Ridge** (L2) shrinks all weights; **Lasso** (L1)
# pushes some weights to exactly zero (feature selection).


# %% kind=function color=mint title="Ridge vs Lasso"
# @explain: alpha controls regularisation strength. Larger α → simpler
# @explain: model, smaller weights, more bias / less variance.
for name, M in [("Plain", LinearRegression()),
                ("Ridge(α=1)", Ridge(alpha=1.0)),
                ("Lasso(α=0.5)", Lasso(alpha=0.5))]:
    M.fit(X_tr, y_tr)
    print(f"{name:14s} test R²: {M.score(X_te, y_te):.3f}  |w|₁ = {np.abs(M.coef_).sum():.1f}")


# %% kind=function color=mint title="Polynomial features — fitting a curve"
# @explain: Linear regression on x, x², x³, … fits curves. Wrap in a
# @explain: pipeline so the polynomial expansion is part of the model.
n = 60
X = np.linspace(-3, 3, n).reshape(-1, 1)
y_true = 0.5 * X.ravel() ** 3 - 2 * X.ravel() + 1
y = y_true + np.random.randn(n) * 1.5

degree3 = Pipeline([
    ("poly", PolynomialFeatures(degree=3, include_bias=False)),
    ("scale", StandardScaler()),
    ("reg",   LinearRegression()),
]).fit(X, y)

xs = np.linspace(-3.2, 3.2, 200).reshape(-1, 1)
plt.figure(figsize=(5, 3))
plt.scatter(X, y, alpha=0.5)
plt.plot(xs, degree3.predict(xs), color="crimson", label="degree 3 fit")
plt.legend(); plt.title("Polynomial regression"); plt.show()


# %% [markdown]
# # Part 2 — Logistic regression


# %% kind=intro color=sky title="What logistic regression learns"
# @explain: It's NOT regression — it's classification. The model returns
# @explain: a probability via the sigmoid of a linear combination:
# @explain:   p = 1 / (1 + e^(-(w·x + b)))
# @explain: Predict class 1 when p > 0.5.


# %% kind=function color=mint title="Binary classification demo"
# @explain: 2 features so we can plot the decision boundary.
X, y = make_classification(n_samples=300, n_features=2, n_informative=2,
                            n_redundant=0, n_clusters_per_class=1,
                            class_sep=1.5, random_state=0)
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.3, random_state=0)

clf = LogisticRegression().fit(X_tr, y_tr)
print(f"train acc: {clf.score(X_tr, y_tr):.3f}")
print(f"test  acc: {clf.score(X_te, y_te):.3f}")

# Decision boundary plot
xx, yy = np.meshgrid(np.linspace(X[:, 0].min()-1, X[:, 0].max()+1, 200),
                     np.linspace(X[:, 1].min()-1, X[:, 1].max()+1, 200))
Z = clf.predict_proba(np.c_[xx.ravel(), yy.ravel()])[:, 1].reshape(xx.shape)
plt.figure(figsize=(5, 4))
plt.contourf(xx, yy, Z, levels=20, cmap="coolwarm", alpha=0.6)
plt.scatter(X[:, 0], X[:, 1], c=y, cmap="coolwarm", edgecolor="k")
plt.title("Logistic regression decision surface")
plt.show()


# %% kind=function color=mint title="Probability vs hard prediction"
# @explain: predict_proba gives you P(class=1). The default 0.5
# @explain: threshold is rarely optimal — pick it from the ROC curve
# @explain: for your business cost.
proba = clf.predict_proba(X_te)[:, 1]
hard = (proba > 0.5).astype(int)
print("proba[:5]:", proba[:5].round(2))
print("hard [:5]:", hard[:5])
print("truth[:5]:", y_te[:5])
print()
print(f"AUC : {roc_auc_score(y_te, proba):.3f}")
print(classification_report(y_te, hard))


# %% kind=function color=mint title="Multiclass logistic regression"
# @explain: With multi_class='multinomial' (default for newer solvers)
# @explain: it generalises to K > 2 classes naturally.
from sklearn.datasets import load_iris
iris = load_iris()
X_tr, X_te, y_tr, y_te = train_test_split(
    iris.data, iris.target, test_size=0.25, stratify=iris.target, random_state=0
)
clf = LogisticRegression(max_iter=500).fit(X_tr, y_tr)
print(f"accuracy: {clf.score(X_te, y_te):.3f}")
print("class weights shape:", clf.coef_.shape)  # (3 classes, 4 features)


# %% [markdown]
# ## Practice
# 1. Fit `Ridge(alpha=0.1)` on `make_regression(n_samples=200, noise=20)`
#    and report R² on a held-out 25% test split.
# 2. Train a logistic regression on a binary `make_classification` with
#    500 samples and 5 features. Compute ROC AUC.


# %% kind=function color=mint title="Practice 1 — Ridge R²"
X, y = make_regression(n_samples=200, n_features=5, noise=20, random_state=0)
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25, random_state=0)
m = Ridge(alpha=0.1).fit(X_tr, y_tr)
print(f"R²: {m.score(X_te, y_te):.3f}")


# %% kind=function color=mint title="Practice 2 — Binary AUC"
X, y = make_classification(n_samples=500, n_features=5, random_state=0)
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=0)
clf = LogisticRegression(max_iter=500).fit(X_tr, y_tr)
proba = clf.predict_proba(X_te)[:, 1]
print(f"AUC: {roc_auc_score(y_te, proba):.3f}")


# %% [markdown]
# ## Recap
# - ✅ LinearRegression + interpret the coefficients
# - ✅ MSE / MAE / R²
# - ✅ Ridge / Lasso regularisation
# - ✅ Polynomial features for nonlinear shapes
# - ✅ LogisticRegression for binary + multiclass
# - ✅ ROC AUC, decision boundaries
#
# **Next:** Module 13 — Neural networks intro.
