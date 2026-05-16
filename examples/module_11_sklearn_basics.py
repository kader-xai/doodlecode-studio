# %% [markdown]
# # Module 11 — scikit-learn Basics
# Every sklearn model shares the same four-method API: `fit`, `predict`,
# `score`, plus `transform` for preprocessing. Learn the pattern once,
# use it for hundreds of models.

# %% kind=install color=rose title="Install scikit-learn"
import importlib, subprocess, sys
if importlib.util.find_spec("sklearn") is None:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "scikit-learn"])
print("sklearn ready.")


# %% kind=import color=sky title="Imports"
import numpy as np
from sklearn.datasets import load_iris, make_classification
from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score,
)
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
np.random.seed(0)


# %% kind=intro color=sky title="The estimator API"
# @explain: estimator.fit(X, y)         → learn from data
# @explain: estimator.predict(X_new)    → make predictions
# @explain: estimator.score(X, y)       → evaluate (accuracy / R²)
# @explain: For preprocessors: .transform / .fit_transform.
# @tags: intro


# %% kind=assign color=peach title="A built-in dataset — iris"
# @explain: 150 flowers, 4 features each, 3 species. The 'hello world'
# @explain: of classification.
iris = load_iris()
X, y = iris.data, iris.target
print("X shape :", X.shape)
print("classes :", iris.target_names)
print("features:", iris.feature_names)


# %% kind=function color=mint title="Train / test split"
# @explain: 80/20 split with stratify so each class is represented in
# @explain: both halves. random_state makes the split reproducible.
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)
print(f"train: {X_train.shape},  test: {X_test.shape}")


# %% [markdown]
# ## A first model — LogisticRegression


# %% kind=function color=mint title="Fit, predict, score"
# @explain: Three lines and you have a working classifier. Logistic
# @explain: regression is a solid baseline for any classification task.
clf = LogisticRegression(max_iter=200)
clf.fit(X_train, y_train)
preds = clf.predict(X_test)
print(f"accuracy: {clf.score(X_test, y_test):.3f}")
print(f"preds[:10]: {preds[:10]}")
print(f"truth[:10]: {y_test[:10]}")


# %% [markdown]
# ## Classification metrics — accuracy isn't everything


# %% kind=function color=mint title="Confusion matrix"
# @explain: Each row = true class, each column = predicted class. The
# @explain: diagonal is correct predictions; off-diagonal is mistakes.
print(confusion_matrix(y_test, preds))


# %% kind=function color=mint title="Precision, recall, F1"
# @explain: Precision = of those predicted positive, how many are right.
# @explain: Recall    = of all true positives, how many did we catch.
# @explain: F1 = harmonic mean. On imbalanced data, look at these — not
# @explain: just accuracy.
print(classification_report(y_test, preds, target_names=iris.target_names))


# %% kind=function color=mint title="Binary classification metrics + AUC"
# @explain: ROC AUC measures the model's ranking ability across all
# @explain: thresholds. 0.5 = random, 1.0 = perfect.
Xb, yb = make_classification(n_samples=1000, n_features=10, n_classes=2,
                              weights=[0.7, 0.3], random_state=0)
Xb_tr, Xb_te, yb_tr, yb_te = train_test_split(Xb, yb, test_size=0.2, random_state=0)
clf = LogisticRegression(max_iter=500).fit(Xb_tr, yb_tr)
proba = clf.predict_proba(Xb_te)[:, 1]   # P(class=1)
preds = (proba > 0.5).astype(int)
print(f"accuracy : {accuracy_score(yb_te, preds):.3f}")
print(f"precision: {precision_score(yb_te, preds):.3f}")
print(f"recall   : {recall_score(yb_te, preds):.3f}")
print(f"f1       : {f1_score(yb_te, preds):.3f}")
print(f"ROC AUC  : {roc_auc_score(yb_te, proba):.3f}")


# %% [markdown]
# ## Cross-validation — getting a stable score


# %% kind=function color=mint title="K-fold cross-validation"
# @explain: Train K models, each on K-1 folds, test on the held-out
# @explain: fold. Average score = much less noisy than a single split.
clf = LogisticRegression(max_iter=200)
scores = cross_val_score(clf, X, y, cv=5, scoring="accuracy")
print("per-fold:", scores.round(3))
print(f"mean: {scores.mean():.3f}  ±  {scores.std():.3f}")


# %% [markdown]
# ## Comparing models head-to-head


# %% kind=function color=mint title="Four classifiers, one loop"
# @explain: Same API for everything — that's the point of sklearn.
# @explain: Wrap each in a pipeline with a scaler so distance/linear
# @explain: methods work fairly.
models = {
    "LogReg":      Pipeline([("s", StandardScaler()), ("m", LogisticRegression(max_iter=500))]),
    "KNN-5":       Pipeline([("s", StandardScaler()), ("m", KNeighborsClassifier(n_neighbors=5))]),
    "SVM-RBF":     Pipeline([("s", StandardScaler()), ("m", SVC(kernel="rbf", probability=False))]),
    "RandomForest": RandomForestClassifier(n_estimators=100, random_state=0),
}

for name, m in models.items():
    s = cross_val_score(m, X, y, cv=5, scoring="accuracy")
    print(f"{name:14s}: {s.mean():.3f}  ±  {s.std():.3f}")


# %% [markdown]
# ## Feature importance — which inputs matter?


# %% kind=function color=mint title="Random forest feature importances"
# @explain: Tree-based models expose feature_importances_. Higher =
# @explain: more useful for splitting. Quick sanity check on a dataset.
rf = RandomForestClassifier(n_estimators=200, random_state=0).fit(X, y)
for name, imp in zip(iris.feature_names, rf.feature_importances_):
    print(f"  {name:25s}: {imp:.3f}")


# %% [markdown]
# ## Practice
# 1. Train a `DecisionTreeClassifier(max_depth=3)` on iris and report
#    its accuracy.
# 2. Use 10-fold CV on a `LogisticRegression(max_iter=1000)`, report
#    mean ± std accuracy.


# %% kind=function color=mint title="Practice 1 — shallow decision tree"
# @explain: max_depth caps the tree complexity. Depth 3 on iris is
# @explain: usually enough for ~95%+ accuracy.
tree = DecisionTreeClassifier(max_depth=3, random_state=0).fit(X_train, y_train)
print(f"accuracy: {tree.score(X_test, y_test):.3f}")


# %% kind=function color=mint title="Practice 2 — 10-fold CV"
# @explain: Same idea as 5-fold, just K=10. Smaller test sets, more
# @explain: averaging, slightly higher variance per fold.
clf = LogisticRegression(max_iter=1000)
s = cross_val_score(clf, X, y, cv=10, scoring="accuracy")
print(f"10-fold accuracy: {s.mean():.3f} ± {s.std():.3f}")


# %% [markdown]
# ## Recap
# - ✅ fit / predict / score / transform API
# - ✅ train_test_split with stratify
# - ✅ Accuracy, precision, recall, F1, ROC AUC, confusion matrix
# - ✅ K-fold cross-validation
# - ✅ Side-by-side model comparison
# - ✅ Feature importances
#
# **Next:** Module 12 — Regression (linear + logistic).
