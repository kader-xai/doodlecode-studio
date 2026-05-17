# doodlecode format-version: 2
# Auto-converted from module_32_langchain_essentials.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 32 Langchain Essentials"
# # Module 32 Langchain Essentials
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 32 — LangChain Essentials"
# # Module 32 — LangChain Essentials
#
# > M30 built RAG by hand. M31 built prompts by hand. **LangChain** is the framework that wraps all of this — prompts, models, retrievers, tools, memory, agents — into composable building blocks. It's the most-used LLM framework in production.
#
# This module assumes you've finished **M25 (fine-tuning)**, **M30 (RAG)**, and **M31 (prompts + eval)**. We use a **local Hugging Face model** so everything runs in Colab without API keys; the same code works with OpenAI / Anthropic / Cohere by swapping one import.
#
# ### What you'll cover
# 1. The LangChain mental model — six core abstractions
# …


# %% [markdown] color=mint title="1 · The LangChain Mental Model — Six Abstractions"
# # 1 · The LangChain Mental Model — Six Abstractions
#
# | Building block | What it is | Why you'd use it |
# |---|---|---|
# | **Models** | `LLM` (text) or `ChatModel` (messages) | swap providers without rewriting code |
# | **Prompts** | `PromptTemplate`, `ChatPromptTemplate` | string formatting + variable validation |
# | **Output parsers** | `StrOutputParser`, `PydanticOutputParser` | turn raw text into typed objects |
# | **Retrievers** | wrap any vector DB (Chroma, FAISS, Pinecone…) | uniform `.invoke(query)` API |
# …


# %% color=peach title="!pip -q install langchain langchain-community…"
# @explain: Run this cell to see the output.
!pip -q install langchain langchain-community langchain-huggingface langchain-chroma transformers sentence-transformers
import warnings; warnings.filterwarnings("ignore")


# %% [markdown] color=violet title="2 · Setup — Local Model First, OpenAI as Alternative"
# # 2 · Setup — Local Model First, OpenAI as Alternative
#
# We use `HuggingFacePipeline` so there's nothing to pay for and nothing to configure. Same `chain.invoke(...)` works regardless of which model is plugged in.


# %% color=amber title="Smoke test"
# @explain: Smoke test
from langchain_huggingface import HuggingFacePipeline
from transformers import pipeline

llm_pipe = pipeline("text2text-generation",
                     model="google/flan-t5-base",
                     max_new_tokens=200, do_sample=False)
llm = HuggingFacePipeline(pipeline=llm_pipe)

# Smoke test
print(llm.invoke("What is the capital of France?"))


# %% [markdown] color=rose title="OpenAI alternative"
# # OpenAI alternative
#
# **OpenAI alternative (concept):**
#
# ```python
# from langchain_openai import ChatOpenAI
# llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
# ```
#
# Every chain we build below works **unchanged** with that swap. That portability is why teams use LangChain.


# %% [markdown] color=lime title="3 · Prompts — `PromptTemplate` and `ChatPromptTemplate`"
# # 3 · Prompts — `PromptTemplate` and `ChatPromptTemplate`
#
# Hand-written f-strings get unwieldy fast. `PromptTemplate` adds **variable validation** + **partial filling** + **automatic Pydantic coercion**.


# %% color=teal title="from langchain_core.prompts import PromptTemplate"
# @explain: Run this cell to see the output.
from langchain_core.prompts import PromptTemplate

tmpl = PromptTemplate.from_template(
    "Translate the following English to {language}:\n\n{text}\n\nTranslation:"
)

print(tmpl.format(language="French", text="Good morning, how are you?"))


# %% color=sky title="Same idea but for chat"
# @explain: Same idea but for chat (system + user roles)
# Same idea but for chat (system + user roles)
from langchain_core.prompts import ChatPromptTemplate

chat_tmpl = ChatPromptTemplate.from_messages([
    ("system", "You are a concise data-science tutor."),
    ("user",   "Explain {topic} in two sentences."),
])

print(chat_tmpl.format_messages(topic="cross-validation"))


# %% [markdown] color=mint title="4 · LCEL — Compose Anything with `|`"
# # 4 · LCEL — Compose Anything with `|`
#
# LCEL (LangChain Expression Language) is the modern way to build chains. Every component implements `.invoke()`, `.batch()`, `.stream()`, and `.ainvoke()`. You glue them with `|`:


# %% color=peach title=".invoke"
# @explain: .invoke — single call
# @explain: .batch — many in parallel
from langchain_core.output_parsers import StrOutputParser

prompt = PromptTemplate.from_template("Translate to {language}: {text}")
chain  = prompt | llm | StrOutputParser()

# .invoke — single call
print(chain.invoke({"language": "French", "text": "Good morning"}))

# .batch — many in parallel
inputs = [
    {"language": "Spanish", "text": "Good morning"},
    {"language": "Tamil",   "text": "Good morning"},
    {"language": "Arabic",  "text": "Good morning"},
]
print(chain.batch(inputs))


# %% [markdown] color=violet title="Why this matters"
# # Why this matters
#
# **Why this matters:**
# - The same chain object handles single calls, batches, async, and streaming.
# - Adding a step (e.g. logging, caching, validation) is one more `|` away.
# - Swap the LLM for OpenAI / Anthropic — the pipe doesn't change.


# %% [markdown] color=amber title="5 · Output Parsers — Get Typed Results Back"
# # 5 · Output Parsers — Get Typed Results Back
#
# Free-form strings are hard to use programmatically. Output parsers convert the raw model text into the shape your code expects.


# %% color=rose title="from langchain_core.output_parsers import…"
# @explain: Run this cell to see the output.
from langchain_core.output_parsers import CommaSeparatedListOutputParser

parser = CommaSeparatedListOutputParser()

prompt = PromptTemplate.from_template(
    "List 5 {category}, comma-separated, no numbering:\n{format_instructions}"
).partial(format_instructions=parser.get_format_instructions())

chain = prompt | llm | parser
print(chain.invoke({"category": "European capital cities"}))


# %% [markdown] color=lime title="Pydantic parser — for full structured output"
# # Pydantic parser — for full structured output
#


# %% color=teal title="from langchain_core.output_parsers import…"
# @explain: Run this cell to see the output.
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List

class BookSummary(BaseModel):
    title: str
    author: str
    year: int = Field(description="Year published")
    themes: List[str] = Field(description="Three main themes")

parser = PydanticOutputParser(pydantic_object=BookSummary)

prompt = PromptTemplate.from_template(
    "Extract a structured summary.\n{format_instructions}\n\nBook description: {desc}"
).partial(format_instructions=parser.get_format_instructions())

chain = prompt | llm | parser

desc = "1984 is George Orwell's 1949 novel about totalitarianism, surveillance, and the malleability of truth."
try:
    out = chain.invoke({"desc": desc})
    print(type(out).__name__, "→", out)
except Exception as e:
    print("Small models often fumble strict JSON; production uses GPT-4o + structured outputs.")
    print("error:", e)


# %% [markdown] color=sky title="6 · RAG with LangChain — 50 Lines of M30, Now 5"
# # 6 · RAG with LangChain — 50 Lines of M30, Now 5
#
# Compare against `module_30_rag_and_vector_search.ipynb`. The full pipeline becomes a one-liner chain.


# %% color=mint title="1"
# @explain: 1
# @explain: 2
# @explain: 3
# @explain: 4
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

# 1. Embeddings (same MiniLM as M30)
embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# 2. Tiny corpus
docs = [
    Document(page_content="NumPy was created by Travis Oliphant in 2006."),
    Document(page_content="PyTorch was released by Facebook AI Research in 2016."),
    Document(page_content="DeepSeek-V3 is a 671B-parameter MoE model with Multi-Latent Attention."),
    Document(page_content="The Transformer paper 'Attention Is All You Need' came out in 2017."),
]

# 3. Vector store (in-memory)
vectorstore = Chroma.from_documents(docs, embedding=embedder)
retriever   = vectorstore.as_retriever(search_kwargs={"k": 2})

# 4. RAG chain — retrieve + stuff into prompt + generate
from langchain_core.runnables import RunnablePassthrough

rag_prompt = PromptTemplate.from_template(
    "Use the context to answer. If the answer isn't there, say 'I don't know'.\n\n"
    "Context:\n{context}\n\nQuestion: {question}\nAnswer:"
)

def format_docs(docs):
    return "\n\n".join(d.page_content for d in docs)

rag = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | rag_prompt
    | llm
    | StrOutputParser()
)

print(rag.invoke("Who created NumPy?"))
print(rag.invoke("What's special about DeepSeek-V3?"))


# %% [markdown] color=peach title="Reading the chain:** the dict at the top runs the…"
# # Reading the chain:** the dict at the top runs the…
#
# **Reading the chain:** the dict at the top runs the retriever AND passes the original question through, in parallel. That dict becomes the prompt's input variables. Pipe through prompt → LLM → string. Five lines, fully type-safe, fully streamable.


# %% [markdown] color=violet title="7 · Memory — Conversational Chains"
# # 7 · Memory — Conversational Chains
#


# %% color=amber title="In-memory store: one history per session_id"
# @explain: In-memory store: one history per session_id
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a friendly tutor. Keep replies under 30 words."),
    ("placeholder", "{history}"),
    ("user", "{input}"),
])

base_chain = prompt | llm | StrOutputParser()

# In-memory store: one history per session_id
store = {}
def get_history(session_id):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

chat = RunnableWithMessageHistory(
    base_chain, get_history,
    input_messages_key="input",
    history_messages_key="history",
)

cfg = {"configurable": {"session_id": "alice"}}
print(chat.invoke({"input": "My name is Alice."}, config=cfg))
print(chat.invoke({"input": "What's my name?"},   config=cfg))


# %% [markdown] color=rose title="The chain now **remembers** prior turns of…"
# # The chain now **remembers** prior turns of…
#
# The chain now **remembers** prior turns of conversation, scoped by `session_id`. Swap `InMemoryChatMessageHistory` for Redis, Postgres, or DynamoDB to persist across restarts (M37 covers Redis).


# %% [markdown] color=lime title="8 · Tools & Agents — A ReAct Agent that Uses a Calculator"
# # 8 · Tools & Agents — A ReAct Agent that Uses a Calculator
#
# LangChain agents wrap the ReAct loop from M31 — Thought → Action → Observation → Final Answer — automatically.


# %% color=teal title="Standard ReAct prompt from LangChain hub"
# @explain: Standard ReAct prompt from LangChain hub
# @explain: ⚠️ flan-t5 is small and frequently fumbles the ReAct format
# @explain: In production this is where you swap to GPT-4o or Claude
from langchain_core.tools import tool
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub

@tool
def calculator(expression: str) -> str:
    """Evaluate a Python arithmetic expression. Example: calculator('17 * 24')."""
    try:
        return str(eval(expression, {"__builtins__": {}}))
    except Exception as e:
        return f"error: {e}"

# Standard ReAct prompt from LangChain hub
react_prompt = hub.pull("hwchase17/react")

agent = create_react_agent(llm, [calculator], react_prompt)
executor = AgentExecutor(agent=agent, tools=[calculator],
                         verbose=True, handle_parsing_errors=True,
                         max_iterations=4)

# ⚠️ flan-t5 is small and frequently fumbles the ReAct format.
# In production this is where you swap to GPT-4o or Claude.
try:
    print(executor.invoke({"input": "What is 17 * 24 plus 100?"}))
except Exception as e:
    print("ReAct format error (small models often fail this):", e)


# %% [markdown] color=sky title="Production note:** ReAct agents need a strong…"
# # Production note:** ReAct agents need a strong…
#
# **Production note:** ReAct agents need a strong instruction-following model. With local 1B-class models you'll see frequent format failures. With GPT-4o-mini / Claude-3.5-Haiku / Llama-3-70B-Instruct it's solid. The `handle_parsing_errors=True` flag is your friend.


# %% [markdown] color=mint title="9 · Tracing & Debugging"
# # 9 · Tracing & Debugging
#
# Two flags + one external tool cover almost all debugging needs.


# %% color=peach title="Built-in: pass verbose=True or set debug"
# @explain: Built-in: pass verbose=True or set debug
# Built-in: pass verbose=True or set debug
import langchain
langchain.debug = True   # prints every step's input/output

prompt = PromptTemplate.from_template("Translate '{text}' to French.")
chain = prompt | llm | StrOutputParser()
chain.invoke({"text": "good morning"})

langchain.debug = False


# %% [markdown] color=violet title="LangSmith — production observability"
# # LangSmith — production observability
#
# LangSmith (paid SaaS, generous free tier) is LangChain's tracing platform. Two env vars and every chain invocation is logged with full input/output, timing, and token counts.
#
# ```bash
# export LANGCHAIN_TRACING_V2=true
# export LANGCHAIN_API_KEY=ls__...
# ```
# …


# %% [markdown] color=amber title="10 · Practice — Try Yourself"
# # 10 · Practice — Try Yourself
#
# 1. **Swap the LLM** — replace `HuggingFacePipeline` with `ChatOpenAI(model="gpt-4o-mini")` (needs API key). Re-run the RAG chain. How much better are the answers?
# 2. **Add a step** — extend the RAG chain to ALSO return the source `page_content` it used. Hint: `{"answer": rag, "context": retriever}`.
# 3. **New tool** — add a `wikipedia_search(query)` tool to the agent. Test on "Who wrote Hamlet?"
# 4. **Conversational RAG** — combine §6 (RAG) and §7 (memory). The agent should remember prior questions and use them as context for follow-up retrievals.


# %% color=rose title="Sketch for #2"
# @explain: Sketch for #2 — return answer + sources
# Sketch for #2 — return answer + sources
from langchain_core.runnables import RunnableParallel

retrieve_and_answer = RunnableParallel(
    answer=rag,
    sources=retriever,
)

result = retrieve_and_answer.invoke("Who created NumPy?")
print("answer :", result["answer"])
print("sources:", [d.page_content for d in result["sources"]])


# %% [markdown] color=lime title="11 · Where This Scales"
# # 11 · Where This Scales
#
# | Need | Tool |
# |---|---|
# | Stateful agent graphs (loops, branches) | **LangGraph** (M33) |
# | RAG-first framework with better doc parsing | **LlamaIndex** (M34) |
# | Programmatic prompt optimisation | **DSPy** (M35) |
# | Multi-agent orchestration | **crewAI** / **AutoGen** (M43) |
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


