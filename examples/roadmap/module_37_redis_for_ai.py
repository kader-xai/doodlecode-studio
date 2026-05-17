# doodlecode format-version: 2
# Auto-converted from module_37_redis_for_ai.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 37 Redis For Ai"
# # Module 37 Redis For Ai
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 37 — Redis for AI Backends"
# # Module 37 — Redis for AI Backends
#
# > Redis is the **swiss-army knife of AI infra**. Every production LLM app uses it for at least one of:
# > 1. **Caching** identical prompts → save $$ on repeat calls
# > 2. **Rate limiting** users / tenants
# > 3. **Session memory** — short-term conversation history (cheaper than Postgres)
# > 4. **Pub/Sub** — stream tokens from a worker to the user's browser
# > 5. **Task queues** with Redis Streams — for async embeddings / generations
# …


# %% [markdown] color=mint title="1 · Why Redis for AI"
# # 1 · Why Redis for AI
#
# | Use case | Datatype | Why |
# |---|---|---|
# | Cache identical LLM calls | `STRING` + `EXPIRE` | save tokens, latency drops to ~1 ms |
# | Track tokens-per-minute per user | `Sorted Set` (ZADD with timestamp) | sliding-window rate limit |
# | Store last 10 conversation turns | `LIST` (LPUSH + LTRIM) | trim to a fixed window cheaply |
# | Async job queue (e.g. embed-this-doc) | `Stream` (XADD / XREADGROUP) | consumer groups, exactly-once-ish |
# …


# %% [markdown] color=peach title="2 · Setup — Redis Stack inside Colab"
# # 2 · Setup — Redis Stack inside Colab
#
# Redis Stack = Redis + RediSearch + RedisJSON + RedisTimeSeries + RedisBloom modules. We install it via the official tarball and run the server in the background.


# %% color=violet title="!curl -fsSL…"
# @explain: Run this cell to see the output.
!curl -fsSL https://packages.redis.io/redis-stack/redis-stack-server-7.4.0-v0.focal.x86_64.tar.gz -o /tmp/rs.tgz
!mkdir -p /opt/redis-stack && tar -xzf /tmp/rs.tgz -C /opt/redis-stack --strip-components=1
!nohup /opt/redis-stack/bin/redis-stack-server --daemonize yes --port 6379 > /tmp/redis.log 2>&1 &
import time; time.sleep(2)
!/opt/redis-stack/bin/redis-cli ping


# %% color=amber title="!pip -q install redis sentence-transformers numpy"
# @explain: Run this cell to see the output.
!pip -q install redis sentence-transformers numpy


# %% color=rose title="import redis"
# @explain: Run this cell to see the output.
import redis, json, time, hashlib, numpy as np
r = redis.Redis(host='localhost', port=6379, decode_responses=True)
r.ping()


# %% [markdown] color=lime title="3 · Strings + TTL → the LLM response cache"
# # 3 · Strings + TTL → the LLM response cache
#
# The simplest, highest-ROI Redis pattern for AI apps. Hash the prompt + model name → use it as the key. If the key exists, return the cached response. Otherwise call the model, store with a TTL.


# %% color=teal title="--- expensive call (placeholder"
# @explain: --- expensive call (placeholder — pretend we hit an LLM) ---
def cache_key(prompt: str, model: str) -> str:
    h = hashlib.sha256(f"{model}::{prompt}".encode()).hexdigest()[:16]
    return f"llm:cache:{model}:{h}"

def cached_llm_call(prompt: str, model: str = "flan-t5-base", ttl: int = 3600):
    key = cache_key(prompt, model)
    hit = r.get(key)
    if hit is not None:
        return json.loads(hit), "HIT"
    # --- expensive call (placeholder — pretend we hit an LLM) ---
    response = {"text": f"[fake completion for: {prompt[:40]}...]", "tokens": 42}
    r.setex(key, ttl, json.dumps(response))   # SET + EXPIRE in one command
    return response, "MISS"

print(cached_llm_call("What is RAG?"))      # MISS
print(cached_llm_call("What is RAG?"))      # HIT — instant
print("TTL remaining:", r.ttl(cache_key("What is RAG?", "flan-t5-base")), "s")


# %% [markdown] color=sky title="4 · Hashes → user sessions"
# # 4 · Hashes → user sessions
#
# A `HASH` is a flat key→value map under one Redis key. Perfect for a session object: user_id, plan, last_seen, token_balance.


# %% color=mint title="r.hset('session:u123'"
# @explain: Run this cell to see the output.
r.hset("session:u123", mapping={
    "user_id": "u123",
    "plan": "pro",
    "tokens_remaining": 50000,
    "last_seen": int(time.time()),
})
r.expire("session:u123", 86400)   # auto-expire after 24h

print(r.hgetall("session:u123"))
r.hincrby("session:u123", "tokens_remaining", -1500)   # atomic decrement
print("after a generation call:", r.hget("session:u123", "tokens_remaining"))


# %% [markdown] color=peach title="5 · Lists → conversation history (last-N window)"
# # 5 · Lists → conversation history (last-N window)
#
# `LPUSH` adds to head, `LTRIM` keeps only the latest N. Together they implement a sliding conversation window — cheaper than re-querying Postgres on every turn.


# %% color=violet title="def remember_turn(user_id: str"
# @explain: Run this cell to see the output.
def remember_turn(user_id: str, role: str, content: str, max_turns: int = 10):
    key = f"chat:{user_id}:history"
    r.lpush(key, json.dumps({"role": role, "content": content, "ts": int(time.time())}))
    r.ltrim(key, 0, max_turns * 2 - 1)   # *2 because each turn = user + assistant

def recent_turns(user_id: str):
    raw = r.lrange(f"chat:{user_id}:history", 0, -1)
    return [json.loads(x) for x in reversed(raw)]   # oldest → newest

remember_turn("u123", "user", "hi")
remember_turn("u123", "assistant", "hello! how can I help?")
remember_turn("u123", "user", "explain redis streams")
for t in recent_turns("u123"):
    print(t)


# %% [markdown] color=amber title="6 · Sorted sets → sliding-window rate limit"
# # 6 · Sorted sets → sliding-window rate limit
#
# A `ZSET` orders members by a numeric score. We use the **timestamp** as the score, then count entries inside the window.


# %% color=rose title="def allow(user_id: str"
# @explain: Run this cell to see the output.
def allow(user_id: str, max_per_minute: int = 30) -> bool:
    key = f"ratelimit:{user_id}"
    now = time.time()
    pipe = r.pipeline()
    pipe.zadd(key, {f"{now}-{np.random.randint(1<<32)}": now})  # add this hit
    pipe.zremrangebyscore(key, 0, now - 60)                     # drop hits older than 60s
    pipe.zcard(key)                                             # count remaining
    pipe.expire(key, 70)
    _, _, count, _ = pipe.execute()
    return count <= max_per_minute

for i in range(35):
    ok = allow("u123", max_per_minute=30)
    print(f"req {i+1:>2}: {'OK' if ok else 'BLOCKED'}")


# %% [markdown] color=lime title="7 · Streams → durable async job queue"
# # 7 · Streams → durable async job queue
#
# `Stream` is Redis's append-only log (think mini-Kafka). Use it when you have **producers** (web app accepting upload) and **consumers** (workers running embeddings). `XREADGROUP` gives you consumer-group semantics — each message goes to exactly one worker.


# %% color=teal title="producer"
# @explain: producer — web app side
# @explain: create consumer group (idempotent)
# @explain: consumer — worker process
# @explain: 
# producer — web app side
r.xadd("jobs:embed", {"doc_id": "d42", "url": "s3://docs/d42.pdf"})
r.xadd("jobs:embed", {"doc_id": "d43", "url": "s3://docs/d43.pdf"})
r.xadd("jobs:embed", {"doc_id": "d44", "url": "s3://docs/d44.pdf"})

# create consumer group (idempotent)
try:
    r.xgroup_create("jobs:embed", "embedders", id="0", mkstream=True)
except redis.ResponseError as e:
    if "BUSYGROUP" not in str(e): raise

# consumer — worker process
msgs = r.xreadgroup("embedders", "worker-1", {"jobs:embed": ">"}, count=10, block=100)
for stream, items in msgs:
    for msg_id, data in items:
        print("processing", msg_id, data)
        # ... do the actual work ...
        r.xack("jobs:embed", "embedders", msg_id)   # ack so it's not redelivered


# %% [markdown] color=sky title="8 · Pub/Sub → stream LLM tokens to the browser"
# # 8 · Pub/Sub → stream LLM tokens to the browser
#
# When your worker generates tokens, **publish** them on a per-request channel. Your web framework **subscribes** and forwards them as Server-Sent Events to the user.


# %% color=mint title="In a real app"
# @explain: In a real app, worker and webserver are different processes
# @explain: Here we simulate by subscribing in a thread
# @explain: worker emits tokens
# In a real app, worker and webserver are different processes.
# Here we simulate by subscribing in a thread.
import threading
received = []

def subscriber():
    sub = redis.Redis(host='localhost', port=6379, decode_responses=True).pubsub()
    sub.subscribe("stream:req-789")
    for msg in sub.listen():
        if msg["type"] == "message":
            tok = msg["data"]
            if tok == "[DONE]": break
            received.append(tok)

t = threading.Thread(target=subscriber); t.start(); time.sleep(0.2)

# worker emits tokens
for tok in ["The ", "capital ", "of ", "France ", "is ", "Paris.", "[DONE]"]:
    r.publish("stream:req-789", tok); time.sleep(0.05)

t.join(timeout=2)
print("client received:", "".join(received))


# %% [markdown] color=peach title="9 · RediSearch + vectors → ANN inside Redis"
# # 9 · RediSearch + vectors → ANN inside Redis
#
# Redis Stack ships with **RediSearch**, which adds a `VECTOR` field type. You can run cosine ANN queries on millions of vectors entirely inside Redis — no Postgres / Pinecone needed for the hot index.


# %% color=violet title="define index over hashes whose key starts with 'doc:'"
# @explain: define index over hashes whose key starts with 'doc:'
from redis.commands.search.field import TextField, VectorField, TagField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query
from sentence_transformers import SentenceTransformer

emb = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
DIM = emb.get_sentence_embedding_dimension()

# define index over hashes whose key starts with 'doc:'
schema = (
    TextField("text"),
    TagField("tag"),
    VectorField("vec", "HNSW", {"TYPE": "FLOAT32", "DIM": DIM, "DISTANCE_METRIC": "COSINE"}),
)
try:
    r.ft("idx:docs").create_index(schema, definition=IndexDefinition(prefix=["doc:"], index_type=IndexType.HASH))
except Exception as e:
    print("index already exists:", e)


# %% color=amber title="docs = ["
# @explain: Run this cell to see the output.
docs = [
    ("Paris is the capital of France.",   "geo"),
    ("The Eiffel Tower is in Paris.",     "landmark"),
    ("Python is a programming language.", "tech"),
    ("PyTorch is a deep-learning library.", "tech"),
    ("Croissants are a French pastry.",   "food"),
]
for i, (txt, tag) in enumerate(docs):
    v = emb.encode(txt).astype(np.float32).tobytes()
    r.hset(f"doc:{i}", mapping={"text": txt, "tag": tag, "vec": v})
print("inserted", len(docs), "docs")


# %% color=rose title="qvec = emb.encode('Where is the Eiffel…"
# @explain: Run this cell to see the output.
qvec = emb.encode("Where is the Eiffel tower?").astype(np.float32).tobytes()
q = (Query("(*)=>[KNN 3 @vec $V AS score]")
     .return_fields("text", "tag", "score")
     .sort_by("score").dialect(2))
res = r.ft("idx:docs").search(q, query_params={"V": qvec})
for d in res.docs:
    print(f"{float(d.score):.3f}  [{d.tag}]  {d.text}")


# %% color=lime title="hybrid: filter by tag THEN ANN"
# @explain: hybrid: filter by tag THEN ANN
# hybrid: filter by tag THEN ANN
q2 = (Query("(@tag:{tech})=>[KNN 2 @vec $V AS score]")
      .return_fields("text", "score").sort_by("score").dialect(2))
qvec2 = emb.encode("learn neural networks").astype(np.float32).tobytes()
for d in r.ft("idx:docs").search(q2, query_params={"V": qvec2}).docs:
    print(f"{float(d.score):.3f}  {d.text}")


# %% [markdown] color=teal title="10 · Production notes"
# # 10 · Production notes
#
# | Topic | What to know |
# |---|---|
# | **Persistence** | RDB snapshots (periodic) + AOF (append-only log). For caches you can disable both — speed > durability. |
# | **Eviction** | Set `maxmemory` + `maxmemory-policy allkeys-lru` so your cache evicts cleanly when full |
# | **Cluster** | Sharded Redis Cluster scales writes horizontally. Most teams stay on a single primary + replica until > 50 GB working set. |
# | **Hosted** | Upstash (serverless, pay-per-request), Redis Cloud, ElastiCache, Memorystore. Start hosted; self-host only if you must. |
# …


# %% [markdown] color=sky title="✅ Recap"
# # ✅ Recap
#
# - **Cache** prompts with `SETEX` — biggest LLM-cost win you can ship today.
# - **Sessions** in `HASH`, **history** in `LIST` (`LPUSH`+`LTRIM`).
# - **Rate limit** with sorted-set sliding window.
# - **Streams** for durable job queues with consumer groups.
# - **Pub/Sub** for per-request token streaming to browsers.
# - **RediSearch** adds vector ANN to the same Redis instance.
#
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


