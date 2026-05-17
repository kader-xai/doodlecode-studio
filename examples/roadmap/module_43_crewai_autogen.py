# doodlecode format-version: 2
# Auto-converted from module_43_crewai_autogen.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 43 Crewai Autogen"
# # Module 43 Crewai Autogen
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 43 — crewAI & AutoGen"
# # Module 43 — crewAI & AutoGen
#
# > A single LLM agent (M32 LangChain, M33 LangGraph) is one actor with tools. **Multi-agent** systems compose multiple specialised agents — a Researcher, a Writer, a Critic — that **talk to each other** to solve a task. The two leading frameworks: **crewAI** (role-based, declarative, easy to read) and **AutoGen** from Microsoft (conversation-based, programmable, built for tool-using agents).
# >
# > This module shows **the same task in both frameworks** so you can pick.
#
# ### What you'll cover
# 1. When multi-agent helps — and when it just adds tokens
# …


# %% [markdown] color=mint title="1 · When multi-agent actually helps"
# # 1 · When multi-agent actually helps
#
# Multi-agent is **not free** — every "agent talks to agent" turn is another LLM call. Use it when:
#
# | ✅ Good fit | ❌ Bad fit |
# |---|---|
# | Tasks have **clear sub-roles** (research → write → review) | Single-shot Q&A; one LLM call is enough |
# | You want **explicit critique / verification** of an output | Anywhere a chain-of-thought prompt would do |
# …


# %% [markdown] color=peach title="2 · Two mental models"
# # 2 · Two mental models
#
# | | **crewAI** | **AutoGen** |
# |---|---|---|
# | Mental model | **Crew of role-based experts** working a list of tasks | **Conversation** between agents that route messages |
# | Style | Declarative (configure agents + tasks, run) | Programmatic (you wire conversations) |
# | Strengths | Clear, readable, easy onboarding | Tool use, code execution, group chats with managers |
# | Weaknesses | Less control over per-message routing | More code, more concepts |
# …


# %% [markdown] color=violet title="3 · Setup — point at Ollama (free) or OpenAI"
# # 3 · Setup — point at Ollama (free) or OpenAI
#
# We assume Ollama is already running on `http://localhost:11434` (M38). If not, restart this section after running the M38 setup cells.


# %% color=amber title="!pip -q install crewai==0.86.0 'crewai-tools'…"
# @explain: Run this cell to see the output.
!pip -q install crewai==0.86.0 "crewai-tools" pyautogen==0.4.0 ollama


# %% color=rose title="point both frameworks at Ollama via OpenAI-compat"
# @explain: point both frameworks at Ollama via OpenAI-compat
import os
# point both frameworks at Ollama via OpenAI-compat
os.environ["OPENAI_API_KEY"]   = "ollama"            # any non-empty string
os.environ["OPENAI_API_BASE"]  = "http://localhost:11434/v1"
os.environ["OPENAI_MODEL_NAME"]= "qwen2.5:0.5b-instruct"   # tiny, free, fast on CPU
print("ENV ready")


# %% [markdown] color=lime title="4 · crewAI — Researcher → Writer → Critic"
# # 4 · crewAI — Researcher → Writer → Critic
#


# %% color=teal title="Tell crewAI to talk to local Ollama through the…"
# @explain: Tell crewAI to talk to local Ollama through the OpenAI-compat shim
from crewai import Agent, Task, Crew, Process
from crewai.llm import LLM

# Tell crewAI to talk to local Ollama through the OpenAI-compat shim
local_llm = LLM(model="openai/qwen2.5:0.5b-instruct",
                base_url="http://localhost:11434/v1",
                api_key="ollama")

researcher = Agent(
    role="Senior Researcher",
    goal="Find three concrete facts about the topic.",
    backstory="You are meticulous and cite sources.",
    llm=local_llm,
    verbose=True,
)
writer = Agent(
    role="Tech Writer",
    goal="Turn the researcher's bullets into a 5-sentence summary.",
    backstory="You write tight, no fluff.",
    llm=local_llm,
    verbose=True,
)
critic = Agent(
    role="Editor",
    goal="Find at least one weakness in the draft and suggest a fix.",
    backstory="You are direct and constructive.",
    llm=local_llm,
    verbose=True,
)


# %% color=sky title="result = crew.kickoff()      # uncomment to…"
# @explain: result = crew.kickoff()      # uncomment to actually run; takes ~30-60s on CPU Ollama
# @explain: print(result)
topic = "The Transformer attention mechanism"

t_research = Task(description=f"Research the topic: {topic}. Output 3 bullet points.",
                  expected_output="3 bullet points with sources",
                  agent=researcher)
t_write    = Task(description="Write a 5-sentence summary using the bullets.",
                  expected_output="5-sentence paragraph",
                  agent=writer,
                  context=[t_research])
t_critique = Task(description="Critique the draft. Suggest one specific improvement.",
                  expected_output="Critique + suggestion",
                  agent=critic,
                  context=[t_write])

crew = Crew(agents=[researcher, writer, critic],
            tasks=[t_research, t_write, t_critique],
            process=Process.sequential,
            verbose=False)

# result = crew.kickoff()      # uncomment to actually run; takes ~30-60s on CPU Ollama
# print(result)


# %% [markdown] color=mint title="5 · AutoGen — same trio as a conversation"
# # 5 · AutoGen — same trio as a conversation
#


# %% color=peach title="user.initiate_chat(manager"
# @explain: user.initiate_chat(manager, message="Topic: The Transformer attention mechanism.")  # uncomment to run
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager

llm_config = {
    "config_list": [{
        "model": "qwen2.5:0.5b-instruct",
        "base_url": "http://localhost:11434/v1",
        "api_key": "ollama",
        "price": [0, 0],     # silence cost warnings
    }],
    "temperature": 0.2,
}

researcher = AssistantAgent(name="Researcher",
    system_message="Find 3 facts about the topic. Reply ONLY with a numbered list.",
    llm_config=llm_config)

writer = AssistantAgent(name="Writer",
    system_message="Take the researcher's bullets and write a 5-sentence summary. No fluff.",
    llm_config=llm_config)

critic = AssistantAgent(name="Critic",
    system_message="Critique the draft in 2 sentences and end with 'TERMINATE'.",
    llm_config=llm_config)

user = UserProxyAgent(name="User", human_input_mode="NEVER",
    is_termination_msg=lambda m: "TERMINATE" in (m.get("content") or ""),
    code_execution_config=False, max_consecutive_auto_reply=1)

chat = GroupChat(agents=[user, researcher, writer, critic], messages=[], max_round=8)
manager = GroupChatManager(groupchat=chat, llm_config=llm_config)

# user.initiate_chat(manager, message="Topic: The Transformer attention mechanism.")  # uncomment to run


# %% [markdown] color=violet title="What's happening.** The `GroupChatManager` is…"
# # What's happening.** The `GroupChatManager` is…
#
# **What's happening.** The `GroupChatManager` is itself an LLM that picks **who speaks next** at each round. You give it a roster and a stop condition; it routes. Compared to crewAI's pre-defined task list, AutoGen lets agents **decide** to call each other — more flexible, more failure modes.


# %% [markdown] color=amber title="6 · Tool use — agents calling Python"
# # 6 · Tool use — agents calling Python
#
# Both frameworks let you expose Python functions to agents. The agent sees the function's signature in its prompt and decides when to call it.


# %% color=rose title="crewAI tool"
# @explain: crewAI tool — using the @tool decorator
# crewAI tool — using the @tool decorator
from crewai_tools import tool

@tool("calculator")
def calculator(expr: str) -> str:
    """Evaluates a Python arithmetic expression like '2*3 + 4'."""
    return str(eval(expr, {"__builtins__": {}}, {}))

mathy = Agent(role="Math Helper", goal="Use the calculator for any arithmetic.",
              backstory="You always show your work.",
              tools=[calculator], llm=local_llm, verbose=True)
print("tool wired:", calculator.name)


# %% color=lime title="AutoGen"
# @explain: AutoGen — register a function on the assistant
# AutoGen — register a function on the assistant
from autogen import register_function

def calc(expr: str) -> str:
    """Eval an arithmetic expression."""
    return str(eval(expr, {"__builtins__":{}}, {}))

mathy_ag = AssistantAgent(name="Mathy", llm_config=llm_config,
    system_message="Use the calc tool for arithmetic.")

register_function(calc, caller=mathy_ag, executor=user,
                  name="calc", description="Evaluate arithmetic")
print("registered:", "calc")


# %% [markdown] color=teal title="7 · Pattern: sequential pipeline (Researcher → Writer → Critic)"
# # 7 · Pattern: sequential pipeline (Researcher → Writer → Critic)
#
# Best for tasks with a **clear ordering**. Already shown above. Cost: 3+ LLM calls per turn. Reliability: high. The output of step `i` is in the **context** of step `i+1`.


# %% [markdown] color=sky title="8 · Pattern: hierarchical (Manager + Workers)"
# # 8 · Pattern: hierarchical (Manager + Workers)
#
# ```
#               ┌── Manager LLM ──┐
#               │                 │
#    "fetch X"  ▼                 ▼ "summarise Y"
#         Worker 1            Worker 2
# ```
# …


# %% [markdown] color=mint title="9 · Common failure modes"
# # 9 · Common failure modes
#
# | Symptom | Cause | Fix |
# |---|---|---|
# | Agents loop forever, repeating themselves | No clear stop condition | `max_round` (AutoGen), `max_iter` (crewAI), `is_termination_msg` |
# | Cost explodes | Big context replayed to every agent | Use **summarising memory** between agents; trim per-call context |
# | Agents disagree on the goal | System prompts overlap or conflict | One sentence in each: **what the agent must produce, what they must NOT do** |
# | Hallucinated tool calls | Tiny model, weak instruction-follow | Use ≥ 7-8B for tool-use, or LangGraph for explicit branching (M33) |
# …


# %% [markdown] color=peach title="10 · Decision table — crewAI vs AutoGen vs LangGraph"
# # 10 · Decision table — crewAI vs AutoGen vs LangGraph
#
# | Need | Pick |
# |---|---|
# | Quick prototype with named roles | **crewAI** |
# | Tool-using agents, code execution sandbox | **AutoGen** |
# | Explicit state machine, retries, time-travel | **LangGraph** (M33) |
# | Single agent + tools | **LangChain** (M32) — don't multi-agent prematurely |
# …


# %% [markdown] color=violet title="✅ Recap"
# # ✅ Recap
#
# - Multi-agent = several specialised LLMs that **talk to each other** through tasks or conversation.
# - **crewAI** is declarative (roles + tasks). **AutoGen** is programmatic (conversation graph + manager).
# - Both frameworks point at any OpenAI-compatible endpoint — Ollama for free, GPT-4o for quality.
# - Watch for loops, runaway cost, and goal disagreement.
# - For audit-grade workflows, drop down to **LangGraph** (M33).
#
# Next: **M44 — vLLM** (high-throughput LLM inference for production).


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


