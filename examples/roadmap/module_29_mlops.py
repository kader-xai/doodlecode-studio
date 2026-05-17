# doodlecode format-version: 2
# Auto-converted from module_29_mlops.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 29 Mlops"
# # Module 29 Mlops
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 29 — MLOps: From Notebook to Revenue"
# # Module 29 — MLOps: From Notebook to Revenue
#
# > A model that lives only in a notebook generates **zero revenue**. MLOps is the engineering work that turns a `.fit()` call into an API your product can call. This module covers the four pieces every team needs: serving, packaging, experiment tracking, and monitoring.
#
# ### What you'll cover
# 1. The MLOps landscape — what each piece does
# 2. Train and **persist** a model with `joblib`
# 3. **FastAPI** — wrap the model in an HTTP endpoint
# …


# %% [markdown] color=mint title="1 · The MLOps Landscape"
# # 1 · The MLOps Landscape
#
# | Piece | What it does | Tool we use |
# |---|---|---|
# | **Serving** | turn a model into an HTTP endpoint | FastAPI + uvicorn |
# | **Packaging** | bundle code + deps + model into a portable artefact | Docker |
# | **Experiment tracking** | log every training run; compare metrics; reproduce | MLflow |
# | **Model registry** | versioned 'staging' / 'production' model store | MLflow registry |
# …


# %% color=peach title="!pip -q install fastapi uvicorn[standard] httpx…"
# @explain: Run this cell to see the output.
!pip -q install fastapi uvicorn[standard] httpx mlflow joblib scikit-learn pydantic
import joblib, json, os, pickle, time
import numpy as np, pandas as pd, matplotlib.pyplot as plt
import warnings; warnings.filterwarnings("ignore")


# %% [markdown] color=violet title="2 · Train + Persist a Model"
# # 2 · Train + Persist a Model
#
# Every deployment starts with a TRAINED model saved to disk. We'll use `joblib` (faster than pickle for NumPy-heavy models).


# %% color=amber title="Persist model + the feature names"
# @explain: Persist model + the feature names (we'll need them at inference)
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, roc_auc_score

data = load_breast_cancer(as_frame=True)
X, y = data.data, data.target
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

model = RandomForestClassifier(n_estimators=200, n_jobs=-1, random_state=0).fit(X_tr, y_tr)
print(f"acc={accuracy_score(y_te, model.predict(X_te)):.4f}",
      f"auc={roc_auc_score(y_te, model.predict_proba(X_te)[:,1]):.4f}")

# Persist model + the feature names (we'll need them at inference)
os.makedirs("/tmp/artifacts", exist_ok=True)
joblib.dump(model, "/tmp/artifacts/model.joblib")
with open("/tmp/artifacts/features.json", "w") as f:
    json.dump(list(X.columns), f)
print("saved →", os.listdir("/tmp/artifacts"))


# %% [markdown] color=rose title="3 · FastAPI Service — Wrap the Model in an HTTP Endpoint"
# # 3 · FastAPI Service — Wrap the Model in an HTTP Endpoint
#
# FastAPI is the modern Python web framework. Two big wins:
# 1. **Auto-generated OpenAPI / Swagger docs** at `/docs` — every endpoint testable from the browser.
# 2. **Pydantic validation** — bad inputs get rejected with helpful error messages, no extra code.


# %% color=lime title="Write the FastAPI app to a file so Docker can pick…"
# @explain: Write the FastAPI app to a file so Docker can pick it up later
# Write the FastAPI app to a file so Docker can pick it up later.
app_code = """
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List
import joblib, json, os

ARTIFACTS = os.environ.get("ARTIFACTS_DIR", "/tmp/artifacts")
model = joblib.load(f"{ARTIFACTS}/model.joblib")
with open(f"{ARTIFACTS}/features.json") as f:
    FEATURES = json.load(f)

app = FastAPI(title="Cancer-classifier API", version="1.0")

class PredictRequest(BaseModel):
    features: List[float] = Field(..., description=f"List of {len(FEATURES)} floats in fixed order")

class PredictResponse(BaseModel):
    label: int
    label_name: str
    proba: float

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/features")
def get_features():
    return {"features": FEATURES, "count": len(FEATURES)}

@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    if len(req.features) != len(FEATURES):
        return {"label": -1, "label_name": "error",
                "proba": 0.0}  # in production, raise HTTPException
    proba = float(model.predict_proba([req.features])[0, 1])
    label = int(proba >= 0.5)
    return PredictResponse(
        label=label,
        label_name="benign" if label == 1 else "malignant",
        proba=proba)
"""

with open("/tmp/artifacts/app.py", "w") as f:
    f.write(app_code)
print("wrote /tmp/artifacts/app.py")


# %% [markdown] color=teal title="Test the API in-process with `TestClient`"
# # Test the API in-process with `TestClient`
#
# `TestClient` lets us call our FastAPI app directly inside Python, no separate server needed — perfect for tests AND for Colab.


# %% color=sky title="/health"
# @explain: /health
# @explain: /features
# @explain: /predict — pass one row from the test set
import sys
sys.path.insert(0, "/tmp/artifacts")
import importlib, app as app_module
importlib.reload(app_module)

from fastapi.testclient import TestClient
client = TestClient(app_module.app)

# /health
print("/health      :", client.get("/health").json())

# /features
print("/features cnt:", client.get("/features").json()["count"])

# /predict — pass one row from the test set
sample = X_te.iloc[0].tolist()
resp = client.post("/predict", json={"features": sample})
print("/predict     :", resp.json())


# %% [markdown] color=mint title="Running the server for real (locally)"
# # Running the server for real (locally)
#
# ```bash
# cd /tmp/artifacts
# uvicorn app:app --host 0.0.0.0 --port 8000 --reload
# # Then open http://localhost:8000/docs in your browser
# ```


# %% [markdown] color=peach title="4 · Docker — Package the Whole Thing"
# # 4 · Docker — Package the Whole Thing
#
# Docker bundles your code + Python + dependencies + model artefacts into a **single portable image**. Same container runs identically on your laptop, CI, AWS, GCP, your friend's Mac.


# %% color=violet title="1"
# @explain: 1
# @explain: 2
dockerfile = """
FROM python:3.11-slim

WORKDIR /app

# 1. Install Python deps first (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Copy artefacts + app
COPY artifacts/ /app/artifacts/

ENV ARTIFACTS_DIR=/app/artifacts
EXPOSE 8000

CMD ["uvicorn", "artifacts.app:app", "--host", "0.0.0.0", "--port", "8000"]
"""

requirements = """
fastapi==0.110.0
uvicorn[standard]==0.27.1
scikit-learn==1.4.0
joblib==1.3.2
pydantic==2.6.1
numpy==1.26.4
"""

with open("/tmp/Dockerfile", "w") as f: f.write(dockerfile.strip())
with open("/tmp/requirements.txt", "w") as f: f.write(requirements.strip())
print("wrote /tmp/Dockerfile and /tmp/requirements.txt")


# %% [markdown] color=amber title="Build & run (on your laptop)"
# # Build & run (on your laptop)
#
# ```bash
# # Layout:
# #   /your_project/
# #     Dockerfile
# #     requirements.txt
# #     artifacts/        ← contains model.joblib, features.json, app.py
# …


# %% [markdown] color=rose title="5 · MLflow — Track Every Experiment"
# # 5 · MLflow — Track Every Experiment
#
# You'll train a model dozens of times before shipping it. **Without MLflow you'll lose track of which config gave the best AUC.** Three calls log everything you need.


# %% color=lime title="Try a small grid"
# @explain: Try a small grid
import mlflow, mlflow.sklearn

mlflow.set_tracking_uri("file:/tmp/mlruns")
mlflow.set_experiment("cancer-classifier")

def train_run(n_estimators, max_depth, run_name):
    with mlflow.start_run(run_name=run_name):
        m = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth,
                                    n_jobs=-1, random_state=0).fit(X_tr, y_tr)
        proba = m.predict_proba(X_te)[:, 1]
        acc = accuracy_score(y_te, m.predict(X_te))
        auc = roc_auc_score(y_te, proba)

        mlflow.log_params({"n_estimators": n_estimators, "max_depth": max_depth})
        mlflow.log_metrics({"accuracy": acc, "roc_auc": auc})
        mlflow.sklearn.log_model(m, name="model")
        print(f"  {run_name}: acc={acc:.4f}, auc={auc:.4f}")

# Try a small grid
for n in [50, 200, 500]:
    for d in [None, 5, 10]:
        train_run(n_estimators=n, max_depth=d, run_name=f"rf_n{n}_d{d}")


# %% color=teal title="Inspect the logged runs"
# @explain: Inspect the logged runs
# Inspect the logged runs
runs = mlflow.search_runs(experiment_names=["cancer-classifier"])
print(runs[["run_id", "params.n_estimators", "params.max_depth",
            "metrics.accuracy", "metrics.roc_auc"]]
      .sort_values("metrics.roc_auc", ascending=False)
      .head())


# %% [markdown] color=sky title="Launching the MLflow UI"
# # Launching the MLflow UI
#
# ```bash
# mlflow ui --backend-store-uri file:/tmp/mlruns --host 0.0.0.0 --port 5000
# # Open http://localhost:5000 — interactive comparison, parallel-coordinates plot
# ```
#
# ### Model registry — promote the winner
# …


# %% [markdown] color=mint title="6 · Monitoring — Catch Drift Before Customers Do"
# # 6 · Monitoring — Catch Drift Before Customers Do
#
# A deployed model degrades silently when the **input distribution shifts** (new product launch, seasonality, broken upstream feed). Three things to monitor:
#
# | Drift type | Detect with | Action |
# |---|---|---|
# | **Input drift** | KS test or Population Stability Index (PSI) per feature | flag, investigate, maybe retrain |
# | **Output drift** | shift in average predicted class / score distribution | symptom of input drift, often easier to monitor |
# …


# %% color=peach title="Reference = training data"
# @explain: Reference = training data
# @explain: Simulated 'current' production data — same distribution (no drift)
# @explain: Simulated 'current' with INDUCED DRIFT — shift the mean of 5 features
from scipy import stats

def ks_drift(reference, current, alpha=0.01):
    """Kolmogorov-Smirnov test per feature. Returns dict with p-value and drift flag."""
    out = {}
    for col in reference.columns:
        stat, pval = stats.ks_2samp(reference[col], current[col])
        out[col] = {"p_value": pval, "drift": pval < alpha}
    return pd.DataFrame(out).T

# Reference = training data
reference = X_tr.copy()

# Simulated 'current' production data — same distribution (no drift)
current_clean = X_te.copy()

# Simulated 'current' with INDUCED DRIFT — shift the mean of 5 features
current_drift = X_te.copy()
drifted_cols = current_drift.columns[:5]
current_drift[drifted_cols] += current_drift[drifted_cols].mean().values * 0.30

print("=== no drift ===")
print(ks_drift(reference, current_clean).head())

print("\n=== with induced drift on first 5 features ===")
flagged = ks_drift(reference, current_drift)
print(flagged.head(7))
print(f"\nFeatures flagged for drift: {flagged['drift'].sum()} / {len(flagged)}")


# %% [markdown] color=violet title="Population Stability Index (PSI) — the industry default"
# # Population Stability Index (PSI) — the industry default
#
# PSI bins each feature, compares the distribution between reference and current, and returns a single number per feature:
#
# | PSI | Verdict |
# |---|---|
# | < 0.1 | no significant change |
# | 0.1 - 0.25 | small change — investigate |
# …


# %% color=amber title="def psi(reference"
# @explain: Run this cell to see the output.
def psi(reference, current, bins=10):
    """Population Stability Index — works for one feature at a time."""
    cuts = np.histogram_bin_edges(reference, bins=bins)
    cuts[0]  = -np.inf
    cuts[-1] = np.inf
    ref_cnts, _ = np.histogram(reference, bins=cuts)
    cur_cnts, _ = np.histogram(current,   bins=cuts)
    ref_p = (ref_cnts + 1e-6) / ref_cnts.sum()
    cur_p = (cur_cnts + 1e-6) / cur_cnts.sum()
    return float(((cur_p - ref_p) * np.log(cur_p / ref_p)).sum())

scores = pd.DataFrame({
    "feature": reference.columns,
    "psi_clean":  [psi(reference[c], current_clean[c]) for c in reference.columns],
    "psi_drift":  [psi(reference[c], current_drift[c]) for c in reference.columns],
})
print(scores.head(10).round(3))


# %% color=rose title="Output drift"
# @explain: Output drift — easier to monitor; one number for the whole model
# Output drift — easier to monitor; one number for the whole model
ref_score = model.predict_proba(reference)[:, 1]
cur_score_clean = model.predict_proba(current_clean)[:, 1]
cur_score_drift = model.predict_proba(current_drift)[:, 1]

fig, ax = plt.subplots(figsize=(8, 3))
ax.hist(ref_score,        bins=30, alpha=.5, label="reference", color="steelblue")
ax.hist(cur_score_clean,  bins=30, alpha=.4, label="current — no drift", color="green")
ax.hist(cur_score_drift,  bins=30, alpha=.4, label="current — drift!",   color="red")
ax.legend(); ax.set(xlabel="predicted probability of benign", title="Output-score drift")
plt.show()

print("PSI of OUTPUT scores (clean vs drift):",
      round(psi(ref_score, cur_score_clean), 3),
      "vs",
      round(psi(ref_score, cur_score_drift), 3))


# %% [markdown] color=lime title="7 · The Full Deployment Lifecycle"
# # 7 · The Full Deployment Lifecycle
#
# ```
# TRAIN  →  TRACK  →  REGISTER  →  PACKAGE  →  DEPLOY  →  SERVE  →  MONITOR  →  RETRAIN
#  (M14-15) (mlflow) (registry) (Docker)    (k8s)     (FastAPI)   (drift)     (loop)
# ```
#
# ### CI/CD for ML — typical GitHub-Actions workflow
# …


# %% [markdown] color=teal title="8 · Where This Scales"
# # 8 · Where This Scales
#
# | Need | Tool |
# |---|---|
# | Multi-model serving with auto-scaling | **BentoML**, **KServe**, **Triton Inference Server** |
# | Cluster orchestration | **Kubernetes** (with Helm charts for ML services) |
# | Pipeline orchestration | **Airflow**, **Prefect**, **Dagster** |
# | Drift detection & dashboards | **Evidently**, **Arize**, **Whylabs** |
# …


# %% [markdown] color=sky title="9 · Practice — Try Yourself"
# # 9 · Practice — Try Yourself
#
# 1. **/predict_batch** — extend the FastAPI app with a new endpoint `/predict_batch` that accepts a list of feature lists and returns a list of predictions.
# 2. **PSI threshold** — write a function `is_drifted(scores_dict, threshold=0.25)` that returns True if ANY feature's PSI exceeds the threshold.
# 3. **MLflow auto-pick** — query MLflow for the run with the highest test AUC, load the model, and run a prediction on `X_te.iloc[0]`.
# 4. **Health-check endpoint with model info** — extend `/health` to also return the model's class name, the number of features, and the last-modified time of `model.joblib`.


# %% color=mint title="Solution sketches"
# @explain: Solution sketches
# @explain: 2) PSI threshold check
# @explain: 3) Load the best MLflow model and predict
# Solution sketches

# 2) PSI threshold check
def is_drifted(scores, threshold=0.25):
    return any(v > threshold for v in scores.values())

scores_drift = {c: psi(reference[c], current_drift[c]) for c in reference.columns[:5]}
print("any drift?", is_drifted(scores_drift, threshold=0.25))

# 3) Load the best MLflow model and predict
runs = mlflow.search_runs(experiment_names=["cancer-classifier"])
best = runs.sort_values("metrics.roc_auc", ascending=False).iloc[0]
best_model = mlflow.sklearn.load_model(f"runs:/{best['run_id']}/model")
print("best AUC:", best["metrics.roc_auc"])
print("prediction on X_te[0]:", best_model.predict([X_te.iloc[0].tolist()]))


# %% [markdown] color=peach title="Recap"
# # Recap
#
# ✅ Persist a trained model with `joblib`
# ✅ Wrap a model in a **FastAPI** endpoint with Pydantic validation
# ✅ Test the API in-process with `TestClient`
# ✅ Write a **Dockerfile** that bakes the model into a portable image
# ✅ Track experiments + register a winning model with **MLflow**
# ✅ Detect input drift with the KS test and **PSI**, output drift with a histogram
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


