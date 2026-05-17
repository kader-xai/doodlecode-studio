# doodlecode format-version: 2
# Auto-converted from module_34_llamaindex_production_rag.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 34 Llamaindex Production Rag"
# # Module 34 Llamaindex Production Rag
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 34 — LlamaIndex for Production RAG"
# # Module 34 — LlamaIndex for Production RAG
#
# > M30 built RAG by hand. M32 wrapped it in LangChain. **LlamaIndex** is what serious teams use when RAG is the *primary* product — knowledge bases, doc-search, customer-support copilots. It has stronger document loaders, better chunking, more retrieval strategies, and a cleaner mental model **specifically for RAG**.
#
# This module assumes you've finished **M30 (RAG)** and **M32 (LangChain)**.
#
# ### What you'll cover
# 1. LangChain vs LlamaIndex — when to pick which
# …


# %% [markdown] color=mint title="1 · LangChain vs LlamaIndex — When Each Wins"
# # 1 · LangChain vs LlamaIndex — When Each Wins
#
# | Need | LangChain | LlamaIndex |
# |---|---|---|
# | General LLM pipelines (any task) | ✅ | weaker |
# | Agents / tools / multi-step workflows | ✅ | weaker (use LangGraph) |
# | **RAG with messy real documents** | OK | ✅ best-in-class |
# | Document loaders (PDF, Notion, Slack, Confluence...) | ~80 | **~300** |
# …


# %% [markdown] color=peach title="2 · The Six Core Abstractions"
# # 2 · The Six Core Abstractions
#
# | Building block | What it is |
# |---|---|
# | **Document** | a single source (page, file, scraped URL) with text + metadata |
# | **Node** | a chunk of a Document (after splitting). What actually gets embedded |
# | **Index** | a data structure over nodes (`VectorStoreIndex`, `KeywordTableIndex`, `SummaryIndex`...) |
# | **Retriever** | given a query, returns relevant nodes |
# …


# %% color=violet title="!pip -q install llama-index…"
# @explain: Run this cell to see the output.
!pip -q install llama-index llama-index-embeddings-huggingface llama-index-llms-huggingface llama-index-postprocessor-sbert-rerank
import warnings; warnings.filterwarnings("ignore")


# %% [markdown] color=amber title="3 · Setup — Free Local Models"
# # 3 · Setup — Free Local Models
#
# Same `flan-t5` + `MiniLM` stack as M32/M33 so we don't need API keys.


# %% color=rose title="Embed with MiniLM"
# @explain: Embed with MiniLM (small, fast, CPU-friendly)
# @explain: LLM with flan-t5-base
# @explain: Chunk size for the default splitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.core import Settings

# Embed with MiniLM (small, fast, CPU-friendly)
Settings.embed_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
)

# LLM with flan-t5-base
Settings.llm = HuggingFaceLLM(
    tokenizer_name="google/flan-t5-base",
    model_name="google/flan-t5-base",
    context_window=512, max_new_tokens=200,
    generate_kwargs={"do_sample": False},
)

# Chunk size for the default splitter
Settings.chunk_size = 256
Settings.chunk_overlap = 32
print("LlamaIndex Settings configured (HF embed + flan-t5)")


# %% [markdown] color=lime title="Key idea — `Settings` is global state.** Once you…"
# # Key idea — `Settings` is global state.** Once you…
#
# **Key idea — `Settings` is global state.** Once you set `Settings.llm` and `Settings.embed_model`, every Index, Retriever, and QueryEngine you build picks them up automatically. For OpenAI: just swap the two `Settings` lines.


# %% [markdown] color=teal title="4 · Loading Documents"
# # 4 · Loading Documents
#
# LlamaIndex has the largest document-loader ecosystem in Python. We'll show three patterns: **inline**, **directory**, **URL**.


# %% color=sky title="1) Inline"
# @explain: 1) Inline — for testing
# @explain: 2) Directory — most common in production
# @explain: 3) Web — quick demo
# @explain: from llama_index.readers.web import SimpleWebPageReader
# @explain: web_docs = SimpleWebPageReader(html_to_text=True).load_data(["https://example.com"])
from llama_index.core import Document, SimpleDirectoryReader
import os, tempfile

# 1) Inline — for testing
inline_docs = [
    Document(text="NumPy was created by Travis Oliphant in 2006 and is the foundation of the Python scientific stack.",
             metadata={"source": "numpy", "year": 2006}),
    Document(text="PyTorch was released by Facebook AI Research in 2016 with dynamic computation graphs.",
             metadata={"source": "pytorch", "year": 2016}),
    Document(text="DeepSeek-V3 is a 671B-parameter open-weight Mixture-of-Experts model with Multi-Latent Attention.",
             metadata={"source": "deepseek", "year": 2024}),
]
print(f"inline: {len(inline_docs)} docs")

# 2) Directory — most common in production
tmp = tempfile.mkdtemp()
for d in inline_docs:
    with open(os.path.join(tmp, d.metadata["source"] + ".txt"), "w") as f:
        f.write(d.text)

dir_docs = SimpleDirectoryReader(tmp).load_data()
print(f"directory: {len(dir_docs)} docs (auto-detects .txt/.pdf/.md/.docx)")

# 3) Web — quick demo
# from llama_index.readers.web import SimpleWebPageReader
# web_docs = SimpleWebPageReader(html_to_text=True).load_data(["https://example.com"])


# %% [markdown] color=mint title="5 · Build an Index → Query Engine — 4 Lines"
# # 5 · Build an Index → Query Engine — 4 Lines
#


# %% color=peach title="from llama_index.core import VectorStoreIndex"
# @explain: Run this cell to see the output.
from llama_index.core import VectorStoreIndex

index   = VectorStoreIndex.from_documents(inline_docs)
query   = index.as_query_engine(similarity_top_k=2)

response = query.query("What year was NumPy created?")
print("answer:", response)
print("sources:", [n.metadata.get("source") for n in response.source_nodes])


# %% [markdown] color=violet title="Reading those 4 lines"
# # Reading those 4 lines
#
# **Reading those 4 lines:**
# 1. `VectorStoreIndex.from_documents(...)` — splits, embeds, indexes (uses `Settings`)
# 2. `.as_query_engine(top_k=2)` — wires retriever + LLM
# 3. `.query(...)` — embeds question → retrieves → stuffs into prompt → answers
# 4. `response.source_nodes` — the chunks that grounded the answer (always available — built-in citation support)


# %% [markdown] color=amber title="6 · Custom Chunking — SentenceSplitter and SemanticSplitter"
# # 6 · Custom Chunking — SentenceSplitter and SemanticSplitter
#
# The default `SentenceSplitter` cuts at sentence boundaries near the chunk size. The `SemanticSplitterNodeParser` cuts where the embedding similarity DROPS — semantically coherent chunks.


# %% color=rose title="Default sentence splitter"
# @explain: Default sentence splitter — what we used implicitly in §5
# @explain: Semantic splitter — splits when embeddings DIVERGE
from llama_index.core.node_parser import SentenceSplitter, SemanticSplitterNodeParser

# Default sentence splitter — what we used implicitly in §5
sent_splitter = SentenceSplitter(chunk_size=128, chunk_overlap=20)

long_doc = Document(text=(
    "Python's NumPy library handles numerical arrays. "
    "Pandas builds on NumPy for tabular data. "
    "Matplotlib is the foundation for visualisation. "
    "Switching topic. Football is a popular sport. "
    "The 2022 World Cup was won by Argentina. "
    "Switching again. PyTorch is a deep learning framework. "
    "It uses dynamic computation graphs. "
))

sent_nodes = sent_splitter.get_nodes_from_documents([long_doc])
print(f"SentenceSplitter produced {len(sent_nodes)} nodes:")
for i, n in enumerate(sent_nodes):
    print(f"  [{i}] {n.text[:80]}…")

# Semantic splitter — splits when embeddings DIVERGE
sem_splitter = SemanticSplitterNodeParser(
    buffer_size=1, breakpoint_percentile_threshold=85,
    embed_model=Settings.embed_model,
)
sem_nodes = sem_splitter.get_nodes_from_documents([long_doc])
print(f"\nSemanticSplitter produced {len(sem_nodes)} nodes:")
for i, n in enumerate(sem_nodes):
    print(f"  [{i}] {n.text[:120]}…")


# %% [markdown] color=lime title="Compare the splits.** SentenceSplitter cuts every…"
# # Compare the splits.** SentenceSplitter cuts every…
#
# **Compare the splits.** SentenceSplitter cuts every ~128 chars regardless of topic. SemanticSplitter ideally puts NumPy/Pandas together, football together, PyTorch together — three coherent chunks.


# %% [markdown] color=teal title="7 · Re-Rankers — Second-Stage Refinement"
# # 7 · Re-Rankers — Second-Stage Refinement
#
# Same idea as M30 §7 (cross-encoder reranking). LlamaIndex makes it a one-line postprocessor.


# %% color=sky title="from llama_index.postprocessor.sbert_rerank import…"
# @explain: Run this cell to see the output.
from llama_index.postprocessor.sbert_rerank import SentenceTransformerRerank

reranker = SentenceTransformerRerank(
    model="cross-encoder/ms-marco-MiniLM-L-6-v2",
    top_n=2,                       # keep the best 2 after rerank
)

query = index.as_query_engine(
    similarity_top_k=5,             # retrieve 5 cheap candidates
    node_postprocessors=[reranker], # then rerank to keep the top 2
)

response = query.query("What does DeepSeek-V3 use for attention?")
print("answer:", response)
print("sources:", [n.metadata.get("source") for n in response.source_nodes])


# %% [markdown] color=mint title="Two-stage retrieval pattern:** retrieve 5 cheap…"
# # Two-stage retrieval pattern:** retrieve 5 cheap…
#
# **Two-stage retrieval pattern:** retrieve 5 cheap candidates with a vector index, then a cross-encoder reranks to keep the most relevant 2. Production default.


# %% [markdown] color=peach title="8 · Hierarchical Retrieval — Small Chunks + Parent Context"
# # 8 · Hierarchical Retrieval — Small Chunks + Parent Context
#
# The problem: small chunks → precise retrieval but lose context. Big chunks → richer context but noisier retrieval. Solution: **embed small chunks, but return their parent paragraph for the LLM to read.**


# %% color=violet title="Build a hierarchy: top-level"
# @explain: Build a hierarchy: top-level (1024) → mid (256) → leaf (64) chars
# @explain: Index ONLY the leaf nodes — small + precise
# @explain: AutoMergingRetriever: when many sibling leaves match, return the PARENT
from llama_index.core.node_parser import HierarchicalNodeParser, get_leaf_nodes
from llama_index.core import StorageContext
from llama_index.core.retrievers import AutoMergingRetriever
from llama_index.core.query_engine import RetrieverQueryEngine

# Build a hierarchy: top-level (1024) → mid (256) → leaf (64) chars
hier_parser = HierarchicalNodeParser.from_defaults(chunk_sizes=[1024, 256, 64])
hier_nodes  = hier_parser.get_nodes_from_documents(inline_docs)
leaf_nodes  = get_leaf_nodes(hier_nodes)

# Index ONLY the leaf nodes — small + precise
storage = StorageContext.from_defaults()
storage.docstore.add_documents(hier_nodes)              # all levels in docstore
leaf_index = VectorStoreIndex(leaf_nodes, storage_context=storage)

# AutoMergingRetriever: when many sibling leaves match, return the PARENT
base_retriever  = leaf_index.as_retriever(similarity_top_k=3)
auto_retriever  = AutoMergingRetriever(base_retriever, storage)

query = RetrieverQueryEngine.from_args(auto_retriever)
print(query.query("What is DeepSeek-V3?"))


# %% [markdown] color=amber title="Why this matters:** when 2+ leaf chunks of the same…"
# # Why this matters:** when 2+ leaf chunks of the same…
#
# **Why this matters:** when 2+ leaf chunks of the same parent paragraph all hit a query, the retriever upgrades to returning the parent — giving the LLM the FULL paragraph context instead of fragments.


# %% [markdown] color=rose title="9 · Persistence — Save / Reload the Index"
# # 9 · Persistence — Save / Reload the Index
#
# Re-embedding is expensive. In production you build the index once, persist it, and reload on every server start.


# %% color=lime title="Save"
# @explain: Save
# @explain: Reload (in a fresh process / pod / restart)
import tempfile
persist_dir = tempfile.mkdtemp(prefix="llamaindex_")

# Save
index.storage_context.persist(persist_dir=persist_dir)
print("saved to:", persist_dir)
print("contents:", os.listdir(persist_dir))

# Reload (in a fresh process / pod / restart)
from llama_index.core import StorageContext, load_index_from_storage

storage = StorageContext.from_defaults(persist_dir=persist_dir)
reloaded = load_index_from_storage(storage)

resp = reloaded.as_query_engine().query("Who created NumPy?")
print("\nafter reload:", resp)


# %% [markdown] color=teal title="For production: swap the default file-based store…"
# # For production: swap the default file-based store…
#
# For production: swap the default file-based store for **Chroma**, **Pinecone**, **Weaviate**, **Qdrant**, or **Postgres+pgvector** (M36). The graph code doesn't change — just the `vector_store` argument to `VectorStoreIndex`.


# %% [markdown] color=sky title="10 · Where This Scales"
# # 10 · Where This Scales
#
# | Need | Tool |
# |---|---|
# | **Messy PDFs / tables / images** | **LlamaParse** (paid SaaS by LlamaIndex; first 1k pages/day free) |
# | Hosted RAG-as-a-Service | **LlamaCloud** |
# | Better retrievers | **Hybrid** (vector + BM25), **Recursive**, **Auto-Merging**, **HyDE** |
# | Eval framework | **Trulens**, **Ragas** (M31) |
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


