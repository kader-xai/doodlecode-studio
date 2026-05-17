# doodlecode format-version: 2
# Auto-converted from module_36_postgresql_pgvector.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 36 Postgresql Pgvector"
# # Module 36 Postgresql Pgvector
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 36 — PostgreSQL + pgvector"
# # Module 36 — PostgreSQL + pgvector
#
# > M26 was SQLite (great for learning). Production runs **PostgreSQL** — concurrent, transactional, with JSONB, full-text search, and crucially the **`pgvector`** extension for vector similarity search. One database for relational data + embeddings. No more sync issues between Postgres and Chroma.
#
# This module assumes you've finished **M26 (SQL)** and **M30 (RAG)**.
#
# ### What you'll cover
# 1. Why Postgres over SQLite (and why pgvector beat dedicated vector DBs for many teams)
# …


# %% [markdown] color=mint title="1 · Why Postgres + pgvector"
# # 1 · Why Postgres + pgvector
#
# | Reason | Why it matters |
# |---|---|
# | **Concurrent writes** | SQLite locks the whole DB; Postgres handles thousands of concurrent connections |
# | **Transactional integrity** | Insert a doc + its embedding atomically — no partial state |
# | **JSONB** | semi-structured data with a B-tree-style index; faster than NoSQL for many workloads |
# | **Full-text search** built in | no need for Elasticsearch for most use cases |
# …


# %% [markdown] color=peach title="2 · Setup — Postgres + pgvector inside Colab"
# # 2 · Setup — Postgres + pgvector inside Colab
#
# One cell — installs Postgres 16, the pgvector extension, starts the server, and creates a database. ~60 seconds.


# %% color=violet title="!apt-get -qq install -y postgresql…"
# @explain: Run this cell to see the output.
!apt-get -qq install -y postgresql postgresql-contrib postgresql-16-pgvector > /dev/null
!service postgresql start
!sudo -u postgres psql -c "CREATE USER me WITH SUPERUSER PASSWORD 'pw';"
!sudo -u postgres psql -c "CREATE DATABASE demo OWNER me;"
print("Postgres ready")


# %% color=amber title="!pip -q install psycopg[binary] sqlalchemy…"
# @explain: Run this cell to see the output.
!pip -q install psycopg[binary] sqlalchemy sentence-transformers
import psycopg, numpy as np, pandas as pd
from psycopg.rows import dict_row

DSN = "postgresql://me:pw@localhost/demo"
con = psycopg.connect(DSN, row_factory=dict_row, autocommit=True)
print(con.execute("SELECT version()").fetchone()["version"])


# %% [markdown] color=rose title="Note on portability:** the same…"
# # Note on portability:** the same…
#
# **Note on portability:** the same `psycopg.connect(DSN, ...)` works against any Postgres URL — Neon, Supabase, AWS RDS, Aurora, your local Docker container. Only the URL changes.


# %% [markdown] color=lime title="3 · JSONB — Semi-Structured Data, Indexed"
# # 3 · JSONB — Semi-Structured Data, Indexed
#
# `JSONB` stores arbitrary JSON in a column with a binary representation that's queryable and indexable. The single most useful "Postgres > MySQL" feature.


# %% color=teal title="Insert events with arbitrary JSON shapes"
# @explain: Insert events with arbitrary JSON shapes
# @explain: Query JSONB with the -> and ->> operators
con.execute("DROP TABLE IF EXISTS events")
con.execute("""
CREATE TABLE events (
    id        SERIAL PRIMARY KEY,
    user_id   TEXT,
    ts        TIMESTAMPTZ DEFAULT NOW(),
    payload   JSONB
)
""")

# Insert events with arbitrary JSON shapes
con.execute("INSERT INTO events (user_id, payload) VALUES (%s, %s)",
            ("ada", json.dumps({"event": "login", "ip": "1.2.3.4"})))
con.execute("INSERT INTO events (user_id, payload) VALUES (%s, %s)",
            ("ada", json.dumps({"event": "click", "button": "buy",   "value": 99})))
con.execute("INSERT INTO events (user_id, payload) VALUES (%s, %s)",
            ("linus", json.dumps({"event": "click", "button": "help", "value": 0})))

# Query JSONB with the -> and ->> operators
rows = con.execute("""
SELECT user_id, payload->>'event' AS event, (payload->>'value')::int AS value
FROM events
WHERE payload->>'event' = 'click'
ORDER BY value DESC
""").fetchall()
print(rows)


# %% [markdown] color=sky title="Operators to know"
# # Operators to know
#
# **Operators to know:**
# - `payload -> 'key'` — returns JSONB
# - `payload ->> 'key'` — returns TEXT (cast to int/float as needed: `(payload->>'value')::int`)
# - `payload @> '{"event":"click"}'` — JSONB contains
# - `CREATE INDEX ON events USING GIN (payload)` — fast `@>` queries


# %% [markdown] color=mint title="4 · Arrays & Generated Columns"
# # 4 · Arrays & Generated Columns
#


# %% color=peach title="con.execute('DROP TABLE IF EXISTS articles')"
# @explain: Run this cell to see the output.
con.execute("DROP TABLE IF EXISTS articles")
con.execute("""
CREATE TABLE articles (
    id     SERIAL PRIMARY KEY,
    title  TEXT,
    body   TEXT,
    tags   TEXT[],
    word_count INT GENERATED ALWAYS AS (array_length(string_to_array(body, ' '), 1)) STORED
)
""")
con.execute("INSERT INTO articles (title, body, tags) VALUES (%s, %s, %s)",
            ("PyTorch tips", "A short post about PyTorch and tensors and autograd",
             ["pytorch", "deep-learning"]))
con.execute("INSERT INTO articles (title, body, tags) VALUES (%s, %s, %s)",
            ("SQL window functions", "A guide to window functions and partitions",
             ["sql", "data"]))

print(pd.DataFrame(con.execute("SELECT title, tags, word_count FROM articles").fetchall()))


# %% [markdown] color=violet title="`GENERATED ALWAYS AS"
# # `GENERATED ALWAYS AS
#
# **`GENERATED ALWAYS AS ... STORED`** auto-computes a column on insert/update. Avoids stale derived data.
#
# **Array operations:**
# - `tags @> ARRAY['pytorch']` — contains
# - `tags && ARRAY['ai','ml']` — overlaps any
# - `unnest(tags)` — flatten an array column into rows


# %% [markdown] color=amber title="5 · Full-Text Search with `tsvector`"
# # 5 · Full-Text Search with `tsvector`
#
# For most "search by keyword" needs you don't need Elasticsearch — Postgres ships with stemming, stopwords, and ranking via `tsvector`.


# %% color=rose title="Query with stemming + ranking"
# @explain: Query with stemming + ranking
con.execute("ALTER TABLE articles ADD COLUMN tsv TSVECTOR")
con.execute("UPDATE articles SET tsv = to_tsvector('english', title || ' ' || body)")
con.execute("CREATE INDEX articles_tsv_idx ON articles USING GIN (tsv)")

# Query with stemming + ranking
rows = con.execute("""
SELECT title, ts_rank(tsv, query) AS rank
FROM articles, plainto_tsquery('english', 'tensor') AS query
WHERE tsv @@ query
ORDER BY rank DESC
""").fetchall()
print(rows)


# %% [markdown] color=lime title="Notice the query for `'tensor'` matches `tensors`…"
# # Notice the query for `'tensor'` matches `tensors`…
#
# Notice the query for `'tensor'` matches `tensors` thanks to English stemming. `ts_rank` orders by relevance.


# %% [markdown] color=teal title="6 · pgvector — Vector Type + Distance Operators"
# # 6 · pgvector — Vector Type + Distance Operators
#
# Three distance operators ship with pgvector:
#
# | Operator | Distance | Best for |
# |---|---|---|
# | `<->` | L2 (Euclidean) | numeric features, raw distances |
# | `<#>` | negative inner product | when vectors are normalised + you want speed |
# …


# %% color=sky title="Embed a tiny corpus with sentence-transformers"
# @explain: Embed a tiny corpus with sentence-transformers
con.execute("CREATE EXTENSION IF NOT EXISTS vector")
con.execute("DROP TABLE IF EXISTS docs")
con.execute("""
CREATE TABLE docs (
    id        SERIAL PRIMARY KEY,
    content   TEXT,
    metadata  JSONB,
    embedding vector(384)
)
""")

# Embed a tiny corpus with sentence-transformers
from sentence_transformers import SentenceTransformer
embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

corpus = [
    ("NumPy was created by Travis Oliphant in 2006.", {"topic": "numpy", "year": 2006}),
    ("PyTorch was released by Facebook AI Research in 2016.", {"topic": "pytorch", "year": 2016}),
    ("Pandas was created by Wes McKinney in 2008.", {"topic": "pandas", "year": 2008}),
    ("DeepSeek-V3 is a 671B-parameter open-weight MoE model with Multi-Latent Attention.", {"topic": "deepseek", "year": 2024}),
]

embeddings = embedder.encode([t for t, _ in corpus], normalize_embeddings=True)

for (text, meta), emb in zip(corpus, embeddings):
    con.execute(
        "INSERT INTO docs (content, metadata, embedding) VALUES (%s, %s, %s)",
        (text, json.dumps(meta), emb.tolist())
    )
print(f"inserted {con.execute('SELECT COUNT(*) AS n FROM docs').fetchone()['n']} docs")


# %% [markdown] color=mint title="7 · Cosine Search — Top-K Most Similar"
# # 7 · Cosine Search — Top-K Most Similar
#


# %% color=peach title="def search(query"
# @explain: Run this cell to see the output.
def search(query, k=2):
    q_emb = embedder.encode([query], normalize_embeddings=True)[0].tolist()
    rows = con.execute("""
        SELECT content,
               metadata->>'topic' AS topic,
               1 - (embedding <=> %s::vector) AS similarity
        FROM docs
        ORDER BY embedding <=> %s::vector
        LIMIT %s
    """, (q_emb, q_emb, k)).fetchall()
    return rows

for r in search("Who created NumPy?"):
    print(f"  ({r['similarity']:.3f}) [{r['topic']}]  {r['content']}")
print()
for r in search("Tell me about Mixture of Experts models"):
    print(f"  ({r['similarity']:.3f}) [{r['topic']}]  {r['content']}")


# %% [markdown] color=violet title="Note:** `<=>` returns cosine *distance* (lower =…"
# # Note:** `<=>` returns cosine *distance* (lower =…
#
# **Note:** `<=>` returns cosine *distance* (lower = closer). We compute similarity as `1 - distance`. The same query is referenced twice — once in `SELECT` (for the score) and once in `ORDER BY` (for ranking).


# %% [markdown] color=amber title="8 · ANN Indexes — HNSW & IVFFlat for Speed"
# # 8 · ANN Indexes — HNSW & IVFFlat for Speed
#
# Without an index the search is sequential — fine for thousands of rows, slow for millions. Two index types:
#
# | Index | Build time | Recall vs recall | Memory |
# |---|---|---|---|
# | **HNSW** | slower | best recall | higher |
# | **IVFFlat** | faster | OK recall (tunable) | lower |
# …


# %% color=rose title="HNSW"
# @explain: HNSW — best for production
# @explain: Verify the planner uses it
# HNSW — best for production
con.execute("""
CREATE INDEX IF NOT EXISTS docs_emb_hnsw_idx
ON docs USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64)
""")

# Verify the planner uses it
plan = con.execute("EXPLAIN ANALYZE SELECT * FROM docs ORDER BY embedding <=> %s::vector LIMIT 2",
                    (embedder.encode(["test"])[0].tolist(),)).fetchall()
for row in plan:
    print(list(row.values())[0])


# %% [markdown] color=lime title="Tuning knobs"
# # Tuning knobs
#
# **Tuning knobs (HNSW):**
# - `m` — connections per layer (8-32). Higher = better recall, slower build.
# - `ef_construction` — search effort during build (40-200). Same trade-off.
# - `SET hnsw.ef_search = 100` — query-time effort (default 40). Bigger = better recall, slower query.


# %% [markdown] color=teal title="9 · Hybrid Retrieval — Vector Search + SQL Filters"
# # 9 · Hybrid Retrieval — Vector Search + SQL Filters
#
# The killer feature of pgvector vs dedicated vector DBs: **WHERE clauses on metadata are just SQL**. Multi-tenant safe, no separate filter step.


# %% color=sky title="def hybrid_search(query"
# @explain: Run this cell to see the output.
def hybrid_search(query, year_min=None, topic=None, k=5):
    q_emb = embedder.encode([query], normalize_embeddings=True)[0].tolist()
    sql = """
    SELECT content,
           metadata->>'topic' AS topic,
           (metadata->>'year')::int AS year,
           1 - (embedding <=> %s::vector) AS similarity
    FROM docs
    WHERE 1=1
    """
    params = [q_emb]
    if year_min is not None:
        sql += " AND (metadata->>'year')::int >= %s"
        params.append(year_min)
    if topic is not None:
        sql += " AND metadata->>'topic' = %s"
        params.append(topic)
    sql += " ORDER BY embedding <=> %s::vector LIMIT %s"
    params.extend([q_emb, k])
    return con.execute(sql, params).fetchall()

print("ALL docs about libraries:")
for r in hybrid_search("Python data library", k=4):
    print(f"  ({r['similarity']:.3f}) [{r['topic']}, {r['year']}]  {r['content']}")

print("\nONLY post-2010:")
for r in hybrid_search("Python data library", year_min=2010, k=4):
    print(f"  ({r['similarity']:.3f}) [{r['topic']}, {r['year']}]  {r['content']}")


# %% [markdown] color=mint title="10 · Where This Scales"
# # 10 · Where This Scales
#
# | Need | Tool |
# |---|---|
# | Hosted Postgres + pgvector (free tier) | **Neon**, **Supabase** |
# | Production-grade managed | **AWS RDS / Aurora**, **GCP Cloud SQL** (with pgvector) |
# | Sharded / distributed | **Citus** (Microsoft), **CockroachDB** |
# | 10×-100× faster ANN at scale | **pgvectorscale** (Timescale), **Lantern** |
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


