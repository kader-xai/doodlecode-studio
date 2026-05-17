# doodlecode format-version: 2
# Auto-converted from module_42_vector_db_comparison.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 42 Vector Db Comparison"
# # Module 42 Vector Db Comparison
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 42 — Vector DB Comparison"
# # Module 42 — Vector DB Comparison
#
# > M27 used **Chroma** (file-based, dev-friendly), M36 used **pgvector** (Postgres extension), M37 added **RediSearch** (hot in-memory). This module zooms out: when do you reach for each, and what about **FAISS**, **Qdrant**, **Weaviate**, **Pinecone**, **Milvus**? You'll run the same RAG load against three of them in this notebook (FAISS, Chroma, Qdrant) and see the API + perf + ops tradeoffs side by side.
#
# ### What you'll cover
# 1. The vector-DB landscape — six categories, one decision tree
# 2. ANN algorithms in 2 minutes — flat / IVF / HNSW / PQ
# 3. **FAISS** — Facebook's library; the gold standard for in-process search
# …


# %% [markdown] color=mint title="1 · The landscape"
# # 1 · The landscape
#
# | Category | Examples | Sweet spot |
# |---|---|---|
# | **In-process library** | FAISS, ScaNN, hnswlib, Annoy | embed inside your Python app; max throughput |
# | **Embedded DB** | Chroma, LanceDB, sqlite-vec | dev / single-node / desktop apps |
# | **Self-hosted server** | Qdrant, Weaviate, Milvus, Vespa | production, you control the box |
# | **Managed cloud** | Pinecone, Vespa Cloud, Weaviate Cloud, Qdrant Cloud, Turbopuffer | "make it someone else's problem" |
# …


# %% [markdown] color=peach title="2 · ANN algorithms in 2 minutes"
# # 2 · ANN algorithms in 2 minutes
#
# | Algorithm | Idea | Build cost | Query cost | Recall@10 |
# |---|---|---|---|---|
# | **Flat** (brute) | scan everything | 0 | O(N·D) | 100% |
# | **IVF** | k-means clusters; search nearest k clusters | medium | O(√N · D) | ~95–98% |
# | **HNSW** | small-world graph; greedy walk | high | O(log N · D) | ~98–99% |
# | **PQ** (Product Quantization) | compress vectors to bytes | low | O(N) but on bytes | ~90% |
# …


# %% [markdown] color=violet title="3 · FAISS — the in-process gold standard"
# # 3 · FAISS — the in-process gold standard
#


# %% color=amber title="!pip -q install faiss-cpu sentence-transformers numpy"
# @explain: Run this cell to see the output.
!pip -q install faiss-cpu sentence-transformers numpy


# %% color=rose title="build a 10K-vector toy corpus"
# @explain: build a 10K-vector toy corpus
import numpy as np, time
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
DIM = model.get_sentence_embedding_dimension()
print("dim:", DIM)

# build a 10K-vector toy corpus
rng = np.random.default_rng(42)
docs = [f"Doc number {i} about topic {rng.integers(0, 100)}." for i in range(10_000)]
X = model.encode(docs, batch_size=128, show_progress_bar=False).astype("float32")
print("X:", X.shape)


# %% color=lime title="(a) FLAT"
# @explain: (a) FLAT — exact, perfect recall, baseline
import faiss

# (a) FLAT — exact, perfect recall, baseline
flat = faiss.IndexFlatIP(DIM)        # inner product (cosine if vectors are L2-normalised)
faiss.normalize_L2(X)
flat.add(X)

q = model.encode(["doc about topic 7"]).astype("float32"); faiss.normalize_L2(q)
t = time.time(); D,I = flat.search(q, 5); print(f"FLAT  query: {(time.time()-t)*1000:.2f} ms  top-5 idx:", I[0])


# %% color=teal title="(b) HNSW"
# @explain: (b) HNSW — approximate, log-N query
# (b) HNSW — approximate, log-N query
hnsw = faiss.IndexHNSWFlat(DIM, 32)   # M=32 graph degree
hnsw.hnsw.efConstruction = 64
t = time.time(); hnsw.add(X); print(f"HNSW build: {time.time()-t:.2f}s")
hnsw.hnsw.efSearch = 64
t = time.time(); D,I = hnsw.search(q, 5); print(f"HNSW  query: {(time.time()-t)*1000:.2f} ms  top-5 idx:", I[0])


# %% [markdown] color=sky title="4 · Chroma — easiest dev experience"
# # 4 · Chroma — easiest dev experience
#


# %% color=mint title="!pip -q install chromadb"
# @explain: Run this cell to see the output.
!pip -q install chromadb


# %% color=peach title="add in batches with metadata for filtering"
# @explain: add in batches with metadata for filtering
import chromadb
client = chromadb.PersistentClient(path="/tmp/chroma_m42")
col = client.get_or_create_collection("m42", metadata={"hnsw:space": "cosine"})

# add in batches with metadata for filtering
ids = [f"d{i}" for i in range(len(docs))]
col.upsert(ids=ids, documents=docs, embeddings=X.tolist(),
           metadatas=[{"topic": int(d.split()[-1].rstrip("."))} for d in docs])

t = time.time()
res = col.query(query_embeddings=q.tolist(), n_results=5, where={"topic": {"$gt": 50}})
print(f"Chroma query (with WHERE topic>50): {(time.time()-t)*1000:.1f} ms")
print(res["ids"][0][:5])


# %% [markdown] color=violet title="5 · Qdrant — the strongest OSS server"
# # 5 · Qdrant — the strongest OSS server
#
# Qdrant ships an in-process mode that needs no server — perfect for Colab. In production you'd run the docker container or use Qdrant Cloud.


# %% color=amber title="!pip -q install qdrant-client"
# @explain: Run this cell to see the output.
!pip -q install qdrant-client


# %% color=rose title="from qdrant_client import QdrantClient"
# @explain: Run this cell to see the output.
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct, Filter, FieldCondition, Range

qc = QdrantClient(":memory:")           # embedded — no server
qc.recreate_collection(
    collection_name="m42",
    vectors_config=VectorParams(size=DIM, distance=Distance.COSINE),
)

points = [
    PointStruct(id=i, vector=X[i].tolist(),
                payload={"topic": int(docs[i].split()[-1].rstrip(".")), "text": docs[i]})
    for i in range(len(docs))
]
qc.upsert(collection_name="m42", points=points)
print("inserted", qc.count("m42").count, "points")


# %% color=lime title="t = time.time()"
# @explain: Run this cell to see the output.
t = time.time()
hits = qc.search(
    collection_name="m42",
    query_vector=q[0].tolist(),
    query_filter=Filter(must=[FieldCondition(key="topic", range=Range(gt=50))]),
    limit=5,
)
print(f"Qdrant query (topic>50): {(time.time()-t)*1000:.1f} ms")
for h in hits:
    print(f"  id={h.id}  score={h.score:.3f}  topic={h.payload['topic']}")


# %% [markdown] color=teal title="6 · Weaviate — schema + GraphQL + hybrid"
# # 6 · Weaviate — schema + GraphQL + hybrid
#
# Weaviate is the strongest of the OSS servers when you want **hybrid search** (BM25 + vector) baked in, schemas with class-level config, and a graph-style query language. We'll skip a live install (heavy in Colab) and show the API shape:
#
# ```python
# import weaviate
#
# client = weaviate.connect_to_local()    # or connect_to_weaviate_cloud(...)
# …


# %% [markdown] color=sky title="7 · Managed + large-scale — concepts"
# # 7 · Managed + large-scale — concepts
#
# | Engine | Why pick it | Watch out for |
# |---|---|---|
# | **Pinecone** | zero ops, autoscale, dependable latency, namespaces for multi-tenant | $$ at scale; vendor lock-in |
# | **Vespa** | huge-scale (billions), structured + tensor + text in one engine; powers Yahoo Search | steep learning curve |
# | **Milvus / Zilliz Cloud** | most knobs, GPU-accelerated, NVIDIA-friendly | heavy ops self-hosted |
# | **Turbopuffer** | object-storage-backed; cheap, slow-cold | not for sub-100ms hot paths |
# …


# %% [markdown] color=mint title="8 · Side-by-side benchmark"
# # 8 · Side-by-side benchmark
#


# %% color=peach title="import statistics"
# @explain: Run this cell to see the output.
import statistics
def bench(name, fn, runs=20):
    times = []
    for _ in range(runs):
        t = time.time(); fn(); times.append((time.time()-t)*1000)
    print(f"{name:8}  median {statistics.median(times):6.2f} ms   p95 {sorted(times)[int(0.95*len(times))]:.2f} ms")

bench("FLAT",  lambda: flat.search(q, 5))
bench("HNSW",  lambda: hnsw.search(q, 5))
bench("Chroma",lambda: col.query(query_embeddings=q.tolist(), n_results=5))
bench("Qdrant",lambda: qc.search(collection_name="m42", query_vector=q[0].tolist(), limit=5))


# %% [markdown] color=violet title="On Colab CPU, FAISS HNSW typically wins on raw…"
# # On Colab CPU, FAISS HNSW typically wins on raw…
#
# On Colab CPU, FAISS HNSW typically wins on raw query latency (it's a tight C++ loop with no serialisation). Qdrant adds protobuf overhead but **wins back** as soon as you add filters. Chroma is the slowest in this micro-benchmark but the simplest to operate.


# %% [markdown] color=amber title="9 · Filtering & hybrid retrieval — the real differentiator"
# # 9 · Filtering & hybrid retrieval — the real differentiator
#
# Pure vector recall is solved. The hard part of production retrieval is **filtering** — `WHERE tenant_id = X AND created_at > Y AND tag IN (...)`.
#
# | Engine | Filter cost | Hybrid (BM25 + vec) |
# |---|---|---|
# | FAISS | none built-in (you filter post-search → recall drops) | no |
# | Chroma | basic `where` over metadata | no |
# …


# %% [markdown] color=rose title="10 · Decision table — picking the right one"
# # 10 · Decision table — picking the right one
#
# | Constraint | Pick |
# |---|---|
# | Already on Postgres | **pgvector** |
# | Single-machine, embed in a Python app | **FAISS** |
# | Local dev / desktop / single-node | **Chroma** or **LanceDB** |
# | OSS, server, hard filters at scale | **Qdrant** |
# …


# %% [markdown] color=lime title="✅ Recap"
# # ✅ Recap
#
# - Six categories of vector store: in-process · embedded · self-hosted · managed · Postgres ext · cache.
# - ANN: **HNSW** is the default everywhere; **IVF+PQ** for billion-scale.
# - FAISS = library, Chroma = dev, Qdrant = OSS server, Pinecone = managed, pgvector = "just use Postgres".
# - The differentiator is **filters + hybrid**, not raw vector recall.
# - Wrap whichever you pick behind a 5-method interface so swapping is a config change.
#
# Next: **M43 — crewAI & AutoGen** (multi-agent orchestration).


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


