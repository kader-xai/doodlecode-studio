# doodlecode format-version: 2
# Auto-converted from module_31_prompt_engineering_and_llm_eval.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 31 Prompt Engineering And Llm Eval"
# # Module 31 Prompt Engineering And Llm Eval
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 31 — Prompt Engineering & LLM Evaluation"
# # Module 31 — Prompt Engineering & LLM Evaluation
#
# > **The finale.** You've built models from Module 14 onward — regression, neural networks, transformers, fine-tuning, RAG. This module covers the part that determines whether any of it actually *works for users*: **how you ask** and **how you measure**.
#
# ### What you'll cover
# 1. Why prompt engineering still matters in 2026
# 2. **Zero-shot, few-shot, role prompting** — the foundations
# 3. **Chain-of-thought (CoT)** — make the model think out loud
# …


# %% [markdown] color=mint title="1 · Why Prompt Engineering Still Matters"
# # 1 · Why Prompt Engineering Still Matters
#
# > "Prompts are dead — just use the model."  Wrong. Even GPT-5 / Claude 4 / DeepSeek-V3 perform **dramatically better** with good prompts. The same model + bad prompt vs same model + good prompt routinely shows 20-40% accuracy differences on benchmarks.
#
# ### Three principles
# 1. **Be specific.** Tell the model exactly what you want. Output format. Length. Tone. Constraints.
# 2. **Show, don't just tell.** A few examples beat a paragraph of instructions.
# 3. **Give it room to think.** "Let's work through this step by step" really does help.
# …


# %% color=peach title="!pip -q install transformers pydantic"
# @explain: Run this cell to see the output.
!pip -q install transformers pydantic
from transformers import pipeline
import warnings; warnings.filterwarnings("ignore")

llm = pipeline("text2text-generation", model="google/flan-t5-base")

def ask(prompt, max_new=120, temperature=0.0):
    out = llm(prompt, max_new_tokens=max_new,
              do_sample=temperature > 0,
              temperature=max(temperature, 1e-5))[0]["generated_text"]
    return out

print(ask("What is 17 * 24?"))


# %% [markdown] color=violet title="2 · Zero-Shot, Few-Shot, Role Prompting — the Foundations"
# # 2 · Zero-Shot, Few-Shot, Role Prompting — the Foundations
#


# %% [markdown] color=amber title="Zero-shot — just describe the task"
# # Zero-shot — just describe the task
#
# Quick, but quality varies wildly with how clearly you describe it.


# %% color=rose title="ZERO = 'Classify the sentiment of this review as…"
# @explain: Run this cell to see the output.
ZERO = "Classify the sentiment of this review as positive, negative, or neutral.\n\nReview: The food was cold and the service was slow.\nSentiment:"
print(ask(ZERO))


# %% [markdown] color=lime title="Few-shot — show 2-5 examples first"
# # Few-shot — show 2-5 examples first
#
# The single highest-leverage upgrade. Shows the model the **exact format** you want and the **kind of inputs** it'll see.


# %% color=teal title="FEW = '''Classify the sentiment of each review as…"
# @explain: Run this cell to see the output.
FEW = """Classify the sentiment of each review as positive, negative, or neutral.

Review: Best burger I've had in years.
Sentiment: positive

Review: The waiter was rude and the table sticky.
Sentiment: negative

Review: It's a restaurant. The food existed.
Sentiment: neutral

Review: The food was cold and the service was slow.
Sentiment:"""

print(ask(FEW))


# %% [markdown] color=sky title="Role prompting — set a persona / expertise frame"
# # Role prompting — set a persona / expertise frame
#
# Less essential than few-shot, but useful for tone, style, or specialised knowledge.


# %% color=mint title="ROLE = '''You are a senior data scientist…"
# @explain: Run this cell to see the output.
ROLE = """You are a senior data scientist explaining concepts to a junior engineer.
Use plain English, no jargon. One short paragraph.

Q: What is the difference between L1 and L2 regularisation?
A:"""
print(ask(ROLE))


# %% [markdown] color=peach title="3 · Chain-of-Thought (CoT) — Make the Model Think Out Loud"
# # 3 · Chain-of-Thought (CoT) — Make the Model Think Out Loud
#
# LLMs are trained to predict the next token. When you ask for an answer directly, they often blurt one out before "thinking." CoT — explicitly asking the model to **show its reasoning** — produces dramatically better results on math, logic, and multi-step problems.


# %% color=violet title="Q = '''A bat and a ball cost $1.10 in total"
# @explain: Run this cell to see the output.
Q = """A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the ball.
How much does the ball cost?"""

print("--- DIRECT ---")
print(ask(Q + "\nAnswer in cents only:"))

print("\n--- CHAIN-OF-THOUGHT ---")
print(ask(Q + "\nLet's think step by step."))


# %% [markdown] color=amber title="Why this works:** the 'let's think step by step'…"
# # Why this works:** the "let's think step by step"…
#
# **Why this works:** the "let's think step by step" trigger lets the model spend tokens computing intermediate state instead of forcing the answer into the first prediction. The intermediate steps get attended to when generating the final answer.
#
# > Original paper: *"Large Language Models are Zero-Shot Reasoners"* (Kojima et al., 2022). The single most cited prompting trick of the LLM era.


# %% [markdown] color=rose title="4 · ReAct — Reason + Act with Tools"
# # 4 · ReAct — Reason + Act with Tools
#
# CoT lets the model think. **ReAct** lets it think AND call tools (search, calculator, code interpreter) interleaved with thought. The pattern:
#
# ```
# Thought: I need to compute 17 * 24.
# Action: calculator(17 * 24)
# Observation: 408
# …


# %% color=lime title="A tiny ReAct-style loop"
# @explain: A tiny ReAct-style loop — toy version using flan-t5
# @explain: Toy "tools" the model can call
# @explain: Hand-driven ReAct loop — in production an agent framework does this for you
# A tiny ReAct-style loop — toy version using flan-t5
import re

# Toy "tools" the model can call
def calculator(expr):
    try:
        return str(eval(expr, {"__builtins__": {}}))    # NEVER do this in production
    except Exception as e:
        return f"error: {e}"

def fake_search(query):
    db = {
        "python release year": "1991",
        "transformer paper authors": "Vaswani et al. (2017)",
        "deepseek v3 active experts": "8 of 256 per token",
    }
    return db.get(query.lower(), "no result")

TOOLS = {"calculator": calculator, "search": fake_search}

REACT_PROMPT = """Answer the question. You may use tools.
Available tools:
- calculator(expression)  — evaluate arithmetic
- search(query)           — look up a fact

Format: Use Thought/Action/Observation lines. End with "Final answer: ...".

Question: {q}
Thought:"""

# Hand-driven ReAct loop — in production an agent framework does this for you
question = "What year was Python released?"
trace = REACT_PROMPT.format(q=question)
trace += " I should look this up.\nAction: search(python release year)\n"
trace += f"Observation: {fake_search('python release year')}\n"
trace += "Thought: I have the answer.\nFinal answer:"
print(ask(trace, max_new=20))


# %% [markdown] color=teal title="Production ReAct:** loop until the model emits…"
# # Production ReAct:** loop until the model emits…
#
# **Production ReAct:** loop until the model emits `Final answer:`. Each step: parse the latest `Action: tool(args)` line, run the tool, append `Observation: ...`, send the updated trace back to the LLM. LangChain's `AgentExecutor` and OpenAI's `tools=[...]` API do this for you. Read sections 7-8 of the *ReAct* paper (Yao et al., 2022) — it's a short and important paper.


# %% [markdown] color=sky title="5 · Structured Outputs — JSON Mode + Pydantic"
# # 5 · Structured Outputs — JSON Mode + Pydantic
#
# Free-form text is unparseable. For real applications you want **structured output** the rest of your code can use.
#
# ### Strategy 1 — ask for JSON in the prompt + parse


# %% color=mint title="Real production code: try/except around json.loads…"
# @explain: Real production code: try/except around json.loads + retry
JSON_PROMPT = """Extract the contact details. Output ONLY valid JSON with keys: name, email, phone.

Text: My name is Ada Lovelace, email ada@example.com, phone +44-20-7946-0958.

JSON:"""

raw = ask(JSON_PROMPT)
print("raw output:", repr(raw))

# Real production code: try/except around json.loads + retry
import json
try:
    parsed = json.loads(raw)
    print("parsed:", parsed)
except json.JSONDecodeError as e:
    print("parse failed:", e)


# %% [markdown] color=peach title="Strategy 2 — Pydantic schemas (the modern way)"
# # Strategy 2 — Pydantic schemas (the modern way)
#
# For OpenAI / Anthropic / Cohere production code, use **constrained decoding**: the model is forced to emit valid JSON matching your schema. No retry loops, no parse failures.
#
# ```python
# # OpenAI structured outputs (concept — needs API key)
# from pydantic import BaseModel
# from openai import OpenAI
# …


# %% [markdown] color=violet title="6 · Self-Consistency + Temperature — for Harder Problems"
# # 6 · Self-Consistency + Temperature — for Harder Problems
#
# For multi-step reasoning, **sample several CoT chains** with `temperature > 0`, then take the **majority answer**. Often beats single-CoT by 5-10%.


# %% color=amber title="Pull the last number from the output as the answer"
# @explain: Pull the last number from the output as the answer
def self_consistent_answer(question, n=5, temperature=0.7):
    """Run CoT n times with sampling, take the most common final answer."""
    answers = []
    prompt = f"{question}\nLet's think step by step. Final numeric answer:"
    for _ in range(n):
        out = ask(prompt, max_new=80, temperature=temperature)
        # Pull the last number from the output as the answer
        nums = re.findall(r"-?\d+\.?\d*", out)
        if nums:
            answers.append(nums[-1])
    if not answers:
        return None
    from collections import Counter
    return Counter(answers).most_common(1)[0][0]

print(self_consistent_answer("Sarah has 3 boxes of 12 cookies. She eats 7. How many remain?", n=5))


# %% [markdown] color=rose title="7 · LLM-as-Judge — Automated Evaluation at Scale"
# # 7 · LLM-as-Judge — Automated Evaluation at Scale
#
# You can't manually grade thousands of outputs. **LLM-as-judge**: ask a (usually larger / smarter) LLM to score outputs against criteria. Standard for production eval pipelines.
#
# ### Pros and cons
# - ✅ Scales to thousands of evaluations cheaply.
# - ✅ Handles open-ended outputs (where exact-match doesn't work).
# - ⚠️ Has known biases — favours longer answers, position bias, self-preference. Mitigate with **pairwise comparison** + **shuffling order** + clear rubric.


# %% color=lime title="Score two candidates against a reference"
# @explain: Score two candidates against a reference
JUDGE_PROMPT = """You are an evaluator. Score the candidate answer on a scale 1-5
based on how well it matches the reference answer in factual content.

5 = same facts, possibly worded differently
3 = partially correct, some missing or extra info
1 = factually wrong or off-topic

Question: {q}
Reference answer: {ref}
Candidate answer: {cand}

Output ONLY the integer score (1-5) and one sentence reason.
Score:"""

def judge(q, ref, cand):
    return ask(JUDGE_PROMPT.format(q=q, ref=ref, cand=cand), max_new=60)

# Score two candidates against a reference
q   = "What year was Python released?"
ref = "Python was first released in 1991 by Guido van Rossum."
print("good cand:", judge(q, ref, "Python came out in 1991."))
print("bad  cand:", judge(q, ref, "Python was created in the late 2000s."))


# %% [markdown] color=teal title="8 · RAG Evaluation — Ragas-Style Metrics"
# # 8 · RAG Evaluation — Ragas-Style Metrics
#
# For RAG specifically (M30), four metrics from the **Ragas** framework cover most production needs:
#
# | Metric | Question it answers |
# |---|---|
# | **Faithfulness** | does the answer ONLY use facts from the retrieved context? |
# | **Answer relevance** | does the answer actually address the question? |
# …


# %% color=sky title="FAITH_PROMPT = '''Below is a question"
# @explain: Run this cell to see the output.
FAITH_PROMPT = """Below is a question, the context that was retrieved, and the answer that was given.
Decide if EVERY claim in the answer is supported by the context.
Reply YES or NO followed by a one-sentence reason.

Question: {q}
Context: {ctx}
Answer: {ans}

Faithful?:"""

def faithfulness(q, ctx, ans):
    return ask(FAITH_PROMPT.format(q=q, ctx=ctx, ans=ans), max_new=80)

q   = "Who created NumPy?"
ctx = "NumPy was created by Travis Oliphant in 2006."

print("--- faithful answer ---")
print(faithfulness(q, ctx, "Travis Oliphant created NumPy in 2006."))

print("\n--- unfaithful answer (added unsupported detail) ---")
print(faithfulness(q, ctx, "Travis Oliphant created NumPy in 2006 while working at Google."))


# %% [markdown] color=mint title="9 · End-to-End Eval Harness"
# # 9 · End-to-End Eval Harness
#
# A real eval harness compares **prompts**, not just **outputs**. Build it once, then test every prompt change against the same fixed dataset.


# %% color=peach title="eval_set = ["
# @explain: Run this cell to see the output.
eval_set = [
    {"q": "Capital of France?",                   "ref": "Paris"},
    {"q": "Who wrote Hamlet?",                    "ref": "William Shakespeare"},
    {"q": "Square root of 144?",                  "ref": "12"},
    {"q": "Boiling point of water in Celsius?",   "ref": "100"},
]

PROMPTS = {
    "zero-shot":          "{q}",
    "concise":            "{q}\nAnswer in one short sentence:",
    "with-instruction":   "Answer the following factual question using exactly one short word or number.\nQ: {q}\nA:",
}

def exact_match(pred, ref):
    return ref.lower() in pred.lower()

results = []
for name, template in PROMPTS.items():
    correct = sum(exact_match(ask(template.format(q=row["q"]), max_new=30), row["ref"])
                  for row in eval_set)
    results.append({"prompt": name, "accuracy": correct / len(eval_set)})

import pandas as pd
print(pd.DataFrame(results).round(3))


# %% [markdown] color=violet title="Read the table:** the accuracy column is your…"
# # Read the table:** the accuracy column is your…
#
# **Read the table:** the accuracy column is your A/B-tested prompt comparison. Now you can iterate on prompts the way you iterate on hyperparameters — measure, compare, ship.


# %% [markdown] color=amber title="10 · Where This Scales"
# # 10 · Where This Scales
#
# | Need | Tool |
# |---|---|
# | Side-by-side prompt comparison framework | **Promptfoo**, **DeepEval**, **TruLens** |
# | Production observability for LLM apps | **Langfuse**, **Helicone**, **LangSmith**, **Arize Phoenix** |
# | RAG evaluation suite | **Ragas**, **DeepEval**, **TruLens** |
# | Constrained / structured generation | **Outlines**, **Guidance**, **LMQL**, OpenAI structured outputs |
# …


# %% [markdown] color=rose title="11 · Practice — Try Yourself"
# # 11 · Practice — Try Yourself
#
# 1. **Few-shot upgrade** — take the zero-shot sentiment classifier from §2 and add 5 few-shot examples covering edge cases (sarcasm, mixed sentiment, neutral). Re-run on 10 hard reviews you write yourself. Did accuracy improve?
#
# 2. **CoT on math** — write 5 multi-step word problems. Compare direct answer vs CoT. Compute accuracy for each.
#
# 3. **Pydantic extraction** — define a `BlogPost(title: str, author: str, year: int, tags: List[str])` schema. Prompt the model to extract these from a sample paragraph. Validate the JSON output against the schema.
#
# …


# %% color=lime title="Solution sketch for #3"
# @explain: Solution sketch for #3 — Pydantic extraction
# Solution sketch for #3 — Pydantic extraction
from pydantic import BaseModel, ValidationError
from typing import List
import json

class BlogPost(BaseModel):
    title: str
    author: str
    year: int
    tags: List[str]

PROMPT = """Extract the metadata as JSON with keys: title, author, year, tags (list of strings).

Text: "Building Better Pipelines" by Ada Carter (2023). Topics covered: dbt, Airflow, dimensional modeling.

JSON:"""

raw = ask(PROMPT, max_new=80)
print("raw:", raw)

try:
    obj = BlogPost.model_validate_json(raw)
    print("valid:", obj)
except ValidationError as e:
    print("invalid — would retry with the validation error in the prompt")
    print(e)


# %% [markdown] color=teal title="12 · You Finished the Course 🎓"
# # 12 · You Finished the Course 🎓
#
# You've now completed **all 31 modules** of the Data Science Roadmap.
#
# ### What you can do, end-to-end
#
# | Track | Modules | What you can do |
# |---|---|---|
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


