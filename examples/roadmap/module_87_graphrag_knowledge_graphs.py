# doodlecode format-version: 2
# Auto-converted from module_87_graphrag_knowledge_graphs.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 87 Graphrag Knowledge Graphs"
# # Module 87 Graphrag Knowledge Graphs
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 87 — GraphRAG + Knowledge Graphs"
# # Module 87 — GraphRAG + Knowledge Graphs
#
# > **M30 vanilla RAG** retrieves the top-`k` semantically similar chunks for a query. That works great for "summarise this PDF" but **silently fails** on multi-hop questions: *"Which engineers worked on the Q3 reorg AND have approved budget authority for the next fiscal year?"* No single chunk contains both facts. **GraphRAG** — Microsoft's 2024 paper and the open-source movement that followed — fixes this by building a **knowledge graph** from your corpus and traversing it at query time. Plus structured citations, plus multi-hop reasoning, plus better-tasting "executive summary" outputs.
# >
# > This module: the graph primer you need, the Microsoft GraphRAG recipe, the open-source alternatives, and when to reach for graph + vector hybrid retrieval vs plain vector RAG.
#
# ### What you'll cover
# 1. Why vanilla RAG fails on multi-hop + global-summary questions
# …


# %% [markdown] color=mint title="1 · Why vanilla RAG fails on the hard questions"
# # 1 · Why vanilla RAG fails on the hard questions
#
# The M30 setup: chunk the corpus, embed, store in a vector DB (M42), retrieve top-`k` by cosine similarity, stuff into the prompt. Three failure modes you'll hit at scale:
#
# | Question shape | Why vanilla RAG breaks |
# |---|---|
# | **Multi-hop** — "which projects did engineers in the Search team ship that the CFO approved?" | the answer requires joining ≥ 2 facts that live in *different* chunks; cosine alone can't traverse the join |
# | **Global summary** — "give me the top 5 themes in the entire codebase reorganisation programme this year" | top-`k` chunks miss the *whole-corpus* signal — you'd need to read everything |
# …


# %% [markdown] color=peach title="2 · Knowledge-graph primer"
# # 2 · Knowledge-graph primer
#
# A knowledge graph (KG) is **nodes** (entities) connected by **edges** (relations). Two big traditions:
#
# | Tradition | Standards / tooling | What dominates today |
# |---|---|---|
# | **RDF (Resource Description Framework)** | W3C; triples `(subject, predicate, object)`; **SPARQL** query language; **OWL** ontology language | Wikidata, DBpedia, scientific KGs, the open semantic web |
# | **Property graph** | nodes + edges, each with arbitrary key-value properties; **Cypher** + **Gremlin** query languages | Neo4j, Memgraph, Amazon Neptune, NebulaGraph — the production-data world |
# …


# %% [markdown] color=violet title="3 · Neo4j + Cypher essentials"
# # 3 · Neo4j + Cypher essentials
#
# Cypher reads like ASCII art of a graph: `()` for nodes, `-[]->` for edges. **Ten queries** that cover 90% of what you'll write.


# %% color=amber title="Spin up Neo4j locally:  docker run -p 7687:7687 -p…"
# @explain: Spin up Neo4j locally:  docker run -p 7687:7687 -p 7474:7474 -e NEO4J_AUTH=none neo4j
# @explain: Then connect with the official driver:
# @explain: pip install neo4j
# @explain: 1
# @explain: 2
# Spin up Neo4j locally:  docker run -p 7687:7687 -p 7474:7474 -e NEO4J_AUTH=none neo4j
# Then connect with the official driver:

neo4j_basics = '''
# pip install neo4j

from neo4j import GraphDatabase
driver = GraphDatabase.driver("bolt://localhost:7687", auth=None)

with driver.session() as s:
    # 1. CREATE nodes + a relationship
    s.run(r'''
      CREATE (a:Person {name: "Alice", title: "VP Engineering"})
      CREATE (b:Person {name: "Bob",   title: "Engineer"})
      CREATE (a)-[:MANAGES {since: 2023}]->(b)
    ''')

    # 2. MATCH (read pattern) — who does Alice manage?
    rows = s.run(r'''
      MATCH (a:Person {name: "Alice"})-[:MANAGES]->(b)
      RETURN b.name AS report
    ''').data()
    print(rows)   # [{'report': 'Bob'}]

    # 3. MERGE = upsert (create if missing, match otherwise)
    s.run("MERGE (p:Person {name: $name}) RETURN p", name="Carol")

    # 4. Properties + labels filter
    s.run(r'''
      MATCH (e:Person {title: "Engineer"})
      RETURN e.name
    ''')

    # 5. 2-HOP traversal — "who manages people who report to Alice?"
    s.run(r'''
      MATCH (a:Person {name: "Alice"})-[:MANAGES]->(:Person)<-[:MANAGES]-(boss)
      RETURN boss.name
    ''')

    # 6. SHORTEST PATH between two nodes
    s.run(r'''
      MATCH p = shortestPath(
        (a:Person {name: "Alice"})-[*..6]-(c:Person {name: "Carol"})
      )
      RETURN [n IN nodes(p) | n.name] AS path
    ''')

    # 7. AGGREGATION — count of reports per manager
    s.run(r'''
      MATCH (m:Person)-[:MANAGES]->(r:Person)
      RETURN m.name, count(r) AS direct_reports
      ORDER BY direct_reports DESC
    ''')

    # 8. Add an index for fast lookup (production essential)
    s.run("CREATE INDEX person_name IF NOT EXISTS FOR (p:Person) ON (p.name)")

    # 9. Vector property + index (Neo4j 5.11+) — for graph + vector hybrid
    s.run(r'''
      CALL db.index.vector.createNodeIndex(
        'doc_embeddings', 'Document', 'embedding', 1536, 'cosine')
    ''')

    # 10. Cypher's CALL ... YIELD — invoke procedures (graph algorithms via GDS)
    s.run(r'''
      CALL gds.pageRank.stream({
        nodeProjection: 'Person',
        relationshipProjection: 'MANAGES'
      })
      YIELD nodeId, score
      RETURN gds.util.asNode(nodeId).name AS person, score
      ORDER BY score DESC LIMIT 10
    ''')
'''
print(neo4j_basics)


# %% [markdown] color=rose title="Three Cypher patterns to internalise"
# # Three Cypher patterns to internalise
#
# **Three Cypher patterns to internalise:**
# 1. **`MATCH (a)-[:R]->(b)`** — pattern matching is *the* primitive; everything else is sugar.
# 2. **`MERGE`** — atomic upsert; use it on every entity write or you get duplicates.
# 3. **`OPTIONAL MATCH`** — like LEFT JOIN; matches when possible, returns NULL when not.
#
# Production rule: **always create an index on the property you `MATCH` by** (`CREATE INDEX person_name FOR (p:Person) ON (p.name)`) — without it, every query is a full scan.


# %% [markdown] color=lime title="4 · LLM-driven graph construction"
# # 4 · LLM-driven graph construction
#
# You rarely *have* a clean KG. You usually have **unstructured documents**. The 2024+ recipe: use an LLM to extract `(entity, relation, entity)` triples from raw text.


# %% color=teal title="Pattern: LLM-as-extractor"
# @explain: Pattern: LLM-as-extractor
# @explain: 1
# @explain: 2
# @explain: Result in Neo4j:
# @explain: (:Person {id:"Alice"})-[:MANAGES]->(:Project {id:"Q3 reorg"})
# Pattern: LLM-as-extractor. Pseudocode using LangChain's LLMGraphTransformer.
graph_construction = '''
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_openai import ChatOpenAI
from langchain_community.graphs import Neo4jGraph
from langchain_core.documents import Document

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
graph = Neo4jGraph(url="bolt://localhost:7687", username="neo4j", password="...")

# 1. Build the transformer — optionally constrain to an ontology
transformer = LLMGraphTransformer(
    llm=llm,
    allowed_nodes=["Person", "Project", "Document", "Company"],
    allowed_relationships=["MANAGES", "AUTHORED", "MENTIONS", "WORKS_AT"],
    strict_mode=True,                              # reject anything not in the allowed lists
)

# 2. Extract triples from raw text
docs = [Document(page_content='''
   Alice (VP Engineering at Acme) leads the Q3 reorg project. The plan, authored by
   Bob and Carol, will be reviewed by the CFO in October. The Acme CTO mentioned
   the project in last week all-hands.
''')]
graph_docs = transformer.convert_to_graph_documents(docs)
graph.add_graph_documents(graph_docs, baseEntityLabel=True, include_source=True)

# Result in Neo4j:
#   (:Person {id:"Alice"})-[:MANAGES]->(:Project {id:"Q3 reorg"})
#   (:Person {id:"Bob"})-[:AUTHORED]->(:Project {id:"Q3 reorg plan"})
#   (:Company {id:"Acme"})-[:EMPLOYS]->(:Person {id:"Alice"})
#   ...
'''
print(graph_construction)


# %% [markdown] color=sky title="Five common pitfalls** and how to fix them"
# # Five common pitfalls** and how to fix them
#
# **Five common pitfalls** and how to fix them:
#
# | Pitfall | Fix |
# |---|---|
# | **Entity duplication** ("Alice" vs "Alice Smith" vs "VP Engineering Alice") | Run an **entity-resolution** pass over extracted nodes — embedding similarity + heuristics, or use Neo4j's `node similarity` |
# | **Schema drift** — different runs invent new relationship types | `strict_mode=True` + a fixed `allowed_relationships` list |
# | **Hallucinated edges** | post-filter: drop any triple not explicitly stated; use stronger model for extraction |
# | **Long-document context loss** | chunk + extract per chunk + dedupe globally |
# …


# %% [markdown] color=mint title="5 · Microsoft GraphRAG (2024) — the recipe that started the term"
# # 5 · Microsoft GraphRAG (2024) — the recipe that started the term
#
# [Microsoft Research, July 2024](https://arxiv.org/abs/2404.16130). Pipeline:
#
# ```
#    1.  Chunk documents
#                 │
#                 ▼
# …


# %% [markdown] color=peach title="6 · LightRAG, nano-graphrag, and the OSS GraphRAG explosion"
# # 6 · LightRAG, nano-graphrag, and the OSS GraphRAG explosion
#
# The Microsoft paper was open-sourced, but slow and expensive. Five open-source variants you'll meet:
#
# | Project | Notes |
# |---|---|
# | **Microsoft GraphRAG** | the canonical reference; Python; PostgreSQL or in-memory storage; LLM-heavy |
# | **nano-graphrag** | ~1000-line minimal reimplementation; great for learning + customisation |
# …


# %% [markdown] color=violet title="7 · Hybrid graph + vector retrieval — the production pattern"
# # 7 · Hybrid graph + vector retrieval — the production pattern
#
# Most production stacks **combine** vector RAG (M30) with KG retrieval. The pattern:
#
# ```
#                 ┌─── classify query intent ────┐
#                 │                              │
#                 ▼                              ▼
# …


# %% [markdown] color=amber title="8 · LLM-generated Cypher — text-to-graph-query"
# # 8 · LLM-generated Cypher — text-to-graph-query
#
# For questions whose answer is *just a graph query* (not a paragraph), let the LLM **write the Cypher**, execute it, and summarise the result.


# %% color=rose title="Behind the scenes the LLM generated something like"
# @explain: Behind the scenes the LLM generated something like:
# @explain: MATCH (a:Person {name: "Alice"})-[:MANAGES*1..3]->(p:Person)
# @explain: RETURN p.name
text_to_cypher = '''
from langchain_neo4j import GraphCypherQAChain
from langchain_neo4j import Neo4jGraph
from langchain_openai import ChatOpenAI

graph = Neo4jGraph(url="bolt://localhost:7687", username="neo4j", password="...")
graph.refresh_schema()   # introspect labels + relationship types

chain = GraphCypherQAChain.from_llm(
    llm=ChatOpenAI(model="gpt-4o-mini", temperature=0),
    graph=graph,
    verbose=True,
    return_intermediate_steps=True,
    allow_dangerous_requests=False,        # disable arbitrary writes
)

ans = chain.invoke({"query": "Which engineers report (directly or indirectly) to Alice?"})
print(ans["result"])
# Behind the scenes the LLM generated something like:
#   MATCH (a:Person {name: "Alice"})-[:MANAGES*1..3]->(p:Person)
#   RETURN p.name
'''
print(text_to_cypher)


# %% [markdown] color=lime title="Production guards for LLM-generated Cypher"
# # Production guards for LLM-generated Cypher
#
# **Production guards for LLM-generated Cypher:**
# 1. **Read-only by default** — `allow_dangerous_requests=False` blocks `CREATE/DELETE/MERGE`.
# 2. **Schema injection** — give the LLM the live schema (`refresh_schema()`) so it generates valid labels + relationship types.
# 3. **Cypher validation** — parse the LLM's output before executing (Neo4j EXPLAIN; catches syntax errors cheaply).
# 4. **Query timeout + row cap** — `LIMIT 200`; abort runaway joins.
# 5. **Audit log** — every executed Cypher → SIEM with `tenant_id` (M51 / M80).
#
# LLM-generated Cypher is one of the few text-to-X tools that actually works in production today, *because the query language is tightly constrained.*


# %% [markdown] color=teal title="9 · Adjacent ideas worth knowing"
# # 9 · Adjacent ideas worth knowing
#
# | Idea | What it adds |
# |---|---|
# | **HippoRAG** (Stanford 2024) | hippocampus-inspired memory; one-pass indexing with Personalised PageRank for retrieval |
# | **RAPTOR** | recursive tree of summaries; alternative to graph + community summaries |
# | **ReadAgent** | LLM agent that reads + gists + jumps through long docs |
# | **GraphReader** | converts the document into a graph, then the LLM "walks" it as an agent |
# …


# %% [markdown] color=sky title="10 · Production graph stack"
# # 10 · Production graph stack
#
# | Engine | Strengths | Watch for |
# |---|---|---|
# | **Neo4j AuraDB / Community / Enterprise** | biggest ecosystem; **vector index built-in** since 5.11; **GDS** library for graph algorithms | Enterprise license cost |
# | **Memgraph** | in-memory, fast for streaming graphs; Cypher-compatible | smaller community |
# | **Kùzu** | embedded, columnar (DuckDB-style); excellent for analytics + LLM workloads | younger; fewer integrations |
# | **NebulaGraph** | distributed, very large graphs | steep ops learning curve |
# …


# %% [markdown] color=mint title="11 · When to pick what — the decision tree"
# # 11 · When to pick what — the decision tree
#
# ```
#    Is the question a JOIN or MULTI-HOP across entities?           ► YES → GRAPH RAG
#                                                                    ► NO  ──┐
#    Does the answer require reading a SPECIFIC document chunk?     ► YES → VANILLA RAG (M30)
#                                                                    ► NO  ──┐
#    Is the question STRUCTURED + over tabular data?                ► YES → SQL ON A WAREHOUSE / pgvector (M36)
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


