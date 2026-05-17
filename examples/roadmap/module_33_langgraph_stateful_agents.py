# doodlecode format-version: 2
# Auto-converted from module_33_langgraph_stateful_agents.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 33 Langgraph Stateful Agents"
# # Module 33 Langgraph Stateful Agents
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 33 — LangGraph: Stateful Agents"
# # Module 33 — LangGraph: Stateful Agents
#
# > M32's **chains** are pipelines: input → step → step → step → done. Real agents need **loops, branches, retries, conditional steps, and persistent state**. That's what **LangGraph** gives you — it models your agent as a state machine (a directed graph of nodes), not a chain.
#
# LangGraph powers production agents at OpenAI, Anthropic-using companies, and most "ChatGPT-with-tools" apps shipped in 2025-2026. It's how `LangChain.AgentExecutor` is being replaced.
#
# ### What you'll cover
# 1. Chain vs Graph — when each is the right shape
# …


# %% [markdown] color=mint title="1 · Chain vs Graph — When Each Is Right"
# # 1 · Chain vs Graph — When Each Is Right
#
# | Pattern | LangChain (LCEL chain) | LangGraph (state graph) |
# |---|---|---|
# | Strict pipeline | ✅ ideal | overkill |
# | Looping until a condition | ❌ awkward | ✅ native |
# | Branching on intermediate results | ❌ painful | ✅ `add_conditional_edges` |
# | Pause-and-resume / human approval | ❌ no | ✅ checkpointers |
# …


# %% [markdown] color=peach title="2 · The Three LangGraph Primitives"
# # 2 · The Three LangGraph Primitives
#
# ```python
# from langgraph.graph import StateGraph, START, END
#
# # 1. STATE — what flows through the graph
# class MyState(TypedDict):
#     counter: int
# …


# %% color=violet title="!pip -q install langgraph langchain…"
# @explain: Run this cell to see the output.
!pip -q install langgraph langchain langchain-huggingface transformers
import warnings; warnings.filterwarnings("ignore")


# %% [markdown] color=amber title="3 · Your First Graph — No LLM Yet"
# # 3 · Your First Graph — No LLM Yet
#
# Build a counter graph that runs three increment nodes in sequence. Every concept is visible without LLM noise.


# %% color=rose title="Build the graph"
# @explain: Build the graph
# @explain: Run it
from typing import TypedDict, List
from langgraph.graph import StateGraph, START, END

class CountState(TypedDict):
    counter: int
    log: List[str]

def double(state: CountState) -> dict:
    new = state["counter"] * 2
    return {"counter": new, "log": state["log"] + [f"doubled to {new}"]}

def add_ten(state: CountState) -> dict:
    new = state["counter"] + 10
    return {"counter": new, "log": state["log"] + [f"+10 → {new}"]}

def square(state: CountState) -> dict:
    new = state["counter"] ** 2
    return {"counter": new, "log": state["log"] + [f"squared to {new}"]}

# Build the graph
g = StateGraph(CountState)
g.add_node("double", double)
g.add_node("add10",  add_ten)
g.add_node("square", square)

g.add_edge(START,  "double")
g.add_edge("double","add10")
g.add_edge("add10", "square")
g.add_edge("square", END)

app = g.compile()

# Run it
result = app.invoke({"counter": 3, "log": []})
print("final counter:", result["counter"])
print("trace:")
for line in result["log"]:
    print(" -", line)


# %% [markdown] color=lime title="Reading the result:** start at counter=3 → double=6…"
# # Reading the result:** start at counter=3 → double=6…
#
# **Reading the result:** start at counter=3 → double=6 → +10=16 → square=256. The `log` list shows every step. Each node returns a **partial update**; LangGraph merges it into state automatically.


# %% [markdown] color=teal title="4 · Conditional Edges — Branching"
# # 4 · Conditional Edges — Branching
#
# The killer feature. A node decides which node runs next based on the current state.


# %% color=sky title="Conditional router"
# @explain: Conditional router — returns the NAME of the next node
class TriageState(TypedDict):
    text: str
    sentiment: str

def detect_sentiment(state: TriageState) -> dict:
    text = state["text"].lower()
    if any(w in text for w in ["great","love","awesome","amazing"]):
        return {"sentiment": "positive"}
    if any(w in text for w in ["bad","hate","terrible","awful"]):
        return {"sentiment": "negative"}
    return {"sentiment": "neutral"}

def positive_handler(state): return {"text": state["text"] + " [thank-you reply queued]"}
def negative_handler(state): return {"text": state["text"] + " [escalation ticket created]"}
def neutral_handler(state):  return {"text": state["text"] + " [logged for review]"}

# Conditional router — returns the NAME of the next node
def route(state: TriageState) -> str:
    return state["sentiment"]   # "positive" / "negative" / "neutral"

g = StateGraph(TriageState)
g.add_node("detect",   detect_sentiment)
g.add_node("positive", positive_handler)
g.add_node("negative", negative_handler)
g.add_node("neutral",  neutral_handler)

g.add_edge(START, "detect")
g.add_conditional_edges(
    "detect", route,
    {"positive":"positive", "negative":"negative", "neutral":"neutral"},
)
for n in ("positive","negative","neutral"):
    g.add_edge(n, END)

app = g.compile()

for txt in ["The food was great",
             "Terrible service",
             "We had dinner"]:
    print(app.invoke({"text": txt, "sentiment": ""})["text"])


# %% [markdown] color=mint title="Reading the syntax"
# # Reading the syntax
#
# **Reading the syntax:**
# - `add_conditional_edges(source, fn, mapping)` — at `source`, call `fn(state)`, look up the result in `mapping`, jump to that node.
# - The mapping dict is what makes flows EXPLICIT. You always know what nodes can fire next.


# %% [markdown] color=peach title="5 · A ReAct Agent as a Graph — Loops Until Done"
# # 5 · A ReAct Agent as a Graph — Loops Until Done
#
# Here's the classic ReAct pattern from M31, but as a LangGraph state machine instead of `AgentExecutor`. You can SEE the loop.


# %% color=violet title="A simple LLM (same as M32)"
# @explain: A simple LLM (same as M32) — small, runs on CPU
# @explain: Toy tools the agent can call
# @explain: --- nodes ---
# @explain: --- router ---
from typing import Annotated
from langchain_huggingface import HuggingFacePipeline
from transformers import pipeline as hf_pipeline
from operator import add

# A simple LLM (same as M32) — small, runs on CPU
llm = HuggingFacePipeline(pipeline=hf_pipeline(
    "text2text-generation", model="google/flan-t5-base",
    max_new_tokens=120, do_sample=False))

# Toy tools the agent can call
def calculator(expr: str) -> str:
    try: return str(eval(expr, {"__builtins__":{}}))
    except Exception as e: return f"error: {e}"

TOOLS = {"calculator": calculator}

class ReActState(TypedDict):
    question: str
    trace: Annotated[List[str], add]   # Annotated[..., add] = APPEND on update
    final: str

# --- nodes ---
def think(state: ReActState) -> dict:
    """Ask the LLM what to do next given the trace so far."""
    prompt = (f"Question: {state['question']}\n"
              f"Trace so far:\n{chr(10).join(state['trace'])}\n"
              "If you can answer, reply: FINAL: <answer>\n"
              "Otherwise reply: ACTION: calculator(<expression>)")
    out = llm.invoke(prompt).strip()
    return {"trace": [f"Thought: {out}"]}

def act(state: ReActState) -> dict:
    """Parse the last Thought, run the tool, append observation."""
    last = state["trace"][-1]
    if "calculator(" in last:
        expr = last.split("calculator(",1)[1].rsplit(")",1)[0]
        obs = calculator(expr)
    else:
        obs = "no recognised action"
    return {"trace": [f"Observation: {obs}"]}

def finalize(state: ReActState) -> dict:
    """Pull FINAL: <answer> out of the trace."""
    for line in reversed(state["trace"]):
        if "FINAL:" in line:
            return {"final": line.split("FINAL:",1)[1].strip()}
    return {"final": "(no final answer)"}

# --- router ---
def route_after_think(state: ReActState) -> str:
    last = state["trace"][-1]
    if "FINAL:" in last:        return "finalize"
    if "ACTION:" in last:       return "act"
    return "finalize"             # safety fallback

g = StateGraph(ReActState)
g.add_node("think",    think)
g.add_node("act",       act)
g.add_node("finalize",  finalize)

g.add_edge(START, "think")
g.add_conditional_edges("think", route_after_think,
                         {"act":"act", "finalize":"finalize"})
g.add_edge("act", "think")          # ★ THE LOOP — back to think
g.add_edge("finalize", END)

app = g.compile()

result = app.invoke({"question": "What is 17 * 24?", "trace": [], "final": ""})
print("FINAL:", result["final"])
print("\nfull trace:")
for line in result["trace"]:
    print(" -", line)


# %% [markdown] color=amber title="The key line:** `g.add_edge('act', 'think')` —…"
# # The key line:** `g.add_edge("act", "think")` —…
#
# **The key line:** `g.add_edge("act", "think")` — that's the loop. `act` always returns to `think`, which decides whether to act again or finalise. `flan-t5-base` is small and often fumbles ReAct format; with GPT-4o or Claude this just works.


# %% [markdown] color=rose title="6 · Persistence / Checkpoints — Pause and Resume"
# # 6 · Persistence / Checkpoints — Pause and Resume
#
# The killer production feature. Every state transition can be saved automatically. You can pause an agent for human approval, replay from any step, or recover from crashes.


# %% color=lime title="Same triage graph from §4"
# @explain: Same triage graph from §4 — but now with a checkpointer
# @explain: ★ KEY ADDITION — MemorySaver checkpoints state at every step
# @explain: First call — runs to completion
# @explain: We can now INSPECT the saved history
from langgraph.checkpoint.memory import MemorySaver

# Same triage graph from §4 — but now with a checkpointer
g2 = StateGraph(TriageState)
g2.add_node("detect",   detect_sentiment)
g2.add_node("positive", positive_handler)
g2.add_node("negative", negative_handler)
g2.add_node("neutral",  neutral_handler)
g2.add_edge(START, "detect")
g2.add_conditional_edges("detect", route,
                          {"positive":"positive","negative":"negative","neutral":"neutral"})
for n in ("positive","negative","neutral"):
    g2.add_edge(n, END)

# ★ KEY ADDITION — MemorySaver checkpoints state at every step
memory = MemorySaver()
app2 = g2.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "ticket-1"}}

# First call — runs to completion
print(app2.invoke({"text":"Terrible service","sentiment":""}, config)["text"])

# We can now INSPECT the saved history
state = app2.get_state(config)
print("\nlast state:", state.values)
print("next nodes:", state.next)


# %% [markdown] color=teal title="For production: swap `MemorySaver` for…"
# # For production: swap `MemorySaver` for…
#
# For production: swap `MemorySaver` for `PostgresSaver` (Postgres-backed) or `RedisSaver` (Redis-backed). The graph code doesn't change.


# %% [markdown] color=sky title="7 · Streaming Events Through the Graph"
# # 7 · Streaming Events Through the Graph
#
# While the graph runs, you can stream every event — node entries, state updates, LLM tokens — to a UI in real time.


# %% color=mint title="Re-use the counter graph from §3"
# @explain: Re-use the counter graph from §3
# @explain: .stream() yields the state after each node
# Re-use the counter graph from §3
g3 = StateGraph(CountState)
g3.add_node("double", double)
g3.add_node("add10",  add_ten)
g3.add_node("square", square)
g3.add_edge(START,  "double")
g3.add_edge("double","add10")
g3.add_edge("add10", "square")
g3.add_edge("square", END)
app3 = g3.compile()

# .stream() yields the state after each node
for chunk in app3.stream({"counter": 3, "log": []}):
    for node_name, partial_update in chunk.items():
        print(f"  after {node_name}: {partial_update}")


# %% [markdown] color=peach title="In a real app you push these events down a…"
# # In a real app you push these events down a…
#
# In a real app you push these events down a Server-Sent-Events stream so the user watches the agent think.


# %% [markdown] color=violet title="8 · Multi-Agent Pattern — Orchestrator + Workers"
# # 8 · Multi-Agent Pattern — Orchestrator + Workers
#
# Common production setup: ONE LLM **decides** which specialist to call; each specialist is its own subgraph.


# %% color=amber title="class TeamState(TypedDict)"
# @explain: Run this cell to see the output.
class TeamState(TypedDict):
    user_query: str
    plan: str
    answer: str

def orchestrator(state: TeamState) -> dict:
    """Decide which specialist handles this."""
    q = state["user_query"].lower()
    if "code" in q or "python" in q:
        return {"plan": "code"}
    if any(w in q for w in ["calculate","math","compute"]):
        return {"plan": "math"}
    return {"plan": "general"}

def code_worker(state):    return {"answer": f"[CODE WORKER] would write code for: {state['user_query']}"}
def math_worker(state):    return {"answer": f"[MATH WORKER] would solve: {state['user_query']}"}
def general_worker(state): return {"answer": f"[GENERAL] best-effort answer to: {state['user_query']}"}

def pick_worker(state: TeamState) -> str:
    return state["plan"]

g4 = StateGraph(TeamState)
g4.add_node("orchestrator", orchestrator)
g4.add_node("code",          code_worker)
g4.add_node("math",          math_worker)
g4.add_node("general",       general_worker)

g4.add_edge(START, "orchestrator")
g4.add_conditional_edges("orchestrator", pick_worker,
                          {"code":"code","math":"math","general":"general"})
for n in ("code","math","general"):
    g4.add_edge(n, END)

team = g4.compile()

for q in ["Write Python code to sort a list",
          "Calculate the area of a 5x3 rectangle",
          "What is the meaning of life?"]:
    print(team.invoke({"user_query": q, "plan":"", "answer":""})["answer"])


# %% [markdown] color=rose title="9 · Visualising the Graph"
# # 9 · Visualising the Graph
#
# `graph.get_graph().draw_mermaid()` returns a Mermaid diagram you can paste into any markdown — including this notebook.


# %% color=lime title="try"
# @explain: Run this cell to see the output.
try:
    print(team.get_graph().draw_mermaid())
except Exception as e:
    print("(mermaid render needs `pip install mermaid-py` — code shown for reference)")
    print("Try the Mermaid Live Editor: https://mermaid.live")


# %% [markdown] color=teal title="When connected to a notebook with mermaid…"
# # When connected to a notebook with mermaid…
#
# When connected to a notebook with mermaid rendering, this gives you a clickable, zoomable graph diagram. Production teams use this in README files and design docs.


# %% [markdown] color=sky title="10 · Where This Scales"
# # 10 · Where This Scales
#
# | Need | Tool |
# |---|---|
# | Hosted LangGraph runtime | **LangGraph Cloud** (paid SaaS) |
# | Self-hosted | **LangGraph Server** (open source, deploys via Docker) |
# | Tracing + observability | **LangSmith** (M51 covers OpenTelemetry alternative) |
# | Persistence backends | `MemorySaver` / `PostgresSaver` / `RedisSaver` (M36 / M37) |
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


