# doodlecode format-version: 2
# Auto-converted from module_73_spark_delta_lake.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 73 Spark Delta Lake"
# # Module 73 Spark Delta Lake
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 73 — Spark + Delta Lake"
# # Module 73 — Spark + Delta Lake
#
# > The whole course assumes a Pandas-shaped dataframe fits in memory. **Production data doesn't.** A real ML platform reads from terabytes of event logs, joins to billions of user rows, materialises features (M69), and feeds the result to training (M57) and serving (M44, M71). The dominant tool for that since 2010 has been **Apache Spark**. The 2020s sequel — **Delta Lake** — bolts ACID transactions onto raw Parquet files, turning a data lake into a database. Together they are the **lakehouse**: cheap object storage + warehouse-grade SQL.
# >
# > This is the final module of the course. By the end you can ingest, transform, version, and merge data at any scale.
#
# ### What you'll cover
# 1. Why distributed data processing (the memory wall)
# …


# %% [markdown] color=mint title="1 · The memory wall"
# # 1 · The memory wall
#
# | Tool | Comfortable up to | Past that |
# |---|---|---|
# | Pandas (M2) | ~1 GB / 10 M rows | swap → OOM |
# | **Polars** | ~50 GB on one machine (out-of-core) | needs a cluster |
# | **DuckDB** | terabytes on one machine, single-process | analytic queries only |
# | **Spark** | petabytes across many machines | the answer at scale |
# …


# %% [markdown] color=peach title="2 · Spark architecture in one picture"
# # 2 · Spark architecture in one picture
#
# ```
#                     ┌─────────── DRIVER ───────────┐
#                     │  - your Python / Scala / SQL │
#                     │  - builds the logical plan   │
#                     │  - schedules stages          │
#                     │  - collects results          │
# …


# %% [markdown] color=violet title="3 · PySpark in Colab + the DataFrame API"
# # 3 · PySpark in Colab + the DataFrame API
#


# %% color=amber title="!pip -q install pyspark==3.5.3 delta-spark==3.2.1"
# @explain: Run this cell to see the output.
!pip -q install pyspark==3.5.3 delta-spark==3.2.1


# %% color=rose title="In production you'd connect to a Databricks / EMR /…"
# @explain: In production you'd connect to a Databricks / EMR / GKE Dataproc cluster
# @explain: Here we run a local single-machine Spark inside Colab — same API
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

# In production you'd connect to a Databricks / EMR / GKE Dataproc cluster.
# Here we run a local single-machine Spark inside Colab — same API.
spark = (SparkSession.builder
         .appName("course_demo")
         .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
         .config("spark.sql.catalog.spark_catalog",
                 "org.apache.spark.sql.delta.catalog.DeltaCatalog")
         .config("spark.jars.packages", "io.delta:delta-spark_2.12:3.2.1")
         .getOrCreate())
spark.sparkContext.setLogLevel("WARN")
print(spark.version)


# %% color=lime title="Make some toy data"
# @explain: Make some toy data
# Make some toy data
import pandas as pd, random, datetime as dt
random.seed(0)

rows = []
for i in range(50_000):
    rows.append({
        "user_id":  random.randint(1, 1_000),
        "amount":   round(random.uniform(1, 500), 2),
        "country":  random.choice(["US","DE","IN","BR","JP"]),
        "event_ts": dt.datetime(2024,1,1) + dt.timedelta(seconds=random.randint(0, 7_776_000)),
        "is_fraud": int(random.random() < 0.03),
    })
df = spark.createDataFrame(pd.DataFrame(rows))
df.show(5)
df.printSchema()


# %% color=teal title="The DataFrame API: looks Pandas-shaped but builds a…"
# @explain: The DataFrame API: looks Pandas-shaped but builds a query plan
# The DataFrame API: looks Pandas-shaped but builds a query plan
agg = (df
        .filter(F.col("amount") > 50)
        .groupBy("country")
        .agg(
            F.count("*").alias("n_events"),
            F.avg("amount").alias("avg_amount"),
            F.sum(F.col("is_fraud")).alias("n_fraud"),
        )
        .orderBy(F.desc("n_events"))
)
agg.show()


# %% color=sky title="Same query in Spark SQL"
# @explain: Same query in Spark SQL — completely interchangeable
# Same query in Spark SQL — completely interchangeable
df.createOrReplaceTempView("events")
spark.sql('''
    SELECT country,
           COUNT(*)         AS n_events,
           AVG(amount)      AS avg_amount,
           SUM(is_fraud)    AS n_fraud
    FROM   events
    WHERE  amount > 50
    GROUP BY country
    ORDER BY n_events DESC
''').show()


# %% [markdown] color=mint title="Note what just happened.** The DataFrame API call…"
# # Note what just happened.** The DataFrame API call…
#
# **Note what just happened.** The DataFrame API call and the SQL query produced **identical query plans**. Spark's **Catalyst** optimiser parses both into the same logical plan, then to a physical plan, then to RDD operations on executors. **Same speed, same correctness — pick whichever your team reads more clearly.**


# %% [markdown] color=peach title="4 · Lazy evaluation, Catalyst, Tungsten — why Spark is fast"
# # 4 · Lazy evaluation, Catalyst, Tungsten — why Spark is fast
#


# %% color=violet title="Spark transformations are LAZY"
# @explain: Spark transformations are LAZY
# @explain: Inspecting the plan WITHOUT running:
# Spark transformations are LAZY. The .show()/.collect()/.write are ACTIONS.
big = (df.filter(F.col("amount") > 100)
         .groupBy("country", "is_fraud")
         .agg(F.count("*").alias("n")))

# Inspecting the plan WITHOUT running:
big.explain(mode="formatted")


# %% [markdown] color=amber title="The plan is built up before anything runs.** That…"
# # The plan is built up before anything runs.** That…
#
# **The plan is built up before anything runs.** That lets the **Catalyst optimiser** rewrite it — push filters down to file scans, prune columns you don't need, choose the cheapest join algorithm, etc. **Tungsten** then turns the physical plan into vectorised CPU code that runs on the **off-heap binary format** instead of JVM objects (faster + lower GC).
#
# A practical consequence: **call `.cache()` on a DataFrame you'll reuse** so the optimiser materialises it once instead of replaying the plan.


# %% color=rose title="big.cache()"
# @explain: Run this cell to see the output.
big.cache()
big.count(); big.count()    # second call hits the cache — no re-scan


# %% [markdown] color=lime title="5 · The hot patterns"
# # 5 · The hot patterns
#
# ```python
# # JOIN — broadcast small dimension table
# from pyspark.sql.functions import broadcast
# joined = df.join(broadcast(countries_df), "country")
#
# # WINDOW functions — rolling features (M69 in spirit)
# …


# %% [markdown] color=teal title="6 · Delta Lake — ACID on top of Parquet"
# # 6 · Delta Lake — ACID on top of Parquet
#
# Spark on plain Parquet has one big hole: **concurrent writes corrupt the data**. Two jobs writing to `s3://bkt/events/` will overwrite each other's files. There's no transaction log. **Delta Lake** fixes that by adding a `_delta_log/` folder of JSON commits next to the Parquet files. Every write is a transaction; every read sees a consistent snapshot.


# %% color=sky title="Write the same data as a Delta table"
# @explain: Write the same data as a Delta table
# @explain: Read it back
# Write the same data as a Delta table
df.write.format("delta").mode("overwrite").save("/tmp/events_delta")

# Read it back
events = spark.read.format("delta").load("/tmp/events_delta")
events.count()


# %% [markdown] color=mint title="What you got for free vs Parquet"
# # What you got for free vs Parquet
#
# **What you got for free vs Parquet.**
#
# | Feature | Plain Parquet | Delta |
# |---|---|---|
# | ACID on concurrent writes | ❌ | ✅ |
# | Schema enforcement | manual | automatic |
# | Schema evolution (`mergeSchema`) | manual | one flag |
# | `UPDATE` / `DELETE` / `MERGE INTO` | ❌ | ✅ |
# …


# %% [markdown] color=peach title="7 · Time travel + MERGE + schema evolution"
# # 7 · Time travel + MERGE + schema evolution
#


# %% color=violet title="1"
# @explain: 1
# 1. Time travel — read a previous version
events_v0 = spark.read.format("delta").option("versionAsOf", 0).load("/tmp/events_delta")
events_v0.count()


# %% color=amber title="2"
# @explain: 2
# @explain: Pretend we receive a daily "updates" feed
# 2. MERGE INTO — upserts, the killer Delta feature
from delta.tables import DeltaTable

# Pretend we receive a daily "updates" feed
updates = spark.createDataFrame(pd.DataFrame([
    {"user_id": 42, "amount": 999.99, "country": "US",
     "event_ts": dt.datetime(2024, 6, 1), "is_fraud": 1},
    {"user_id": 18, "amount": 12.50,  "country": "IN",
     "event_ts": dt.datetime(2024, 6, 1), "is_fraud": 0},
]))

tgt = DeltaTable.forPath(spark, "/tmp/events_delta")
(tgt.alias("t")
    .merge(updates.alias("u"),
           "t.user_id = u.user_id AND t.event_ts = u.event_ts")
    .whenMatchedUpdateAll()
    .whenNotMatchedInsertAll()
    .execute())


# %% color=rose title="3"
# @explain: 3
# 3. Schema evolution — auto-add a new column
new_rows = spark.createDataFrame(pd.DataFrame([
    {"user_id": 7, "amount": 200.0, "country": "FR",
     "event_ts": dt.datetime(2024, 7, 1), "is_fraud": 0,
     "device": "iphone"},                  # ← new column
]))
(new_rows.write.format("delta")
        .option("mergeSchema", "true")     # ← the flag that lets new columns through
        .mode("append")
        .save("/tmp/events_delta"))


# %% [markdown] color=lime title="`MERGE INTO`** is what turned data lakes into databases"
# # `MERGE INTO`** is what turned data lakes into databases
#
# **`MERGE INTO`** is what turned data lakes into databases. The same syntax handles inserts, updates, deletes, and slowly-changing-dimensions in one statement. Before Delta, doing an idempotent upsert on Parquet meant writing-then-renaming whole partitions by hand.
#
# **Time travel** is *not* a backup mechanism — old files get reaped by `VACUUM` after the configured retention (default 7 days). Use it for debugging, reproducibility, and `CREATE TABLE clone AS @ <version>` for rollback during deploys.


# %% [markdown] color=teal title="8 · Medallion architecture (Bronze / Silver / Gold)"
# # 8 · Medallion architecture (Bronze / Silver / Gold)
#
# The canonical lakehouse layout:
#
# ```
#    raw event firehose
#         │
#         ▼
# …


# %% [markdown] color=sky title="9 · Streaming with Structured Streaming"
# # 9 · Streaming with Structured Streaming
#
# Spark's micro-batch streaming API. **Same DataFrame code** for batch and streaming — change `.read` to `.readStream` and Spark runs the same plan continuously.
#
# ```python
# events_stream = (spark.readStream
#                       .format("delta")
#                       .load("/lake/bronze/events"))
# …


# %% [markdown] color=mint title="10 · Spark vs Polars vs DuckDB vs Snowflake"
# # 10 · Spark vs Polars vs DuckDB vs Snowflake
#
# | Tool | Sweet spot | Why pick it |
# |---|---|---|
# | **Spark** | distributed, petabytes, joins across many tables | the workhorse; matches every cloud; Delta + Iceberg + Hudi support |
# | **Polars** (M2-era extension) | single-machine, < 100 GB, lazy Rust performance | dramatically faster than Pandas; one machine, one process |
# | **DuckDB** | analytic SQL on local files, terabytes, embedded | "SQLite for analytics" — incredible for ad-hoc + dbt |
# | **Snowflake** | hosted warehouse, simple SQL, no ops | pay-per-query; great for BI + dbt-driven transforms |
# …


# %% [markdown] color=peach title="11 · 🎓 Course wrap-up — 73 modules"
# # 11 · 🎓 Course wrap-up — 73 modules
#
# ```
# M1   – M5     Python · Pandas · NumPy · Visualisation · SQL
# M6   – M15    Stats · classical ML · evaluation · feature eng · MLOps
# M16  – M24    PyTorch · transformers · diffusion · time-series · DeepSeek-V3
# M25  – M27    Pydantic · LangChain · Chroma RAG starter
# M28  – M31    FastAPI · serving · vector DBs · advanced RAG
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


