# doodlecode format-version: 2
# Auto-converted from module_30_rag_and_vector_search.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 30 Rag And Vector Search"
# # Module 30 Rag And Vector Search
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 30 — RAG & Vector Search"
# # Module 30 — RAG & Vector Search
#
# > **Premise:** LLMs are great at *reasoning over* text but bad at *remembering* facts. **Retrieval-Augmented Generation (RAG)** fixes this by retrieving relevant context from your own documents and stuffing it into the prompt. It's the #1 LLM use case in production in 2026 — every "chat with your docs" / "AI search" / "knowledge assistant" is RAG.
#
# ### What you'll cover
# 1. The RAG mental model — and when to use it (vs fine-tuning)
# 2. The 5-stage pipeline — chunk → embed → store → retrieve → generate
# 3. **Embeddings** with `sentence-transformers`
# …


# %% [markdown] color=mint title="1 · The RAG Mental Model"
# # 1 · The RAG Mental Model
#
# | Approach | When |
# |---|---|
# | **Prompt-only** | facts that fit comfortably in context, won't change |
# | **Fine-tuning** | teach a STYLE or FORMAT (M25) |
# | **RAG** | answer over a CORPUS that's too big for context, changes daily, or is private |
#
# …


# %% color=peach title="!pip -q install sentence-transformers chromadb…"
# @explain: Run this cell to see the output.
!pip -q install sentence-transformers chromadb rank-bm25 transformers
import numpy as np, pandas as pd
from typing import List
import warnings; warnings.filterwarnings("ignore")


# %% [markdown] color=violet title="2 · The Demo Corpus"
# # 2 · The Demo Corpus
#
# A small set of paragraphs about Python's history, the deep-learning libraries, and a few trivia facts. Small enough to read; rich enough to demonstrate retrieval.


# %% color=amber title="docs = ["
# @explain: Run this cell to see the output.
docs = [
    {"id": "py-history",
     "title": "Python history",
     "text": "Python was created by Guido van Rossum and released in 1991. The name was inspired by the British comedy group Monty Python's Flying Circus, not the snake. Guido stepped down as 'Benevolent Dictator For Life' in 2018."},

    {"id": "numpy",
     "title": "NumPy origins",
     "text": "NumPy was created by Travis Oliphant in 2006 by merging the older Numeric and Numarray packages. It provides a fixed-size, typed n-dimensional array and is the foundation of nearly every Python scientific library, including Pandas and scikit-learn."},

    {"id": "pandas",
     "title": "Pandas origins",
     "text": "Pandas was created by Wes McKinney at AQR Capital Management starting in 2008 to handle quantitative analysis on financial data. The name comes from 'panel data', an econometrics term."},

    {"id": "pytorch",
     "title": "PyTorch origins",
     "text": "PyTorch was released by Facebook AI Research in 2016 as a Python-first deep-learning framework with dynamic computation graphs. It became the dominant research framework by around 2019, overtaking TensorFlow in academic publications."},

    {"id": "tf",
     "title": "TensorFlow origins",
     "text": "TensorFlow was open-sourced by Google in 2015. The original 1.x API used static computation graphs with sessions, which many found awkward. TensorFlow 2.0 in 2019 adopted eager execution by default, making it more PyTorch-like."},

    {"id": "transformer",
     "title": "Attention Is All You Need",
     "text": "The Transformer architecture was introduced in the 2017 paper 'Attention Is All You Need' by Vaswani et al. at Google. It replaced recurrent networks with self-attention and became the foundation of GPT, BERT, T5, and every modern LLM."},

    {"id": "deepseek",
     "title": "DeepSeek-V3",
     "text": "DeepSeek-V3 is a 671B-parameter open-weight Mixture-of-Experts language model released in 2024. Its key innovations include Multi-Latent Attention for KV cache compression and auxiliary-loss-free expert routing."},

    {"id": "ada",
     "title": "Ada Lovelace",
     "text": "Ada Lovelace, born in 1815, wrote what many consider the first computer program — an algorithm for Charles Babbage's Analytical Engine to compute Bernoulli numbers. She also speculated that machines could one day compose music."},
]

df = pd.DataFrame(docs)
print(df[["id", "title"]])


# %% [markdown] color=rose title="3 · Embeddings — Convert Text to Vectors"
# # 3 · Embeddings — Convert Text to Vectors
#
# A **text embedding** is a fixed-size vector that captures meaning. Texts about similar topics end up close together (high cosine similarity); unrelated texts end up far apart.
#
# We use `sentence-transformers/all-MiniLM-L6-v2` — small (22 MB), fast (~thousands of sentences/sec on CPU), and hits ~80% of the quality of bigger models. Good default.


# %% color=lime title="Embed the corpus"
# @explain: Embed the corpus
# @explain: Pairwise cosine similarity (since we normalised, dot product = cosine)
from sentence_transformers import SentenceTransformer

embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
print("embedding dim:", embedder.get_sentence_embedding_dimension())

# Embed the corpus
corpus_texts = [d["text"] for d in docs]
embeddings = embedder.encode(corpus_texts, show_progress_bar=False, normalize_embeddings=True)
print("embeddings shape:", embeddings.shape)

# Pairwise cosine similarity (since we normalised, dot product = cosine)
sim = embeddings @ embeddings.T
sim_df = pd.DataFrame(sim.round(2), index=df["id"], columns=df["id"])
print("\nsimilarity matrix:")
print(sim_df)


# %% [markdown] color=teal title="Read the matrix:** `pandas` ↔ `numpy` should be high"
# # Read the matrix:** `pandas` ↔ `numpy` should be high
#
# **Read the matrix:** `pandas` ↔ `numpy` should be high (both are scientific Python libs); `ada` ↔ `deepseek` should be low.


# %% [markdown] color=sky title="4 · Vector DB — Build the Store"
# # 4 · Vector DB — Build the Store
#
# For demos, **NumPy + dot product** is enough. For production with millions of docs, you need a vector DB. Two free options:
#
# | | **FAISS** | **Chroma** |
# |---|---|---|
# | Use case | research, max throughput | apps, ergonomic API |
# | Storage | in-memory or sharded files | embedded SQLite under the hood |
# …


# %% color=mint title="import chromadb"
# @explain: Run this cell to see the output.
import chromadb

client = chromadb.Client()
collection = client.create_collection(name="docs")

collection.add(
    ids=[d["id"] for d in docs],
    documents=[d["text"] for d in docs],
    metadatas=[{"title": d["title"]} for d in docs],
    embeddings=embeddings.tolist(),
)
print(f"stored {collection.count()} documents")


# %% [markdown] color=peach title="Run a query — your first retrieval"
# # Run a query — your first retrieval
#


# %% color=violet title="def search(query"
# @explain: Run this cell to see the output.
def search(query, k=3):
    """Embed the query, return top-k docs + similarity scores."""
    q_emb = embedder.encode([query], normalize_embeddings=True)
    res = collection.query(query_embeddings=q_emb.tolist(), n_results=k)
    return [(meta["title"], doc, 1 - dist)
            for meta, doc, dist in zip(res["metadatas"][0], res["documents"][0], res["distances"][0])]

print("Q: Who created NumPy?")
for title, doc, score in search("Who created NumPy?", k=3):
    print(f"  ({score:.3f}) [{title}]  {doc[:100]}...")

print("\nQ: When was Python released?")
for title, doc, score in search("When was Python released?", k=3):
    print(f"  ({score:.3f}) [{title}]  {doc[:100]}...")


# %% [markdown] color=amber title="5 · Chunking Strategies — How to Split Long Documents"
# # 5 · Chunking Strategies — How to Split Long Documents
#
# Real documents are PDFs and articles, not 80-token blurbs. You need to split them into chunks BEFORE embedding. Three common strategies:
#
# | Strategy | When | Pros | Cons |
# |---|---|---|---|
# | **Fixed-size** (e.g. 256 tokens) | quickest baseline | simple, predictable | breaks mid-sentence |
# | **Recursive character** (LangChain default) | most prose | respects paragraph/sentence boundaries | slightly slower |
# …


# %% color=rose title="def fixed_chunks(text"
# @explain: Run this cell to see the output.
def fixed_chunks(text, size=200, overlap=40):
    """Split text into fixed-character chunks with OVERLAP — the most common baseline."""
    out = []
    for i in range(0, len(text), size - overlap):
        out.append(text[i:i + size])
    return out

long_doc = (docs[3]["text"] + " " + docs[4]["text"] + " " + docs[5]["text"]) * 3
print(f"original length: {len(long_doc)} chars")

chunks = fixed_chunks(long_doc, size=200, overlap=40)
print(f"chunks: {len(chunks)}, avg len {np.mean([len(c) for c in chunks]):.0f}")
print("\nfirst chunk:\n", chunks[0])


# %% [markdown] color=lime title="Why overlap matters:** without it, a key fact that…"
# # Why overlap matters:** without it, a key fact that…
#
# **Why overlap matters:** without it, a key fact that straddles a chunk boundary gets split and neither half is retrievable for the full query. Overlap of ~10-20% of chunk size is the standard heuristic.


# %% [markdown] color=teal title="6 · Retrieval Quality — Recall@k & MRR"
# # 6 · Retrieval Quality — Recall@k & MRR
#
# You can't improve what you don't measure. Build a small **eval set** of (query, expected_doc_id) pairs, then score:
#
# | Metric | What it measures |
# |---|---|
# | **Recall@k** | did the right doc appear in the top-k? |
# | **MRR** (mean reciprocal rank) | how high did it rank? `1/rank` averaged over queries |


# %% color=sky title="eval_set = ["
# @explain: Run this cell to see the output.
eval_set = [
    ("Who created NumPy?",                "numpy"),
    ("When was Python released?",         "py-history"),
    ("What is the Transformer paper?",    "transformer"),
    ("Tell me about DeepSeek's expert routing.", "deepseek"),
    ("Who wrote the first computer program?",    "ada"),
    ("What does PyTorch use for graphs?", "pytorch"),
]

def evaluate(k=3):
    hits, mrr_total = 0, 0.0
    for query, expected_id in eval_set:
        q_emb = embedder.encode([query], normalize_embeddings=True)
        res = collection.query(query_embeddings=q_emb.tolist(), n_results=k)
        ranked_ids = res["ids"][0]
        if expected_id in ranked_ids:
            hits += 1
            mrr_total += 1 / (ranked_ids.index(expected_id) + 1)
    return {"recall@k": hits/len(eval_set), "MRR": mrr_total/len(eval_set)}

for k in [1, 3, 5]:
    print(f"k={k}: {evaluate(k)}")


# %% [markdown] color=mint title="7 · Hybrid Search — BM25 + Vector"
# # 7 · Hybrid Search — BM25 + Vector
#
# Pure vector search misses **exact keyword matches** ("DeepSeek-V3", error codes, model numbers). Pure keyword search misses **paraphrases** ("created" vs "developed by"). The fix: use BOTH, then combine the scores.


# %% color=peach title="1) vector scores"
# @explain: 1) vector scores (cosine via dot product since normalised)
# @explain: 2) BM25 scores
# @explain: 3) weighted sum
from rank_bm25 import BM25Okapi
import re

def tokenize(t): return re.findall(r"\w+", t.lower())

bm25_corpus = [tokenize(d["text"]) for d in docs]
bm25 = BM25Okapi(bm25_corpus)

def hybrid_search(query, k=3, alpha=0.5):
    """alpha = weight of vector score; (1-alpha) = weight of BM25."""
    # 1) vector scores (cosine via dot product since normalised)
    q_emb = embedder.encode([query], normalize_embeddings=True)[0]
    vec_scores = embeddings @ q_emb

    # 2) BM25 scores
    bm25_scores = np.array(bm25.get_scores(tokenize(query)))
    if bm25_scores.max() > 0:
        bm25_scores = bm25_scores / bm25_scores.max()

    # 3) weighted sum
    combined = alpha * vec_scores + (1 - alpha) * bm25_scores
    top = np.argsort(-combined)[:k]
    return [(docs[i]["title"], combined[i]) for i in top]

print("Q: DeepSeek-V3 expert routing")
for title, score in hybrid_search("DeepSeek-V3 expert routing", k=3):
    print(f"  ({score:.3f}) {title}")


# %% [markdown] color=violet title="8 · Reranking — Cross-Encoder for the Top-K"
# # 8 · Reranking — Cross-Encoder for the Top-K
#
# Vector search retrieves CHEAPLY across millions of docs but at lower precision. **Cross-encoder rerankers** are slower but much more accurate — feed them the top-20 from vector search, get back the top-3 most relevant.


# %% color=amber title="Step 1: get a wide vector candidate set"
# @explain: Step 1: get a wide vector candidate set (top-5)
from sentence_transformers import CrossEncoder

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

def rerank(query, candidates):
    pairs = [[query, c["text"]] for c in candidates]
    scores = reranker.predict(pairs)
    return [c for _, c in sorted(zip(scores, candidates), reverse=True)]

# Step 1: get a wide vector candidate set (top-5)
q = "Who released TensorFlow?"
q_emb = embedder.encode([q], normalize_embeddings=True)
top5 = collection.query(query_embeddings=q_emb.tolist(), n_results=5)
candidates = [{"id": i, "text": t, "title": m["title"]}
              for i, t, m in zip(top5["ids"][0], top5["documents"][0], top5["metadatas"][0])]

print("Vector top-5 (in order):")
for c in candidates: print(f"  - {c['title']}")

print("\nReranked top-5:")
for c in rerank(q, candidates): print(f"  - {c['title']}")


# %% [markdown] color=rose title="9 · End-to-End Mini-RAG"
# # 9 · End-to-End Mini-RAG
#
# Now we glue it together: question → retrieve → stuff into prompt → ask an LLM. We'll use a **small** LLM (`google/flan-t5-base`, 250 MB) so it runs on CPU.


# %% color=lime title="1) retrieve"
# @explain: 1) retrieve
# @explain: 2) prompt
# @explain: 3) generate
from transformers import pipeline

generator = pipeline("text2text-generation", model="google/flan-t5-base")

PROMPT = """Use the context below to answer the question.
If the context does not contain the answer, say "I don't know".

Context:
{context}

Question: {question}
Answer:"""

def rag_answer(question, k=3, max_new=100):
    # 1) retrieve
    q_emb = embedder.encode([question], normalize_embeddings=True)
    res = collection.query(query_embeddings=q_emb.tolist(), n_results=k)
    ctx = "\n\n".join(res["documents"][0])

    # 2) prompt
    prompt = PROMPT.format(context=ctx, question=question)

    # 3) generate
    out = generator(prompt, max_new_tokens=max_new, do_sample=False)[0]["generated_text"]

    return {"answer": out, "sources": [m["title"] for m in res["metadatas"][0]]}

for q in ["Who created NumPy?",
          "What is the Transformer paper?",
          "What is DeepSeek-V3?",
          "What's the speed of light?"]:        # ← out-of-corpus
    r = rag_answer(q)
    print(f"\nQ: {q}")
    print(f"A: {r['answer']}")
    print(f"   sources: {r['sources']}")


# %% [markdown] color=teal title="Reading the output:** the in-corpus questions get…"
# # Reading the output:** the in-corpus questions get…
#
# **Reading the output:** the in-corpus questions get grounded answers + sources. The "speed of light" question has no relevant context → the model should refuse with "I don't know". This refusal pattern is the foundation of safe RAG.


# %% [markdown] color=sky title="10 · Where This Scales"
# # 10 · Where This Scales
#
# | Need | Tool |
# |---|---|
# | Higher-level RAG framework | **LangChain**, **LlamaIndex** (chunking + retrievers + chains) |
# | Hosted vector DB | **Pinecone**, **Weaviate**, **Qdrant**, **pgvector** (in Postgres) |
# | Better embeddings | **OpenAI text-embedding-3**, **Cohere Embed v3**, **bge-large-en** |
# | Better rerankers | **Cohere Rerank**, **bge-reranker** |
# …


# %% [markdown] color=mint title="11 · Practice — Try Yourself"
# # 11 · Practice — Try Yourself
#
# 1. **Add 3 new docs** about your favourite topic. Re-build the embeddings + collection. Query something only your docs would know.
# 2. **Tune `alpha` for hybrid search** (sweep 0.0 → 1.0). Plot recall@3 across the eval set. Where's the sweet spot?
# 3. **Compare fixed-size vs recursive chunking** on the long_doc from §5. Which gives more retrievable chunks for a query about TensorFlow's static graphs?
# 4. **Add a citation** field to `rag_answer` — return a markdown answer with `[1]`, `[2]` style citations linking to source titles.


# %% [markdown] color=peach title="Recap"
# # Recap
#
# ✅ Choose **RAG vs fine-tuning** for the right job
# ✅ Build the 5-stage RAG pipeline from scratch
# ✅ Embed text with `sentence-transformers`
# ✅ Store and query vectors with **Chroma**
# ✅ Pick a chunking strategy and tune overlap
# ✅ Measure retrieval with recall@k and MRR — *before* trusting your RAG
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


