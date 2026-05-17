# doodlecode format-version: 2
# Auto-converted from module_16_capstone.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 16 Capstone"
# # Module 16 Capstone
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 16 — Final Capstone Project"
# # Module 16 — Final Capstone Project
#
# *IBM Data Analysis · Module 6 of 6 — the finale (Module 16 of 16)*
#
# This is the **end-to-end run**. We import a real dataset, wrangle it, explore it, model it, evaluate it, and finish with a one-page narrative that a non-technical stakeholder could read.
#
# We use a **new dataset** for the capstone — the **Boston-style California Housing dataset** — to prove the workflow generalises beyond auto-mpg.
#
# ### The six-step workflow (memorise it)
# …


# %% color=mint title="!pip -q install pandas numpy scikit-learn…"
# @explain: Run this cell to see the output.
!pip -q install pandas numpy scikit-learn matplotlib seaborn
import pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns
from sklearn.datasets import fetch_california_housing


# %% [markdown] color=peach title="Step 1 — Import"
# # Step 1 — Import
#


# %% color=violet title="ds = fetch_california_housing(as_frame=True)"
# @explain: Run this cell to see the output.
ds = fetch_california_housing(as_frame=True)
df = ds.frame                  # the DataFrame: features + target
print(df.shape)
print("target column:", ds.target_names[0])
df.head()


# %% [markdown] color=amber title="Column meanings**"
# # Column meanings**
#
# **Column meanings** (from the dataset docs):
#
# | Column | Meaning |
# |---|---|
# | `MedInc` | median income (block group), \$10k units |
# | `HouseAge` | median house age |
# | `AveRooms` | avg rooms per household |
# | `AveBedrms` | avg bedrooms per household |
# …


# %% [markdown] color=rose title="Step 2 — Clean"
# # Step 2 — Clean
#
# Run the standard inspection ritual.


# %% color=lime title="df.info()"
# @explain: Run this cell to see the output.
df.info()


# %% color=teal title="print('missing:'"
# @explain: Run this cell to see the output.
print("missing:", df.isna().sum().sum())
print(df.describe().round(2).T)


# %% [markdown] color=sky title="No missing values — clean data"
# # No missing values — clean data
#
# No missing values — clean data. But `AveRooms`, `AveBedrms`, `Population`, `AveOccup` have huge max values (likely outliers). We'll keep them for now and see if the model handles them with regularisation.


# %% [markdown] color=mint title="Step 3 — Explore"
# # Step 3 — Explore
#
# Distribution of the target, correlations, geography.


# %% color=peach title="fig"
# @explain: Run this cell to see the output.
fig, ax = plt.subplots(1, 2, figsize=(11, 3))
df["MedHouseVal"].plot.hist(bins=40, ax=ax[0], edgecolor="white")
ax[0].set_title("Distribution of target — MedHouseVal")
df["MedInc"].plot.hist(bins=40, ax=ax[1], edgecolor="white")
ax[1].set_title("Distribution of MedInc (income)")
plt.tight_layout(); plt.show()


# %% color=violet title="corr = df.corr()"
# @explain: Run this cell to see the output.
corr = df.corr()
plt.figure(figsize=(8, 6))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0)
plt.title("Correlation matrix"); plt.show()
print("\ntop correlations with target:")
print(corr["MedHouseVal"].drop("MedHouseVal").sort_values(ascending=False))


# %% color=amber title="Geography"
# @explain: Geography — value vs location
# Geography — value vs location
plt.figure(figsize=(7, 6))
sc = plt.scatter(df["Longitude"], df["Latitude"],
                 c=df["MedHouseVal"], cmap="viridis", alpha=.4, s=10)
plt.colorbar(sc, label="median house value")
plt.title("California — house value by location")
plt.xlabel("longitude"); plt.ylabel("latitude"); plt.show()


# %% [markdown] color=rose title="Three findings so far"
# # Three findings so far
#
# **Three findings so far:**
#
# 1. Target is right-skewed and is **clipped at 5.0** (a known artefact — values were capped).
# 2. `MedInc` has the strongest positive correlation with the target — wealthier areas, pricier homes.
# 3. Coastal locations (San Francisco, LA) have the highest values — geography matters a lot.


# %% [markdown] color=lime title="Step 4 — Model"
# # Step 4 — Model
#
# Start simple — multiple linear regression. Then try Ridge with hyperparameter tuning. Then a non-linear model (Random Forest) for comparison.


# %% color=teal title="Baseline: linear regression"
# @explain: Baseline: linear regression
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor

X = df.drop(columns="MedHouseVal")
y = df["MedHouseVal"].values
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)

# Baseline: linear regression
lr = Pipeline([("scaler", StandardScaler()), ("lr", LinearRegression())])
print(f"Linear Regression CV R²: {cross_val_score(lr, X, y, cv=5).mean():.3f}")


# %% color=sky title="Ridge with hyperparameter tuning"
# @explain: Ridge with hyperparameter tuning
# Ridge with hyperparameter tuning
ridge = Pipeline([("scaler", StandardScaler()), ("m", Ridge())])
g = GridSearchCV(ridge, {"m__alpha": [0.01, 0.1, 1, 10, 100, 1000]},
                 cv=5, scoring="r2").fit(X_tr, y_tr)
print(f"Ridge best α: {g.best_params_['m__alpha']}, CV R²: {g.best_score_:.3f}")


# %% color=mint title="Non-linear comparison: Random Forest"
# @explain: Non-linear comparison: Random Forest
# Non-linear comparison: Random Forest
rf = RandomForestRegressor(n_estimators=100, n_jobs=-1, random_state=0)
print(f"Random Forest CV R²: {cross_val_score(rf, X, y, cv=5).mean():.3f}")


# %% [markdown] color=peach title="Step 5 — Evaluate the winning model"
# # Step 5 — Evaluate the winning model
#


# %% color=violet title="from sklearn.metrics import mean_squared_error"
# @explain: Run this cell to see the output.
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

rf.fit(X_tr, y_tr)
y_pred = rf.predict(X_te)
mse = mean_squared_error(y_te, y_pred)
print(f"Test RMSE : {np.sqrt(mse):.3f}  (units: $100k)")
print(f"Test MAE  : {mean_absolute_error(y_te, y_pred):.3f}")
print(f"Test R²   : {r2_score(y_te, y_pred):.3f}")


# %% color=amber title="Diagnostics"
# @explain: Diagnostics
# Diagnostics
fig, ax = plt.subplots(1, 2, figsize=(12, 4))
ax[0].scatter(y_te, y_pred, alpha=.3, s=10)
ax[0].plot([y_te.min(), y_te.max()], [y_te.min(), y_te.max()], "r--")
ax[0].set(xlabel="actual", ylabel="predicted", title="Predicted vs actual")

ax[1].scatter(y_pred, y_te - y_pred, alpha=.3, s=10)
ax[1].axhline(0, color="red", linestyle="--")
ax[1].set(xlabel="predicted", ylabel="residual", title="Residuals")
plt.tight_layout(); plt.show()


# %% [markdown] color=rose title="Feature importances (from Random Forest)"
# # Feature importances (from Random Forest)
#


# %% color=lime title="importances = pd.Series(rf.feature_importances_"
# @explain: Run this cell to see the output.
importances = pd.Series(rf.feature_importances_, index=X.columns).sort_values()
importances.plot.barh(figsize=(7, 4), title="Feature importances")
plt.tight_layout(); plt.show()
print(importances.round(3))


# %% [markdown] color=teal title="Step 6 — Communicate the findings (the one-page memo)"
# # Step 6 — Communicate the findings (the one-page memo)
#
# ### Question
# > *Can we predict the median house value of a California census block from demographic and geographic features?*
#
# ### Answer
# **Yes** — a Random Forest regressor trained on 8 features predicts median house values with
# **R² ≈ 0.80** on a held-out 20% test set, which is a strong fit.
# …


# %% [markdown] color=sky title="You finished the 16-module roadmap"
# # You finished the 16-module roadmap
#
# | Track | Modules | What you can do |
# |---|---|---|
# | **Python for DS** | M1-5 | Write modular Python; load CSV/JSON; call APIs; scrape HTML |
# | **Visualization** | M6-10 | Pick the right chart; build dashboards; tell a data story |
# | **Data Analysis & ML** | M11-16 | Clean → explore → model → evaluate → communicate |
#
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


