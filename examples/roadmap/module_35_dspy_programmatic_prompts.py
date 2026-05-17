# doodlecode format-version: 2
# Auto-converted from module_35_dspy_programmatic_prompts.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 35 Dspy Programmatic Prompts"
# # Module 35 Dspy Programmatic Prompts
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 35 — DSPy: Programmatic Prompts"
# # Module 35 — DSPy: Programmatic Prompts
#
# > M31 hand-tuned prompt strings. M32-M34 wrapped them in templates. **DSPy flips the model**: declare **what** the LLM should do (input → output) and let the framework auto-tune the prompt. From Stanford NLP, used in production at companies like JetBlue, ServiceNow, and Anthropic-using startups.
#
# This module assumes you've finished **M31 (prompt engineering)**, **M32 (LangChain)**.
#
# ### What you'll cover
# 1. The DSPy mental model — prompts as **code**, not strings
# …


# %% [markdown] color=mint title="1 · The DSPy Mental Model"
# # 1 · The DSPy Mental Model
#
# | Traditional prompts | DSPy |
# |---|---|
# | `"You are a concise tutor. Answer this Q: {q}"` | `class QA(Signature): question:str → answer:str` |
# | Tweak strings by hand | Define a metric, run an **optimiser** that auto-tunes |
# | Re-do all your prompts when you switch models | Same program runs on any LM, optimiser re-tunes |
# | Hard to compose multi-step pipelines | Modules compose like PyTorch layers |
# …


# %% [markdown] color=peach title="2 · Setup"
# # 2 · Setup
#
# DSPy supports OpenAI / Anthropic / Cohere out of the box via `litellm`. For free local use we wrap a HuggingFace pipeline. The same DSPy code runs against any backend.


# %% color=violet title="!pip -q install dspy-ai transformers"
# @explain: Run this cell to see the output.
!pip -q install dspy-ai transformers
import warnings; warnings.filterwarnings("ignore")


# %% color=amber title="A custom LM adapter: minimal interface DSPy needs"
# @explain: A custom LM adapter: minimal interface DSPy needs (callable that returns a list of strings)
# @explain: Mimic LiteLLM-style return so DSPy is happy
import dspy
from transformers import pipeline as hf_pipeline

# A custom LM adapter: minimal interface DSPy needs (callable that returns a list of strings)
class FlanT5LM(dspy.LM):
    def __init__(self, model="google/flan-t5-base"):
        super().__init__(model=model)
        self.pipe = hf_pipeline("text2text-generation", model=model,
                                  max_new_tokens=200, do_sample=False)

    def __call__(self, prompt=None, messages=None, **kw):
        if messages and not prompt:
            prompt = "\n".join(m.get("content","") for m in messages)
        out = self.pipe(prompt)[0]["generated_text"]
        # Mimic LiteLLM-style return so DSPy is happy
        self.history.append({"prompt": prompt, "response": out})
        return [out]

dspy.settings.configure(lm=FlanT5LM())
print("DSPy configured with flan-t5-base")


# %% [markdown] color=rose title="OpenAI alternative"
# # OpenAI alternative
#
# **OpenAI alternative (concept):**
#
# ```python
# dspy.settings.configure(lm=dspy.LM('openai/gpt-4o-mini', api_key=...))
# ```
# Every program below works **unchanged**. That portability is DSPy's superpower — switch models, the optimiser re-tunes the prompts automatically.


# %% [markdown] color=lime title="3 · Signatures — Declarative I/O Specs"
# # 3 · Signatures — Declarative I/O Specs
#
# A **Signature** is the DSPy equivalent of a function signature: input fields, output fields, and a docstring describing the task. It's NOT a prompt — it's a *contract*. DSPy generates the actual prompt later.


# %% color=teal title="That's it"
# @explain: That's it
class QA(dspy.Signature):
    """Answer questions concisely with a single fact."""
    question = dspy.InputField()
    answer   = dspy.OutputField(desc="a short factual answer")

# That's it. No prompt string. DSPy will write one for us.
print("Signature defined:", QA)


# %% [markdown] color=sky title="For more complex schemas, fields can carry types…"
# # For more complex schemas, fields can carry types…
#
# For more complex schemas, fields can carry types and descriptions — exactly like Pydantic models.


# %% color=mint title="from typing import List"
# @explain: Run this cell to see the output.
from typing import List

class TriageTicket(dspy.Signature):
    """Classify a customer-support ticket and propose next actions."""
    text:     str       = dspy.InputField()
    category: str       = dspy.OutputField(desc="One of: bug, billing, feature, other")
    priority: str       = dspy.OutputField(desc="One of: low, medium, high")
    actions:  List[str] = dspy.OutputField(desc="2-3 concrete next steps")


# %% [markdown] color=peach title="4 · Modules — `Predict`, `ChainOfThought`, `ReAct`"
# # 4 · Modules — `Predict`, `ChainOfThought`, `ReAct`
#
# A **Module** is the simplest reusable LLM call. DSPy ships several built-ins. Each takes a Signature and turns it into a callable.


# %% color=violet title="Predict"
# @explain: Predict — the basic module: input → output, one LLM call
# Predict — the basic module: input → output, one LLM call
qa = dspy.Predict(QA)

result = qa(question="What year was Python released?")
print("answer:", result.answer)


# %% color=amber title="ChainOfThought"
# @explain: ChainOfThought — the same I/O, but the model emits 'reasoning' first
# ChainOfThought — the same I/O, but the model emits 'reasoning' first
cot_qa = dspy.ChainOfThought(QA)

result = cot_qa(question="If a bat and ball cost $1.10 and the bat is $1 more than the ball, how much is the ball?")
print("reasoning:", result.reasoning)
print("answer:", result.answer)


# %% [markdown] color=rose title="Reading this:** by switching `Predict` →…"
# # Reading this:** by switching `Predict` →…
#
# **Reading this:** by switching `Predict` → `ChainOfThought`, the *same* signature now produces a `reasoning` field for free. No prompt rewriting. That's DSPy.


# %% [markdown] color=lime title="5 · Compose Modules into Programs"
# # 5 · Compose Modules into Programs
#
# A DSPy **program** is a `Module` subclass that strings together calls — exactly like a `nn.Module` in PyTorch.


# %% color=teal title="Use it like a function"
# @explain: Use it like a function
class MultiStepQA(dspy.Module):
    """Decompose a question, answer each sub-question, then synthesise."""
    def __init__(self):
        super().__init__()
        self.decompose = dspy.Predict("question -> sub_questions: list[str]")
        self.answer    = dspy.ChainOfThought("question -> answer")
        self.synth     = dspy.Predict("question, partial_answers -> final_answer")

    def forward(self, question):
        subs = self.decompose(question=question).sub_questions
        partials = [self.answer(question=s).answer for s in subs]
        return self.synth(question=question, partial_answers=str(partials))

# Use it like a function
prog = MultiStepQA()
result = prog(question="Who created NumPy and what year?")
print(result.final_answer)


# %% [markdown] color=sky title="Note on small models:** flan-t5-base is too small…"
# # Note on small models:** flan-t5-base is too small…
#
# **Note on small models:** flan-t5-base is too small to reliably emit clean Python lists. With GPT-4o-mini or Claude this composition just works. The structure of the code is identical regardless of model — that's the point.


# %% [markdown] color=mint title="6 · Optimisers — Auto-Tune Prompts from Examples"
# # 6 · Optimisers — Auto-Tune Prompts from Examples
#
# Hand-tuning prompts is what M31 was about. DSPy treats this as **compilation**: feed in example data + a metric, and the optimiser searches for the best prompt (often by inserting auto-selected few-shot examples).
#
# | Optimiser | Strategy |
# |---|---|
# | **BootstrapFewShot** | model labels examples → use as few-shot demos in the prompt |
# | **MIPROv2** | searches both instructions AND demos with Bayesian optimisation |
# …


# %% color=peach title="Tiny training set"
# @explain: Tiny training set
# @explain: Metric: case-insensitive substring match (relaxed)
# @explain: Baseline (no compilation)
# Tiny training set
train_set = [
    dspy.Example(question="Who created NumPy?",          answer="Travis Oliphant").with_inputs("question"),
    dspy.Example(question="When was Python released?",    answer="1991").with_inputs("question"),
    dspy.Example(question="Who wrote 'Attention Is All You Need'?", answer="Vaswani et al.").with_inputs("question"),
    dspy.Example(question="What was Ada Lovelace known for?", answer="The first computer program").with_inputs("question"),
]

# Metric: case-insensitive substring match (relaxed)
def match(gold, pred, trace=None):
    return gold.answer.lower() in pred.answer.lower()

# Baseline (no compilation)
baseline = dspy.Predict(QA)
print("--- BEFORE compilation ---")
for ex in train_set:
    p = baseline(question=ex.question)
    print(f"  {ex.question}  →  {p.answer}   ({'✓' if match(ex, p) else '✗'})")


# %% color=violet title="from dspy.teleprompt import BootstrapFewShot"
# @explain: Run this cell to see the output.
from dspy.teleprompt import BootstrapFewShot

optimizer = BootstrapFewShot(metric=match, max_bootstrapped_demos=2)
compiled  = optimizer.compile(student=dspy.Predict(QA), trainset=train_set)

print("\n--- AFTER compilation ---")
for ex in train_set:
    p = compiled(question=ex.question)
    print(f"  {ex.question}  →  {p.answer}   ({'✓' if match(ex, p) else '✗'})")


# %% [markdown] color=amber title="What just happened"
# # What just happened
#
# **What just happened:**
#
# 1. The optimiser ran the baseline against each training example.
# 2. It collected the cases where the model **already** got the answer right (or close enough).
# 3. It now uses those successful cases as **few-shot examples in the prompt** — automatically chosen, automatically formatted.
#
# The compiled program is just a `Predict` with attached demonstrations. Saving it serialises the demos + the underlying signature.


# %% [markdown] color=rose title="7 · Save and Load a Compiled Program"
# # 7 · Save and Load a Compiled Program
#


# %% color=lime title="Reload (e.g"
# @explain: Reload (e.g
import json, tempfile, os

path = os.path.join(tempfile.mkdtemp(), "qa_compiled.json")
compiled.save(path)
print("saved to:", path)

# Reload (e.g. in a fresh server)
fresh = dspy.Predict(QA)
fresh.load(path)
print("\nreloaded test:", fresh(question="Who created NumPy?").answer)


# %% [markdown] color=teal title="8 · DSPy + RAG — A Full RAG Program"
# # 8 · DSPy + RAG — A Full RAG Program
#
# DSPy plays nicely with retrievers. Here's a RAG program with retrieve → generate, all auto-tunable.


# %% color=sky title="Toy in-memory retriever"
# @explain: Toy in-memory retriever
# Toy in-memory retriever
DOCS = [
    "NumPy was created by Travis Oliphant in 2006.",
    "PyTorch was released by Facebook AI Research in 2016.",
    "DeepSeek-V3 is a 671B Mixture-of-Experts model with Multi-Latent Attention.",
    "Python was released by Guido van Rossum in 1991.",
]

def retrieve(query, k=2):
    """Trivial keyword retriever for demo purposes."""
    scored = [(sum(w in d.lower() for w in query.lower().split()), d) for d in DOCS]
    return [d for _, d in sorted(scored, reverse=True)[:k]]

class RAG(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate = dspy.ChainOfThought("context, question -> answer")
    def forward(self, question):
        ctx = "\n\n".join(retrieve(question, k=2))
        return self.generate(context=ctx, question=question)

rag = RAG()
print(rag(question="When was NumPy made?").answer)
print(rag(question="What's special about DeepSeek?").answer)


# %% [markdown] color=mint title="Why this matters:** the retriever is just Python"
# # Why this matters:** the retriever is just Python
#
# **Why this matters:** the retriever is just Python. The DSPy program optimises *how the retrieved context is presented* to the LLM. Plug in a real retriever (Chroma, LlamaIndex, Pinecone) — code unchanged.


# %% [markdown] color=peach title="9 · Where This Scales"
# # 9 · Where This Scales
#
# | Need | Tool |
# |---|---|
# | State-of-the-art prompt optimisation | **MIPROv2** (Bayesian) |
# | Distilling a teacher model into a smaller student | **BootstrapFinetune** |
# | Multi-stage pipelines | DSPy modules compose like PyTorch — works at any depth |
# | Production observability | **MLflow + DSPy** integration / **Phoenix** |
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


