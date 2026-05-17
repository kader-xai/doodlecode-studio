# doodlecode format-version: 2
# Auto-converted from module_88_synthetic_data_distillation.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 88 Synthetic Data Distillation"
# # Module 88 Synthetic Data Distillation
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 88 — Synthetic Data Generation + Distillation"
# # Module 88 — Synthetic Data Generation + Distillation
#
# > The 2024-2026 frontier-model recipe is no longer "scrape more web." It's **synthetic data**: a strong teacher generates training data for a smaller / faster student. **Phi-3 / Phi-4**, **Orca-2**, **WizardLM Evol-Instruct**, **Self-Instruct**, **Self-Rewarding LM**, **Magpie**, **Nemotron-4 340B**, **DeepSeek-R1 → distilled-Qwen / distilled-Llama**, **STaR / Quiet-STaR**, **rejection sampling fine-tuning (RFT)** — all the same idea with different sauces. This module covers the full taxonomy, the math (KL knowledge distillation vs SFT-on-teacher-outputs), the **quality filters** that decide success, and a hands-on Magpie + RFT loop.
#
# ### What you'll cover
# 1. **Why synthetic data** — the data wall, cost of human labels, and the Phi / Orca recipe
# 2. The four flavors — **SFT distillation · KL distillation · Self-Instruct · RLAIF/RFT**
# 3. **Self-Instruct** + **Evol-Instruct** (WizardLM) prompt-evolution
# …


# %% [markdown] color=mint title="1 · Why synthetic data — the data wall"
# # 1 · Why synthetic data — the data wall
#
# By 2024 frontier labs had **already trained on most of the open web**. Three forces pushed synthetic to the center:
#
# | Force | What it means |
# |---|---|
# | **Data wall** | High-quality human text grows ~5%/yr; compute grows 10× faster. There's no more web to scrape. |
# | **Cost of labels** | Human SFT pairs cost $1-10 each; LLM-generated pairs cost $0.001-0.01. **1000× cheaper.** |
# …


# %% [markdown] color=peach title="2 · The four flavors of distillation"
# # 2 · The four flavors of distillation
#
# ```
#                  ┌───────────────────────────────┐
#                  │     SYNTHETIC DATA FLAVORS    │
#                  └───────────────────────────────┘
#                                  │
#    ┌─────────────┬───────────────┴────────────────┬─────────────┐
# …


# %% [markdown] color=violet title="3 · Self-Instruct + Evol-Instruct"
# # 3 · Self-Instruct + Evol-Instruct
#
# **Self-Instruct (Wang et al., 2022)** was the first scalable synthetic-data pipeline:
#
# ```
# 1. Hand-write 175 seed tasks
# 2. For each round:
#    2a. Sample 6 seed tasks + 2 generated tasks
# …


# %% color=amber title="Self-Instruct seed → expansion"
# @explain: Self-Instruct seed → expansion (sketch)
# @explain: ...173 more
# Self-Instruct seed → expansion (sketch)
SEED = [
    {"instruction": "Convert a CSV row to JSON.", "input": "name,age\nAda,36", "output": '{"name": "Ada", "age": 36}'},
    {"instruction": "Explain photosynthesis in one paragraph.", "input": "", "output": "..."},
    # ...173 more
]

PROMPT_TEMPLATE = '''You are a creative task author. Here are example tasks:

{examples}

Now write 8 MORE tasks of the same style. Be diverse — include classification, generation, reasoning, summarization, code.
Output as JSON list with keys "instruction", "input", "output".'''

def expand(pool, llm, rounds=100, k=6):
    import random, json
    for _ in range(rounds):
        examples = random.sample(pool, k)
        text = PROMPT_TEMPLATE.format(examples=json.dumps(examples, indent=2))
        new = llm(text)                       # generates 8 tasks
        for t in new:
            if max(rouge_l(t['instruction'], p['instruction']) for p in pool) < 0.7:
                pool.append(t)
    return pool


# %% [markdown] color=rose title="4 · Magpie — the zero-prompt synthetic-data trick"
# # 4 · Magpie — the zero-prompt synthetic-data trick
#
# **Magpie (Xu et al., 2024)** showed something wild: you can **extract** the entire training distribution of an instruction-tuned LLM by feeding it *only the chat template prefix* and letting it free-generate the user turn:
#
# ```
# <|user|>          ← give the model ONLY this
#                   ← it now generates a plausible user instruction
# ↓
# …


# %% [markdown] color=lime title="5 · Orca / Orca-2 — distill the reasoning, not just the answer"
# # 5 · Orca / Orca-2 — distill the reasoning, not just the answer
#
# The Orca recipe is one line: **"Tell GPT-4 to *think step by step and show its work*, then train the student on the trace."**
#
# | Standard SFT pair | Orca SFT pair |
# |---|---|
# | `Q: 23×47?  A: 1081` | `Q: 23×47?  A: Let me compute: 23×47 = 23×40 + 23×7 = 920 + 161 = 1081.` |
#
# …


# %% [markdown] color=teal title="6 · Self-Rewarding LM + RLAIF as data engines"
# # 6 · Self-Rewarding LM + RLAIF as data engines
#
# **Self-Rewarding LM (Meta, 2024)** noticed: if you have one model, you can use it as **both** generator *and* judge:
#
# ```
# Loop:
#   step 1:  generate K candidate completions for each prompt
#   step 2:  same model rates them with an "LLM-as-judge" prompt → reward
# …


# %% [markdown] color=sky title="7 · Rejection Sampling Fine-Tuning (RFT) + STaR"
# # 7 · Rejection Sampling Fine-Tuning (RFT) + STaR
#
# For **verifiable** tasks (math, code, formal proofs) you don't need an LLM judge — you have a **ground-truth checker**. That makes synthetic data trivially correct.
#
# **RFT pipeline (Touvron et al. 2023 · Llama-2 paper):**
# ```
# 1. Take a prompt with a known answer (GSM8K, MATH, HumanEval)
# 2. Sample N=100 chain-of-thought completions at T=0.8
# …


# %% [markdown] color=mint title="8 · DeepSeek-R1 distillation — the 2025 shocker"
# # 8 · DeepSeek-R1 distillation — the 2025 shocker
#
# DeepSeek-R1 (Jan 2025) is a 671B MoE that learned long-form reasoning via **pure RL** (GRPO) with verifiable rewards — no SFT cold start. The shocker for the open-source world was the **distillation appendix**:
#
# ```
# DeepSeek-R1 (671B teacher)
#   │
#   ├─→ generate 800k (prompt, reasoning, answer) traces
# …


# %% color=peach title="DeepSeek-R1-style distillation recipe"
# @explain: DeepSeek-R1-style distillation recipe (HuggingFace TRL · sketch)
# @explain: 1
# @explain: Each row: { 'prompt': "...", 'completion': "<think>...</think><answer>...</answer>" }
# @explain: 2
# DeepSeek-R1-style distillation recipe (HuggingFace TRL · sketch)
from datasets import Dataset
from trl import SFTTrainer, SFTConfig
from transformers import AutoModelForCausalLM, AutoTokenizer

# 1. Generate traces from the teacher (offline, batched, vLLM)
#    Each row: { 'prompt': "...", 'completion': "<think>...</think><answer>...</answer>" }
ds = Dataset.from_json('r1_traces_800k.jsonl')

# 2. Train the student
student = AutoModelForCausalLM.from_pretrained('Qwen/Qwen2.5-7B')
tok     = AutoTokenizer.from_pretrained('Qwen/Qwen2.5-7B')

cfg = SFTConfig(
    output_dir='qwen7b-r1-distill',
    max_seq_length=16384,        # long reasoning traces!
    per_device_train_batch_size=2,
    gradient_accumulation_steps=16,
    learning_rate=1e-5,
    num_train_epochs=2,
    bf16=True,
    packing=True,                # critical for throughput
)
trainer = SFTTrainer(student, args=cfg, train_dataset=ds, tokenizer=tok)
trainer.train()


# %% [markdown] color=violet title="9 · Quality filters — the bit that actually matters"
# # 9 · Quality filters — the bit that actually matters
#
# Naive synthetic data is **worse** than no data — repetition, hallucinated facts, format collapse all destroy a student. Every successful pipeline above leans on aggressive filtering:
#
# | Filter | What it catches | Common tool |
# |---|---|---|
# | **Exact-dedup** | Verbatim copies (n-gram hash) | `text-dedup` · MinHash-LSH |
# | **Semantic-dedup** | Near-duplicates | embedding sim > 0.9 (BGE / E5 / Nomic) |
# …


# %% [markdown] color=amber title="10 · The 2026 synthetic-data stack + risks"
# # 10 · The 2026 synthetic-data stack + risks
#
# **OSS synthetic-data toolkit (May 2026):**
#
# | Tool | What it does |
# |---|---|
# | **distilabel** (Argilla) | End-to-end synthetic-data pipelines; ships Self-Instruct, Evol-Instruct, Magpie, UltraFeedback templates |
# | **Nemotron-4 340B + Reward** (NVIDIA) | Open weight teacher + reward model designed for synthetic-data work |
# …


# %% [markdown] color=rose title="✅ Recap"
# # ✅ Recap
#
# - **Synthetic data** broke the data wall; **quality > quantity** once you have a strong teacher.
# - Four flavors: **SFT distillation · KL distillation · Self-Instruct · RLAIF/RFT** — pick by what you have access to.
# - **Self-Instruct → Evol-Instruct → Magpie** is the open-prompt evolution chain; **Orca / R1-distill** is the closed-prompt reasoning-trace chain.
# - **RFT / STaR** for verifiable tasks (math, code, proofs) — the verifier *is* the reward model.
# - **DeepSeek-R1 distillation**: boring SFT on `<think>...</think>` traces beats clever losses; replicated everywhere in 2025.
# - **Filtering keeps 5-30%** of raw synthetic data — dedup · perplexity · reward model · verifier · diversity · contamination check.
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


