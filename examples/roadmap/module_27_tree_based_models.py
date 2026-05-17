# doodlecode format-version: 2
# Auto-converted from module_27_tree_based_models.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 27 Tree Based Models"
# # Module 27 Tree Based Models
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 27 — Tree-Based Models & Gradient Boosting"
# # Module 27 — Tree-Based Models & Gradient Boosting
#
# > **Premise:** for **tabular data** — the kind that lives in CSVs and databases — gradient-boosted trees beat neural networks ~80% of the time. They train in seconds, give you free feature importance, and require almost no preprocessing. This module is the workhorse you'll reach for first on any new tabular problem.
#
# ### What you'll cover
# 1. Why trees dominate tabular ML
# 2. **Decision Tree** — one tree, every concept visible
# 3. **Random Forest** — many trees, voted average
# …


# %% [markdown] color=mint title="1 · Why Trees for Tabular Data"
# # 1 · Why Trees for Tabular Data
#
# | Problem with neural nets on tabular | Why trees handle it |
# |---|---|
# | Need feature scaling | Trees are scale-invariant — split on raw values |
# | Need one-hot encoding | Modern boosters handle categoricals natively |
# | Need lots of data | Trees train well on hundreds-to-thousands of rows |
# | Hyper-sensitive to hyperparameters | XGBoost defaults work surprisingly often |
# …


# %% color=peach title="!pip -q install xgboost lightgbm shap"
# @explain: Run this cell to see the output.
!pip -q install xgboost lightgbm shap
import numpy as np, pandas as pd, matplotlib.pyplot as plt
import warnings; warnings.filterwarnings("ignore")
np.random.seed(0)


# %% [markdown] color=violet title="2 · Decision Tree — One Tree, Every Concept Visible"
# # 2 · Decision Tree — One Tree, Every Concept Visible
#
# Start with a **single decision tree**. It's the building block of everything below. The algorithm:
#
# 1. Look at every feature × every possible split.
# 2. Pick the split that **most reduces impurity** (Gini or entropy for classification, MSE for regression).
# 3. Recurse on each side until pure or `max_depth` is hit.


# %% color=amber title="Tree depth = 3 to keep it visualisable"
# @explain: Tree depth = 3 to keep it visualisable
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.metrics import accuracy_score

data = load_breast_cancer(as_frame=True)
X, y = data.data, data.target
print("shape:", X.shape, "  classes:", data.target_names.tolist())

X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Tree depth = 3 to keep it visualisable
tree = DecisionTreeClassifier(max_depth=3, random_state=0).fit(X_tr, y_tr)
print(f"train acc: {tree.score(X_tr, y_tr):.3f}")
print(f"test  acc: {tree.score(X_te, y_te):.3f}")


# %% color=rose title="plt.figure(figsize=(14"
# @explain: Run this cell to see the output.
plt.figure(figsize=(14, 6))
plot_tree(tree, feature_names=X.columns, class_names=data.target_names,
          filled=True, rounded=True, fontsize=8)
plt.show()


# %% [markdown] color=lime title="Read the tree:** each box shows the split rule,…"
# # Read the tree:** each box shows the split rule,…
#
# **Read the tree:** each box shows the split rule, Gini impurity, sample count, and class distribution. The COLOUR INTENSITY indicates how confident the leaf is (saturated blue = malignant; saturated orange = benign).


# %% [markdown] color=teal title="3 · Random Forest — Many Trees, Voted Average"
# # 3 · Random Forest — Many Trees, Voted Average
#
# A single tree **overfits** easily. Random Forest fixes this by training **many trees on bootstrap samples + random feature subsets**, then averaging.
#
# Each tree:
# - Sees a different random sample of rows (with replacement = "bootstrap").
# - Considers a random subset of features at each split.
#
# …


# %% color=sky title="from sklearn.ensemble import RandomForestClassifier"
# @explain: Run this cell to see the output.
from sklearn.ensemble import RandomForestClassifier

rf = RandomForestClassifier(n_estimators=200, max_depth=None,
                            n_jobs=-1, random_state=0).fit(X_tr, y_tr)
print(f"RF train acc: {rf.score(X_tr, y_tr):.3f}")
print(f"RF test  acc: {rf.score(X_te, y_te):.3f}")


# %% color=mint title="Free feature importance"
# @explain: Free feature importance
# Free feature importance
importances = pd.Series(rf.feature_importances_, index=X.columns).sort_values()
importances.tail(10).plot.barh(figsize=(7, 4),
                                title="Top 10 features by Random Forest importance")
plt.tight_layout(); plt.show()


# %% [markdown] color=peach title="4 · Gradient Boosting — Sequential Trees that Fix Each Other's Mistakes"
# # 4 · Gradient Boosting — Sequential Trees that Fix Each Other's Mistakes
#
# Random Forest = **independent** trees averaged.
# Gradient Boosting = **sequential** trees, where each new tree predicts the *errors* of the previous ones.
#
# Result: usually a few percent better than RF, especially on harder datasets. Standard scikit-learn implementation:


# %% color=violet title="from sklearn.ensemble import GradientBoostingClassifier"
# @explain: Run this cell to see the output.
from sklearn.ensemble import GradientBoostingClassifier

gb = GradientBoostingClassifier(n_estimators=200, learning_rate=0.1,
                                max_depth=3, random_state=0).fit(X_tr, y_tr)
print(f"GB train acc: {gb.score(X_tr, y_tr):.3f}")
print(f"GB test  acc: {gb.score(X_te, y_te):.3f}")


# %% [markdown] color=amber title="5 · XGBoost & LightGBM — the Production Boosters"
# # 5 · XGBoost & LightGBM — the Production Boosters
#
# These two have **dominated tabular Kaggle competitions for ~10 years** and are the default choice in industry. Both are gradient-boosted-tree implementations with serious engineering:
#
# | Library | Strengths |
# |---|---|
# | **XGBoost** | the "default everyone knows", excellent docs, GPU support |
# | **LightGBM** | faster on big data, native categorical handling, smaller memory |
# …


# %% color=rose title="import xgboost as xgb"
# @explain: Run this cell to see the output.
import xgboost as xgb

xgb_clf = xgb.XGBClassifier(
    n_estimators=300, learning_rate=0.05, max_depth=4,
    subsample=0.9, colsample_bytree=0.9,
    eval_metric="logloss", random_state=0, n_jobs=-1)

xgb_clf.fit(X_tr, y_tr)
print(f"XGB train acc: {xgb_clf.score(X_tr, y_tr):.3f}")
print(f"XGB test  acc: {xgb_clf.score(X_te, y_te):.3f}")


# %% color=lime title="import lightgbm as lgb"
# @explain: Run this cell to see the output.
import lightgbm as lgb

lgb_clf = lgb.LGBMClassifier(
    n_estimators=300, learning_rate=0.05, max_depth=4,
    subsample=0.9, colsample_bytree=0.9,
    random_state=0, n_jobs=-1, verbose=-1)

lgb_clf.fit(X_tr, y_tr)
print(f"LGB train acc: {lgb_clf.score(X_tr, y_tr):.3f}")
print(f"LGB test  acc: {lgb_clf.score(X_te, y_te):.3f}")


# %% [markdown] color=teal title="Side-by-side comparison"
# # Side-by-side comparison
#


# %% color=sky title="from sklearn.tree import DecisionTreeClassifier"
# @explain: Run this cell to see the output.
from sklearn.tree import DecisionTreeClassifier

models = {
    "DecisionTree (depth=3)": DecisionTreeClassifier(max_depth=3, random_state=0),
    "RandomForest":           RandomForestClassifier(n_estimators=200, n_jobs=-1, random_state=0),
    "GradientBoosting":       GradientBoostingClassifier(n_estimators=200, random_state=0),
    "XGBoost":                xgb.XGBClassifier(n_estimators=300, learning_rate=0.05,
                                                max_depth=4, eval_metric="logloss",
                                                random_state=0, n_jobs=-1),
    "LightGBM":               lgb.LGBMClassifier(n_estimators=300, learning_rate=0.05,
                                                  max_depth=4, random_state=0,
                                                  n_jobs=-1, verbose=-1),
}

results = []
for name, m in models.items():
    m.fit(X_tr, y_tr)
    results.append({"model": name,
                    "train_acc": m.score(X_tr, y_tr),
                    "test_acc":  m.score(X_te, y_te)})

print(pd.DataFrame(results).round(4))


# %% [markdown] color=mint title="6 · Hyperparameter Tuning with `GridSearchCV`"
# # 6 · Hyperparameter Tuning with `GridSearchCV`
#
# Boosters have many knobs. A small grid usually beats hand-tuning.


# %% color=peach title="from sklearn.model_selection import GridSearchCV"
# @explain: Run this cell to see the output.
from sklearn.model_selection import GridSearchCV

grid = GridSearchCV(
    xgb.XGBClassifier(eval_metric="logloss", random_state=0, n_jobs=-1),
    param_grid={
        "n_estimators": [100, 300],
        "learning_rate": [0.05, 0.1],
        "max_depth": [3, 5, 7],
    },
    cv=5, scoring="roc_auc", n_jobs=-1,
)
grid.fit(X_tr, y_tr)
print("best params:", grid.best_params_)
print(f"best CV AUC: {grid.best_score_:.4f}")


# %% [markdown] color=violet title="7 · Classification Metrics Done Right"
# # 7 · Classification Metrics Done Right
#
# Accuracy hides a lot. The metrics you'll actually report:
#
# | Metric | What it means | When to use |
# |---|---|---|
# | Accuracy | TP+TN / total | balanced classes, all errors equal |
# | Precision | TP / (TP+FP) | false positives are costly (spam filter) |
# …


# %% color=amber title="from sklearn.metrics import"
# @explain: Run this cell to see the output.
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                              f1_score, roc_auc_score, average_precision_score,
                              confusion_matrix, classification_report,
                              roc_curve, precision_recall_curve)

best = grid.best_estimator_
y_pred = best.predict(X_te)
y_proba = best.predict_proba(X_te)[:, 1]   # probability of class 1 (benign)

print("accuracy :", accuracy_score(y_te, y_pred).round(4))
print("precision:", precision_score(y_te, y_pred).round(4))
print("recall   :", recall_score(y_te, y_pred).round(4))
print("F1       :", f1_score(y_te, y_pred).round(4))
print("ROC AUC  :", roc_auc_score(y_te, y_proba).round(4))
print("PR  AUC  :", average_precision_score(y_te, y_proba).round(4))

print("\nconfusion matrix (rows = actual, cols = predicted):")
print(confusion_matrix(y_te, y_pred))
print("\n", classification_report(y_te, y_pred,
                                    target_names=data.target_names))


# %% color=rose title="ROC and PR curves"
# @explain: ROC and PR curves
# ROC and PR curves
fig, ax = plt.subplots(1, 2, figsize=(11, 4))

fpr, tpr, _ = roc_curve(y_te, y_proba)
ax[0].plot(fpr, tpr); ax[0].plot([0,1],[0,1],"--",color="grey")
ax[0].set(xlabel="false positive rate", ylabel="true positive rate (recall)",
          title=f"ROC curve (AUC={roc_auc_score(y_te, y_proba):.3f})")

prec, rec, _ = precision_recall_curve(y_te, y_proba)
ax[1].plot(rec, prec); ax[1].set(xlabel="recall", ylabel="precision",
                                  title=f"PR curve (AP={average_precision_score(y_te, y_proba):.3f})")
plt.tight_layout(); plt.show()


# %% [markdown] color=lime title="8 · Threshold Tuning — When 0.5 Is the Wrong Cutoff"
# # 8 · Threshold Tuning — When 0.5 Is the Wrong Cutoff
#
# By default `.predict()` uses a **0.5 cutoff** on the predicted probability. But for imbalanced or asymmetric-cost problems, that's almost never optimal.


# %% color=teal title="thresholds = np.linspace(0.05"
# @explain: Run this cell to see the output.
thresholds = np.linspace(0.05, 0.95, 19)
rows = []
for t in thresholds:
    pred = (y_proba >= t).astype(int)
    rows.append({"threshold": t,
                 "precision": precision_score(y_te, pred, zero_division=0),
                 "recall":    recall_score(y_te, pred),
                 "f1":        f1_score(y_te, pred, zero_division=0)})

th_df = pd.DataFrame(rows)
ax = th_df.set_index("threshold").plot(figsize=(8, 4),
                                        title="Precision / Recall / F1 vs threshold")
ax.axvline(0.5, color="grey", linestyle="--", label="default 0.5")
ax.legend(); plt.show()

best_f1_row = th_df.iloc[th_df["f1"].idxmax()]
print(f"best F1 at threshold = {best_f1_row.threshold:.2f}: F1 = {best_f1_row.f1:.3f}")


# %% [markdown] color=sky title="9 · Imbalanced Classes — When 99% of Rows Are Class 0"
# # 9 · Imbalanced Classes — When 99% of Rows Are Class 0
#
# Real-world classification is rarely 50/50. Fraud, churn, conversion — usually 1-10% positive class. Three fixes:
#
# 1. **`class_weight="balanced"`** — weight rare class higher in the loss.
# 2. **Resample** — `imbalanced-learn`'s SMOTE for synthetic minority oversampling.
# 3. **Tune threshold** instead of optimising accuracy (section 8).
#
# …


# %% color=mint title="Without class_weight"
# @explain: Without class_weight
# @explain: With class_weight
from sklearn.datasets import make_classification

Xi, yi = make_classification(n_samples=2000, n_features=20, weights=[0.95, 0.05],
                              n_informative=10, random_state=0)
print("class balance:", np.bincount(yi))

Xi_tr, Xi_te, yi_tr, yi_te = train_test_split(Xi, yi, test_size=0.2,
                                                random_state=0, stratify=yi)

# Without class_weight
naive = lgb.LGBMClassifier(n_estimators=300, random_state=0, n_jobs=-1, verbose=-1).fit(Xi_tr, yi_tr)
# With class_weight
weighted = lgb.LGBMClassifier(n_estimators=300, class_weight="balanced",
                              random_state=0, n_jobs=-1, verbose=-1).fit(Xi_tr, yi_tr)

for label, m in [("naive", naive), ("class_weight='balanced'", weighted)]:
    p = m.predict_proba(Xi_te)[:, 1]
    print(f"\n{label}:")
    print(f"  ROC-AUC: {roc_auc_score(yi_te, p):.3f}   PR-AUC: {average_precision_score(yi_te, p):.3f}")


# %% [markdown] color=peach title="10 · SHAP — Explain Any Model's Predictions"
# # 10 · SHAP — Explain Any Model's Predictions
#
# **SHAP** (SHapley Additive exPlanations) assigns each feature a contribution to **each individual prediction**. Critical for:
#
# - Stakeholder communication ("the model said this customer will churn — why?").
# - Regulated industries (loan / insurance / medical model audits).
# - Debugging — spot features the model is leaning on for the wrong reason.


# %% color=violet title="Global view"
# @explain: Global view — average impact of each feature
import shap

explainer = shap.TreeExplainer(best)
sample = X_te.iloc[:200]                           # SHAP can be slow on huge datasets
shap_values = explainer.shap_values(sample)

# Global view — average impact of each feature
shap.summary_plot(shap_values, sample, plot_type="bar", show=False)
plt.tight_layout(); plt.show()


# %% color=amber title="Distribution view"
# @explain: Distribution view — each dot = one prediction; colour = feature value
# Distribution view — each dot = one prediction; colour = feature value
shap.summary_plot(shap_values, sample, show=False)
plt.tight_layout(); plt.show()


# %% color=rose title="Single-prediction explanation"
# @explain: Single-prediction explanation — "why did the model predict this for row 0?"
# Single-prediction explanation — "why did the model predict this for row 0?"
shap.initjs()                                      # for interactive HTML rendering
shap.force_plot(explainer.expected_value, shap_values[0,:], sample.iloc[0,:],
                matplotlib=True, show=False)
plt.tight_layout(); plt.show()


# %% [markdown] color=lime title="11 · Practice — Try Yourself"
# # 11 · Practice — Try Yourself
#
# 1. Load the `wine` dataset (`from sklearn.datasets import load_wine`). Train a Random Forest and report test accuracy + per-class precision/recall.
# 2. On the imbalanced synthetic dataset from §9, find the threshold that **maximises F1**. How much better is it than 0.5?
# 3. Fit XGBoost on the breast-cancer dataset with `early_stopping_rounds=20` and a watchlist. How many trees did it actually train?
# 4. Pick the top-3 SHAP-importance features and re-train on JUST those three. How much accuracy do you lose?


# %% color=teal title="Sketch for #1"
# @explain: Sketch for #1 — Wine
# Sketch for #1 — Wine
from sklearn.datasets import load_wine
wine = load_wine(as_frame=True)
Xw, yw = wine.data, wine.target

Xw_tr, Xw_te, yw_tr, yw_te = train_test_split(Xw, yw, test_size=0.2, random_state=42, stratify=yw)
rf_wine = RandomForestClassifier(n_estimators=200, n_jobs=-1, random_state=0).fit(Xw_tr, yw_tr)
print("wine test acc:", rf_wine.score(Xw_te, yw_te).round(4))
from sklearn.metrics import classification_report
print(classification_report(yw_te, rf_wine.predict(Xw_te), target_names=wine.target_names))


# %% [markdown] color=sky title="Recap"
# # Recap
#
# ✅ Pick the right tree-based model from the situation (single tree → RF → boosting)
# ✅ Run XGBoost and LightGBM as the default tabular baselines
# ✅ Tune hyperparameters with `GridSearchCV` and the right scoring metric
# ✅ Read all 6 classification metrics; pick the right one for the problem
# ✅ Tune the **decision threshold** when 0.5 is wrong
# ✅ Handle **imbalanced classes** with `class_weight` + AUC-PR
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


