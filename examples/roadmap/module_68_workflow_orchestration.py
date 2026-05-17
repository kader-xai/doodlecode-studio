# doodlecode format-version: 2
# Auto-converted from module_68_workflow_orchestration.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 68 Workflow Orchestration"
# # Module 68 Workflow Orchestration
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 68 — Workflow Orchestration"
# # Module 68 — Workflow Orchestration
#
# > Every ML pipeline eventually has the same shape: **fetch raw data → clean → feature-engineer → train → evaluate → register → deploy**. Doing that once is a script. Doing it **every night at 3 AM with retries, alerts, lineage, and backfills** is a workflow orchestrator. This module is the map of the three Python options people actually use — **Airflow**, **Prefect**, and **Dagster** — plus the ML-native cousins (Argo Workflows, Kubeflow Pipelines, ZenML, Metaflow).
#
# ### What you'll cover
# 1. Why you need an orchestrator (the pain it removes)
# 2. The three core concepts: **DAGs, tasks, schedules**
# 3. **Airflow** — the original, operator-based, ubiquitous
# …


# %% [markdown] color=mint title="1 · Why orchestrate"
# # 1 · Why orchestrate
#
# Without an orchestrator, a "production pipeline" looks like:
#
# ```
#    crontab:  0 3 * * *  python /etc/scripts/train.py
# ```
#
# …


# %% [markdown] color=peach title="2 · The three concepts every orchestrator shares"
# # 2 · The three concepts every orchestrator shares
#
# | Term | What it is |
# |---|---|
# | **Task** (Airflow) / **Task** (Prefect) / **Op** + **Asset** (Dagster) | a unit of work — a Python function that runs on a schedule |
# | **DAG** (Directed Acyclic Graph) | the dependency graph between tasks — A → B → C |
# | **Schedule** | when to start a DAG run — cron, interval, "at midnight UTC daily", or event-driven |
# | **Sensor** / **Trigger** | wait for an external condition — a file landed in S3, a Kafka message, an HTTP webhook |
# …


# %% [markdown] color=violet title="3 · Airflow — the original"
# # 3 · Airflow — the original
#
# Born at Airbnb in 2014; the default orchestrator across every other company. Run by Apache; managed offerings from **Astronomer**, **Cloud Composer (GCP)**, **MWAA (AWS)**, **Azure Data Factory** (similar concept).


# %% color=amber title="dags/ml_pipeline.py"
# @explain: dags/ml_pipeline.py
airflow_dag = '''
# dags/ml_pipeline.py
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator

def extract():
    print("fetched 1000 rows")

def transform():
    print("cleaned them")

def train(model_name="rf"):
    print(f"trained {model_name}")

with DAG(
    dag_id="ml_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule="0 3 * * *",                    # 3 AM daily
    catchup=False,
    default_args={"retries": 3, "retry_delay": 300},   # 3 retries, 5 min apart
    tags=["ml"],
) as dag:
    t_extract   = PythonOperator(task_id="extract",   python_callable=extract)
    t_transform = PythonOperator(task_id="transform", python_callable=transform)
    t_train     = PythonOperator(task_id="train",     python_callable=train,
                                  op_kwargs={"model_name": "xgb"})

    t_extract >> t_transform >> t_train     # the >> operator defines the DAG
'''
print(airflow_dag)


# %% [markdown] color=rose title="What Airflow gets right"
# # What Airflow gets right
#
# **What Airflow gets right.**
# - **Ubiquitous** — every cloud has a managed Airflow.
# - **Huge operator library** — `PostgresOperator`, `S3ToRedshiftOperator`, `BigQueryOperator`, `KubernetesPodOperator` — wrappers for nearly every system.
# - **Mature UI** — gantt, graph, logs, retry buttons all in one place.
#
# **What Airflow gets wrong.**
# - DAGs are defined **at parse time** — dynamic structure (e.g. "one task per file") is awkward (TaskGroup helps, not enough).
# - Passing data between tasks goes through **XCom**, which is a small-payload key-value store. Big intermediate dataframes don't fit; you serialise to S3 manually.
# …


# %% [markdown] color=lime title="4 · Prefect — Python-first"
# # 4 · Prefect — Python-first
#


# %% color=teal title="flows/ml_pipeline.py"
# @explain: flows/ml_pipeline.py
# @explain: Deployment — registers schedule + infrastructure
prefect_flow = '''
# flows/ml_pipeline.py
from prefect import flow, task
from datetime import timedelta

@task(retries=3, retry_delay_seconds=300)
def extract():
    print("fetched 1000 rows")
    return 1000

@task
def transform(n_rows: int):
    print(f"cleaned {n_rows} rows")
    return n_rows

@task
def train(n_rows: int, model_name: str = "xgb"):
    print(f"trained {model_name} on {n_rows} rows")

@flow(name="ml_pipeline")
def ml_pipeline():
    n = extract()
    n = transform(n)
    train(n, model_name="xgb")

# Deployment — registers schedule + infrastructure
if __name__ == "__main__":
    ml_pipeline.serve(
        name="prod",
        cron="0 3 * * *",
    )
'''
print(prefect_flow)


# %% [markdown] color=sky title="What Prefect does differently"
# # What Prefect does differently
#
# **What Prefect does differently.**
# - **No DAG declaration** — the flow function *is* the DAG. Dependencies are inferred from how task return values flow.
# - **Dynamic** — `for f in files: process.submit(f)` just works. The DAG shape can depend on runtime data.
# - **Python types pass through** — no XCom, no S3 manual round-trip; results live in a configurable artefact store.
# - **Cleanest local dev experience** of the three — `prefect server start` and you have a UI in 30 seconds.
# - **`prefect-cloud`** is the canonical hosted offering (free tier).


# %% [markdown] color=mint title="5 · Dagster — asset-based"
# # 5 · Dagster — asset-based
#


# %% color=peach title="project/assets.py"
# @explain: project/assets.py
# @explain: project/definitions.py
dagster_assets = '''
# project/assets.py
from dagster import asset, AssetExecutionContext, AutoMaterializePolicy

@asset
def raw_rows():
    return list(range(1000))

@asset(deps=[raw_rows])
def clean_rows(raw_rows):
    return [r for r in raw_rows if r % 7 != 0]

@asset(auto_materialize_policy=AutoMaterializePolicy.eager())
def trained_model(clean_rows):
    print(f"training on {len(clean_rows)} rows")
    return "model_v3"

# project/definitions.py
from dagster import Definitions, ScheduleDefinition, define_asset_job
from . import assets

ml_job = define_asset_job("ml_pipeline", selection="*trained_model")
ml_sched = ScheduleDefinition(job=ml_job, cron_schedule="0 3 * * *")

defs = Definitions(assets=[assets.raw_rows, assets.clean_rows, assets.trained_model],
                   jobs=[ml_job], schedules=[ml_sched])
'''
print(dagster_assets)


# %% [markdown] color=violet title="Dagster's pitch.** Forget DAGs"
# # Dagster's pitch.** Forget DAGs
#
# **Dagster's pitch.** Forget DAGs. Define your **assets** (datasets, models, dashboards). The framework computes the DAG by reading dependencies between assets.
#
# **Why this matters for ML.**
# - An asset is a **typed, versioned, observable object**. The UI shows you when each was last materialised and what depends on it.
# - "Re-materialise the model whenever the cleaned data changes" is **declarative** (`AutoMaterializePolicy.eager()`) — no manual scheduling.
# - **Lineage** — for every model artefact, Dagster shows the upstream code commits + data versions that produced it.
# - Best in class for **data-quality-driven** ML pipelines.
#
# …


# %% [markdown] color=amber title="6 · ML-native orchestrators (when k8s is your home)"
# # 6 · ML-native orchestrators (when k8s is your home)
#
# If your platform is Kubernetes (M46), three more options worth knowing:
#
# | Tool | Mental model | When to pick |
# |---|---|---|
# | **Argo Workflows** | step DAG in YAML, each step is a container | k8s-native, no Python required for orchestration |
# | **Kubeflow Pipelines** | Argo + Python SDK + experiment tracking | ML-first; tight Vertex AI integration |
# …


# %% color=rose title="argo-workflow.yaml"
# @explain: argo-workflow.yaml — one workflow, two steps
argo_yaml = '''
# argo-workflow.yaml — one workflow, two steps
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata: { generateName: ml-pipeline- }
spec:
  entrypoint: pipeline
  templates:
  - name: pipeline
    dag:
      tasks:
      - name: extract
        template: run-script
        arguments: { parameters: [{name: cmd, value: "python extract.py"}] }
      - name: train
        dependencies: [extract]
        template: run-script
        arguments: { parameters: [{name: cmd, value: "python train.py"}] }
  - name: run-script
    inputs: { parameters: [{name: cmd}] }
    container:
      image: my-org/ml:1.3.0
      command: ["sh","-c","{{inputs.parameters.cmd}}"]
'''
print(argo_yaml)


# %% [markdown] color=lime title="7 · Retries, alerts, idempotency, backfills"
# # 7 · Retries, alerts, idempotency, backfills
#
# Five concerns every orchestrator must solve:
#
# ### Retries
# - Set a default `retries=3, retry_delay=5min` per task.
# - **Exponential backoff** for flaky external APIs.
# - **Don't** retry on user-error (wrong schema) — fail fast.
# …


# %% [markdown] color=teal title="8 · Lineage + observability + cost"
# # 8 · Lineage + observability + cost
#
# **Lineage** — what data + code produced this artefact.
# - Dagster has it built in (asset graph).
# - Airflow: bolt on **OpenLineage** → emit events to **Marquez** / **DataHub** / **Atlan**.
# - Prefect: similar via OpenLineage integration.
#
# **Observability** — what ran, how long, why it failed.
# …


# %% [markdown] color=sky title="9 · The simplest alternative — cron + a single script"
# # 9 · The simplest alternative — cron + a single script
#
# Before reaching for Airflow, ask: **is your pipeline three tasks that run nightly and never branch?**
#
# ```
#    crontab:  0 3 * * *  /opt/ml/run_nightly.sh
# ```
#
# …


# %% [markdown] color=mint title="10 · Decision table — pick your orchestrator"
# # 10 · Decision table — pick your orchestrator
#
# | You are… | Pick |
# |---|---|
# | Already an Airflow shop with managed Composer / MWAA | **Airflow** — don't fix what isn't broken |
# | Greenfield Python team, want clean local dev + dynamic flows | **Prefect** |
# | Data-platform team wanting lineage + asset versioning | **Dagster** |
# | Kubernetes-first ML platform, comfortable with YAML | **Argo Workflows** (often + Kubeflow) |
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


