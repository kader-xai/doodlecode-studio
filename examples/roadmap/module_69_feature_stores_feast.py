# doodlecode format-version: 2
# Auto-converted from module_69_feature_stores_feast.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 69 Feature Stores Feast"
# # Module 69 Feature Stores Feast
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 69 — Feature Stores"
# # Module 69 — Feature Stores
#
# > A model trained on `user_avg_purchase_last_30d` will silently break the day production serves it a *slightly different* version of that same feature — re-implemented in a different language, computed over a slightly different window, missing the last-hour update. This is **training-serving skew**, the most expensive bug in classical ML. **Feature stores** solve it: define a feature **once**, serve the same value to training and online inference.
# >
# > This module walks the canonical open-source one — **Feast** — and shows when you actually need a feature store (often you don't).
#
# ### What you'll cover
# 1. The training-serving skew problem (and why it's invisible)
# …


# %% [markdown] color=mint title="1 · The training-serving skew problem"
# # 1 · The training-serving skew problem
#
# Imagine a fraud-detection model that uses these features:
#
# | Feature | Training-time source | Production source |
# |---|---|---|
# | `user_avg_purchase_last_30d` | Spark job on the data warehouse | Online API computing on the last 30 days of Postgres |
# | `user_country` | Snowflake `users` table | Microservice that returns the *current* country |
# …


# %% [markdown] color=peach title="2 · The three layers of a feature store"
# # 2 · The three layers of a feature store
#
# ```
#    ┌─────────────────────── REGISTRY ───────────────────────┐
#    │  Single source of truth for feature definitions        │
#    │  - feature view names, schemas, owners, descriptions   │
#    │  - lineage (which Snowflake table feeds which feature) │
#    └────────────────────────────────────────────────────────┘
# …


# %% [markdown] color=violet title="3 · Feast setup"
# # 3 · Feast setup
#


# %% color=amber title="!pip -q install 'feast[redis]' pandas pyarrow"
# @explain: Run this cell to see the output.
!pip -q install "feast[redis]" pandas pyarrow


# %% color=rose title="Initialise a fresh Feast repo"
# @explain: Initialise a fresh Feast repo
# Initialise a fresh Feast repo
import subprocess, os
os.makedirs("/content/feast_demo", exist_ok=True)
res = subprocess.run(
    ["feast","init","fraud","--minimal"],
    cwd="/content/feast_demo", capture_output=True, text=True,
)
print(res.stdout)
print(res.stderr)


# %% [markdown] color=lime title="`feast init` creates"
# # `feast init` creates
#
# `feast init` creates:
# ```
# fraud/
#   feature_store.yaml      # registry/online/offline backend config
#   example_repo.py         # your feature definitions
#   data/                    # parquet files for the demo
# ```
#
# …


# %% [markdown] color=teal title="4 · Entities, FeatureViews, Fields"
# # 4 · Entities, FeatureViews, Fields
#


# %% color=sky title="fraud/repo.py"
# @explain: fraud/repo.py — the feature definitions
# @explain: 1
# @explain: 2
# @explain: 3
defs_py = '''
# fraud/repo.py — the feature definitions
from datetime import timedelta
from feast import Entity, Feature, FeatureView, Field, FileSource, ValueType
from feast.types import Float32, Int64, String

# 1. ENTITY — the thing features describe (a user, a merchant, an item).
user = Entity(name="user_id", value_type=ValueType.INT64,
              description="Unique user id")

# 2. SOURCE — where the raw, time-stamped data comes from
purchases_source = FileSource(
    path="data/purchases.parquet",
    timestamp_field="event_ts",     # the event time — critical for point-in-time correctness
    created_timestamp_column="created_ts",   # when the row landed (optional)
)

# 3. FEATURE VIEW — group of features that share an entity + source
user_purchases_30d = FeatureView(
    name="user_purchases_30d",
    entities=[user],
    ttl=timedelta(days=7),        # how long online-store values stay fresh
    schema=[
        Field(name="avg_purchase_30d",  dtype=Float32),
        Field(name="count_purchase_30d", dtype=Int64),
        Field(name="last_country",       dtype=String),
    ],
    source=purchases_source,
    online=True,                  # push these into the online store
    tags={"team": "fraud", "owner": "kim@example.com"},
)
'''
print(defs_py)


# %% [markdown] color=mint title="Three nouns you'll see in every feature store"
# # Three nouns you'll see in every feature store
#
# **Three nouns you'll see in every feature store.**
#
# | Concept | Definition | Example |
# |---|---|---|
# | **Entity** | the thing features describe | `user_id`, `merchant_id`, `device_id` |
# | **Feature View** | a group of features that share an entity + a source | `user_purchases_30d` |
# | **Field** | one column with a typed dtype | `avg_purchase_30d: Float32` |
#
# …


# %% [markdown] color=peach title="5 · Point-in-time correctness — the unsexy core feature"
# # 5 · Point-in-time correctness — the unsexy core feature
#
# Suppose at training time you want, for **row (user=42, event_ts=2024-08-15 10:00 UTC)**, the value of `avg_purchase_30d` **as known on that exact day**. The naive approach is dangerous:
#
# ```sql
# -- BAD: leaks future data into training!
# SELECT user_id, AVG(amount) AS avg_purchase_30d
# FROM purchases
# …


# %% color=violet title="An 'entity dataframe'"
# @explain: An "entity dataframe" — one row per training example
hist_call = '''
import pandas as pd
from feast import FeatureStore

store = FeatureStore(repo_path="fraud")

# An "entity dataframe" — one row per training example
entity_df = pd.DataFrame({
    "user_id":   [42, 42, 18],
    "event_ts":  [
        pd.Timestamp("2024-08-15 10:00", tz="UTC"),
        pd.Timestamp("2024-09-01 18:30", tz="UTC"),
        pd.Timestamp("2024-08-30 12:00", tz="UTC"),
    ],
})

training_df = store.get_historical_features(
    entity_df=entity_df,
    features=[
        "user_purchases_30d:avg_purchase_30d",
        "user_purchases_30d:count_purchase_30d",
        "user_purchases_30d:last_country",
    ],
).to_df()
'''
print(hist_call)


# %% [markdown] color=amber title="Internally**, Feast issues an `AS OF` join: for…"
# # Internally**, Feast issues an `AS OF` join: for…
#
# **Internally**, Feast issues an `AS OF` join: for each `(user_id, event_ts)` row in your entity dataframe, it grabs the **latest feature value with `feature_event_ts <= entity_event_ts`**. No leakage. Period.
#
# This is the single most important thing a feature store does. Without it, every team eventually invents an `AS OF` join in dbt or Spark and gets it slightly wrong.


# %% [markdown] color=rose title="6 · `feast apply` → `materialize` → online serving"
# # 6 · `feast apply` → `materialize` → online serving
#
# ```bash
# # 1. Register your definitions (creates / updates the registry)
# $ feast apply
#
# # 2. Materialise feature values into the online store
# $ feast materialize \
# …


# %% color=lime title="At inference time, this is ~1 ms"
# @explain: At inference time, this is ~1 ms — a Redis lookup keyed by user_id
online_call = '''
features = store.get_online_features(
    features=[
        "user_purchases_30d:avg_purchase_30d",
        "user_purchases_30d:count_purchase_30d",
        "user_purchases_30d:last_country",
    ],
    entity_rows=[{"user_id": 42}, {"user_id": 18}],
).to_dict()

# At inference time, this is ~1 ms — a Redis lookup keyed by user_id.
print(features)
'''
print(online_call)


# %% [markdown] color=teal title="Same Python call shape** in training and serving"
# # Same Python call shape** in training and serving
#
# **Same Python call shape** in training and serving. Same feature names. **Same logic.** Skew gone.
#
# > 🔄 Most teams run **`feast materialize-incremental`** as an Airflow / Prefect / Dagster (M68) task every N minutes for fresh-enough features. Real-time streaming features (next section) bypass batch entirely.


# %% [markdown] color=sky title="7 · Hosted alternatives"
# # 7 · Hosted alternatives
#
# | Tool | Notes |
# |---|---|
# | **Feast** (OSS) | the canonical OSS feature store; **you run the infra** |
# | **Tecton** | enterprise commercial Feast cousin; same model + managed + streaming compute layer |
# | **Hopsworks** | OSS + commercial; strong online store + model registry combo |
# | **Vertex AI Feature Store** | Google Cloud native; BigQuery offline + Bigtable online |
# …


# %% [markdown] color=mint title="8 · Streaming features"
# # 8 · Streaming features
#
# Some features can't wait for a nightly batch — fraud features (`count_logins_last_5min`), real-time recsys (`items_viewed_in_session`), live bidding (`current_user_intent`). Two patterns:
#
# ### Push to online store
# Your stream processor (Flink / Spark Streaming / Materialize / Kafka Streams) writes directly to the online store keyed by entity. Feast's "push API" then exposes the values:
#
# ```python
# …


# %% [markdown] color=peach title="9 · Feature stores for LLM / RAG apps"
# # 9 · Feature stores for LLM / RAG apps
#
# Feature stores aren't only for tabular ML. For LLM apps in 2025 they take three shapes:
#
# | Use | What goes in the store |
# |---|---|
# | **User profile features for personalised RAG** | `last_purchase_category`, `tier`, `language_preference`, `recent_topics` |
# | **Session signals** | last N user messages, ongoing tool-call results, time-of-day |
# …


# %% [markdown] color=violet title="10 · Do you actually need a feature store?"
# # 10 · Do you actually need a feature store?
#
# **Most teams don't.** Set a feature store up too early and you ship slower without the skew problem to justify the complexity. The decision tree:
#
# ```
# Do features come from > 1 system (warehouse + microservice + stream)?
#    │
#    ├─ No  → just compute in your training job; you don't need a feature store.
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


