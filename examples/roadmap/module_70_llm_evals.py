# doodlecode format-version: 2
# Auto-converted from module_70_llm_evals.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 70 Llm Evals"
# # Module 70 Llm Evals
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 70 — LLM Evals"
# # Module 70 — LLM Evals
#
# > **"Did this prompt change make the product better or worse?"** is the question every team gets wrong every week — because they ship by **vibes** instead of **metrics**. Eval is what turns a chatbot from a demo into a product. This module is the **complete eval stack**: academic benchmarks via **lm-eval-harness**, prompt regression via **Promptfoo**, production tracing + LLM-as-judge via **Langfuse**, exploration + curation via **Arize Phoenix**, plus the unwritten rules every senior LLM engineer follows.
#
# ### What you'll cover
# 1. The five eval flavours — when to use which
# 2. Build your **golden set** (the single most important asset)
# 3. **Reference metrics** (when they actually work) — exact match, ROUGE, BLEU
# …


# %% [markdown] color=mint title="1 · The five flavours of LLM eval"
# # 1 · The five flavours of LLM eval
#
# | Flavour | What it measures | When |
# |---|---|---|
# | **Reference-metric** (BLEU/ROUGE/exact) | similarity to a gold answer | classification, extraction, deterministic outputs |
# | **Programmatic checks** | "does this output parse as JSON? does this code run? does this regex match?" | structured outputs, code, tool calls |
# | **LLM-as-judge** | a stronger model scores your model's output | open-ended generation (most chat use cases) |
# | **Human eval** | humans score on a rubric | the most accurate; expensive; reserve for high-stakes decisions |
# …


# %% [markdown] color=peach title="2 · The golden set — your one critical asset"
# # 2 · The golden set — your one critical asset
#
# Before any tool, before any framework, you need **the golden set**: a curated `(input, expected output, metadata)` dataset that represents your real traffic. Without it, every eval lies.
#
# ### How to build one
# 1. **Sample 100-300 real production traces.** (M51 OTel makes this trivial.)
# 2. **Stratify by intent / persona** — don't oversample easy queries.
# 3. **Label by hand** — yes, by hand. With the eventual rubric you'll automate.
# …


# %% [markdown] color=violet title="3 · Reference metrics — when they work, when they don't"
# # 3 · Reference metrics — when they work, when they don't
#


# %% color=amber title="!pip -q install 'datasets' 'evaluate' rouge_score nltk"
# @explain: Run this cell to see the output.
!pip -q install "datasets" "evaluate" rouge_score nltk


# %% color=rose title="Reference metrics work when there's a single right…"
# @explain: Reference metrics work when there's a single right answer
# @explain: They fall apart on open-ended generation
# Reference metrics work when there's a single right answer.
# They fall apart on open-ended generation.

import evaluate
exact   = evaluate.load("exact_match")
rouge   = evaluate.load("rouge")
bleu    = evaluate.load("bleu")

preds = [
    "Paris",
    "The capital of France is Paris.",
    "It is Paris, the City of Light.",
]
refs  = ["Paris"] * 3

print("exact :", exact.compute(predictions=preds, references=refs))
print("rouge :", rouge.compute(predictions=preds, references=refs))
print("bleu  :", bleu.compute(predictions=preds, references=[[r] for r in refs]))


# %% [markdown] color=lime title="Read the output.** Three semantically equivalent…"
# # Read the output.** Three semantically equivalent…
#
# **Read the output.** Three semantically equivalent answers give wildly different scores. Reference metrics:
#
# | Metric | When it works | When it fails |
# |---|---|---|
# | **Exact match** | classification, structured extraction | any free-form generation |
# | **ROUGE-1/2/L** | summarisation against curated references | paraphrase, multiple-valid-answers |
# | **BLEU** | machine translation | LLM chat |
# | **chrF / METEOR** | translation with character-level robustness | still fails on style variation |
# …


# %% [markdown] color=teal title="4 · LLM-as-judge — the modern default"
# # 4 · LLM-as-judge — the modern default
#


# %% [markdown] color=sky title="Most chat outputs can't be reference-matched"
# # Most chat outputs can't be reference-matched
#
# Most chat outputs can't be reference-matched. Instead, **another LLM grades them**. The standard recipe — single-turn, pair-wise, and rubric — popularised by MT-Bench, AlpacaEval, Arena-Hard.


# %% color=mint title="LLM-as-judge prompt template"
# @explain: LLM-as-judge prompt template (the one most papers use)
# @explain: parse the verdict robustly
# @explain: Use the model_call function from M38/M44/M64 to plug in your judge
# LLM-as-judge prompt template (the one most papers use)
JUDGE_PROMPT = '''You are an impartial judge.
Compare the two responses to the question below.
Pick the one that is more {axis}.

[Question]
{question}

[Response A]
{a}

[Response B]
{b}

Output exactly one of: A, B, TIE.
Reasoning first; final answer on its own line as: VERDICT: <A|B|TIE>'''

def judge_pair(question, a, b, axis="helpful and correct", model_call=None):
    prompt = JUDGE_PROMPT.format(question=question, a=a, b=b, axis=axis)
    out = model_call(prompt)
    # parse the verdict robustly
    verdict_line = next((l for l in out.splitlines() if l.upper().startswith("VERDICT:")), "")
    verdict = verdict_line.upper().split(":")[-1].strip()
    return verdict if verdict in {"A","B","TIE"} else "TIE"

# Use the model_call function from M38/M44/M64 to plug in your judge.


# %% [markdown] color=peach title="Five rules to keep your judge honest"
# # Five rules to keep your judge honest
#
# 1. **Pairwise > absolute scores.** Models are notoriously bad at calibrating "give a 7/10." They're decent at "which of these two is better." Always prefer A-vs-B.
# 2. **Swap A/B and average.** Judges have a **position bias** — they prefer the first option ~10% more often. Run each pair twice with swapped order and average.
# 3. **Use a stronger model than the one being judged.** Judging Llama-8B with GPT-4o is fine; judging GPT-4o with Llama-8B is not.
# 4. **Calibrate on a small human-labelled subset.** If your judge agrees with humans on <80% of a 50-row check set, the judge prompt is broken.
# 5. **Don't use the same model as the one you're optimising for.** Judging GPT-4 outputs with GPT-4 inflates self-similar style.
#
# …


# %% [markdown] color=violet title="5 · lm-eval-harness — academic benchmarks"
# # 5 · lm-eval-harness — academic benchmarks
#


# %% color=amber title="!pip -q install 'lm-eval[hf]==0.4.3'"
# @explain: Run this cell to see the output.
!pip -q install "lm-eval[hf]==0.4.3"


# %% [markdown] color=rose title="`lm-evaluation-harness`** (EleutherAI) is the…"
# # `lm-evaluation-harness`** (EleutherAI) is the…
#
# **`lm-evaluation-harness`** (EleutherAI) is the canonical academic eval runner. Every model card, every leaderboard, every paper benchmarks against its task implementations. If you publish a model, you publish lm-eval-harness numbers.


# %% color=lime title="evaluate a HuggingFace model on five common benchmarks"
# @explain: evaluate a HuggingFace model on five common benchmarks
# @explain: evaluate via a hosted OpenAI-compatible endpoint (your vLLM from M44)
# @explain: Programmatic API
sample_command = '''
# evaluate a HuggingFace model on five common benchmarks
$ lm_eval \
    --model hf \
    --model_args pretrained=meta-llama/Llama-3.2-1B,dtype=bfloat16 \
    --tasks mmlu,hellaswag,arc_challenge,gsm8k,humaneval \
    --batch_size auto \
    --output_path results/llama-3.2-1b

# evaluate via a hosted OpenAI-compatible endpoint (your vLLM from M44)
$ lm_eval \
    --model openai-chat-completions \
    --model_args model=qwen2.5-7b-instruct,base_url=http://localhost:8000/v1,api_key=x \
    --tasks gpqa,ifeval,gsm8k

# Programmatic API
import lm_eval
res = lm_eval.simple_evaluate(
    model="hf",
    model_args="pretrained=gpt2",
    tasks=["arc_easy"],
    limit=20,
)
print(res["results"])
'''
print(sample_command)


# %% [markdown] color=teal title="The benchmark cheat sheet"
# # The benchmark cheat sheet
#
# | Benchmark | What it tests | Status in 2026 |
# |---|---|---|
# | **MMLU** (57 subjects) | broad academic knowledge | nearly saturated — frontier > 89% |
# | **HellaSwag** | commonsense completion | saturated |
# | **ARC-Challenge** | grade-school science | saturated |
# | **WinoGrande** | pronoun resolution | saturated |
# …


# %% [markdown] color=sky title="6 · Promptfoo — prompt regression in YAML + CI"
# # 6 · Promptfoo — prompt regression in YAML + CI
#


# %% color=mint title="!pip -q install --upgrade promptfoo"
# @explain: Run this cell to see the output.
!pip -q install --upgrade promptfoo


# %% [markdown] color=peach title="Promptfoo** is the most popular prompt-testing tool"
# # Promptfoo** is the most popular prompt-testing tool
#
# **Promptfoo** is the most popular prompt-testing tool. It treats prompts like code: you write **YAML test specs** with assertions; CI runs them on every PR; reports show diffs vs the previous baseline.


# %% color=violet title="promptfooconfig.yaml"
# @explain: promptfooconfig.yaml
promptfoo_yaml = '''
# promptfooconfig.yaml
prompts:
  - "Summarise this in one sentence: {{text}}"
  - "Write a 1-sentence summary of: {{text}}"

providers:
  - id: openai:gpt-4o-mini
  - id: ollama:chat:qwen2.5:0.5b-instruct     # local M38
  - id: openai:gpt-4o                           # the judge

tests:
  - vars:
      text: "The quick brown fox jumps over the lazy dog."
    assert:
      - type: contains
        value: "fox"
      - type: javascript
        value: "output.length < 200"

  - vars:
      text: "Mass produces general relativity's spacetime curvature."
    assert:
      - type: llm-rubric
        value: "The summary preserves the cause-effect relation between mass and curvature."
      - type: factuality
        value: "Mass causes spacetime to curve, which is what we perceive as gravity."

  - vars: { text: "1+1" }
    assert:
      - type: not-contains
        value: "violence"
'''
print(promptfoo_yaml)


# %% [markdown] color=amber title="Promptfoo gives you"
# # Promptfoo gives you
#
# **Promptfoo gives you, out of the box.**
# - **Side-by-side prompt × provider grid** — try N prompts on M models in one run.
# - **Assertion types**: `equals`, `contains`, `regex`, `is-json`, `javascript` (custom JS), `llm-rubric` (judge), `factuality`, `latency`, `cost`.
# - **`promptfoo eval` in CI** — fails the build if pass-rate drops below threshold.
# - **`promptfoo view`** — local web UI with diffs across runs.
# - **Datasets** — point at a CSV / Google Sheet of `(input, expected)` rows.
#
# This is **the** answer to "did my prompt change make things better?" Run it on every PR.


# %% [markdown] color=rose title="7 · Langfuse + Phoenix — production evals on real traffic"
# # 7 · Langfuse + Phoenix — production evals on real traffic
#
# Once your app is live, the question becomes: **how well is it doing on production traffic?** Two open-source tools that have eaten this space:
#
# ### Langfuse
# - **Tracing** — every LLM call, every tool call, captured as nested spans (overlaps with OTel from M51; Langfuse accepts OTLP).
# - **Datasets** — promote real production traces into reusable eval datasets.
# - **Online evaluators** — define scorers (LLM-as-judge, regex, code execution) that run on every production trace.
# …


# %% color=lime title="Sketch"
# @explain: Sketch — instrument an LLM call so each request becomes a trace + dataset row
# @explain: attach metadata for later filtering
# @explain: Every call now produces a trace
# @explain: run an offline batch eval with an LLM-as-judge scorer
# Sketch — instrument an LLM call so each request becomes a trace + dataset row
langfuse_sketch = '''
from langfuse.decorators import observe, langfuse_context

@observe()
def rag_chat(user_query: str):
    docs = retriever.search(user_query, k=4)
    answer = llm.complete(make_prompt(user_query, docs))

    # attach metadata for later filtering
    langfuse_context.update_current_observation(
        input=user_query,
        output=answer,
        metadata={"n_docs": len(docs)},
    )
    return answer

# Every call now produces a trace. Promote 200 of them to a dataset and
# run an offline batch eval with an LLM-as-judge scorer.
'''
print(langfuse_sketch)


# %% [markdown] color=teal title="The two-loop pattern** every shipping LLM team…"
# # The two-loop pattern** every shipping LLM team…
#
# **The two-loop pattern** every shipping LLM team converges on:
#
# ```
#    PR     ──► Promptfoo regression on golden set ──► fail-fast CI
#    merge  ──► deploy to prod
#    prod   ──► Langfuse traces everything
#    nightly──► sample traces → judge → metrics
#    weekly ──► curate new failures into golden set ──► loop
# …


# %% [markdown] color=sky title="8 · Online evals — A/B testing LLM apps"
# # 8 · Online evals — A/B testing LLM apps
#
# Offline evals say "the new prompt is 4 % better on my golden set." **Online evals** ask "did real users prefer it?" Same A/B-testing machinery as classic web (M28's stats), with LLM-specific gotchas.
#
# ### Three signals you can A/B
# - **Behavioural** — completion rate, escalation rate, retry rate, session length.
# - **Explicit** — thumbs up/down, in-product rating.
# - **Implicit** — copy-button clicks, "regenerate" clicks (negative signal), follow-up question rate.
# …


# %% [markdown] color=mint title="9 · Anti-patterns"
# # 9 · Anti-patterns
#
# | Anti-pattern | Why it bites | Fix |
# |---|---|---|
# | **Benchmark contamination** | model's training set saw the test questions; scores are inflated | use *fresh* benchmarks (LiveBench, AIME-new, SimpleBench), test on held-out internal data |
# | **Goodhart's law** | optimising for the metric warps the model | rotate benchmarks; prioritise online signals |
# | **Single-prompt evals** | one prompt template hides robustness | eval across paraphrases of the same intent |
# | **Judge bias** | judge prefers verbose answers / its own outputs | swap order, calibrate vs humans, prefer pairwise |
# …


# %% [markdown] color=peach title="10 · The eval playbook every shipping LLM team should follow"
# # 10 · The eval playbook every shipping LLM team should follow
#
# Adopt these six practices in order. Most teams stop at step 2 and pay for it later.
#
# 1. **Curate a 200-row golden set** stratified by intent. Version in git. Re-curate quarterly.
# 2. **Promptfoo on every PR** with hard assertions + LLM-rubric. Fail the build under threshold.
# 3. **`lm-eval-harness` on every release** for the relevant benchmarks (small set, not the whole zoo).
# 4. **Production tracing in Langfuse / Phoenix.** Every LLM call captured; nightly sampled judge scoring.
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


