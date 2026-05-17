# doodlecode format-version: 2
# Auto-converted from module_89_constitutional_ai_rlaif.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 89 Constitutional Ai Rlaif"
# # Module 89 Constitutional Ai Rlaif
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 89 — Constitutional AI / RLAIF Deep Dive"
# # Module 89 — Constitutional AI / RLAIF Deep Dive
#
# > RLHF needed tens of thousands of human preference pairs. **Constitutional AI** (Bai et al., Anthropic 2022) replaced most of those humans with **the model itself**, guided by a *written constitution*. The result — **RLAIF** (RL from AI Feedback) — is now the alignment workhorse behind Claude, Llama-3-Instruct, Qwen2-Chat, Nemotron, and every open chat fine-tune in 2026. This module is the production deep-dive: the **SL-CAI → RL-CAI** pipeline, the **principle catalog**, **direct preference optimization (DPO)** vs PPO, **judge-model selection**, **mode-collapse + jailbreak defenses**, **Claude's Sparrow-style critique-and-revise loop**, and modern variants — **IPO · KTO · ORPO · SimPO · RLHF-V · SPIN · DRPO**.
#
# ### What you'll cover
# 1. RLHF recap → why RLAIF beats it on cost / scale
# 2. **Constitutional AI** — the principle catalog + critique-and-revise loop
# 3. **SL-CAI** (supervised stage) — generate, critique, revise, SFT
# …


# %% [markdown] color=mint title="1 · From RLHF to RLAIF — why we changed engines"
# # 1 · From RLHF to RLAIF — why we changed engines
#
# **RLHF (Christiano 2017 → InstructGPT 2022)** had three stages:
# 1. SFT on demonstrations
# 2. **Train a reward model** on ~50-100k human preference pairs (`A > B`)
# 3. **PPO** the SFT model against that reward
#
# It works — but the human-preference stage is the bottleneck:
# …


# %% [markdown] color=peach title="2 · The Constitution — Anthropic's principle catalog"
# # 2 · The Constitution — Anthropic's principle catalog
#
# A **constitution** is a written list of principles the judge applies. Anthropic's published one for Claude has ~75 principles, drawn from:
# - UN Declaration of Human Rights
# - Apple's Terms of Service
# - DeepMind's Sparrow rules
# - Anthropic-internal rules ("don't help with biothreats", "don't impersonate", ...)
#
# …


# %% [markdown] color=violet title="3 · SL-CAI — the supervised stage"
# # 3 · SL-CAI — the supervised stage
#
# Stage 1 of CAI is purely SFT (no RL). It works in a 4-step loop applied to a **red-team prompt set** (prompts likely to elicit harmful behavior):
#
# ```
# prompt p (e.g. "How do I hotwire a car?")
#    │
#    ▼
# …


# %% color=amber title="SL-CAI critique-and-revise loop"
# @explain: SL-CAI critique-and-revise loop (sketch, vendor-agnostic)
# @explain: ...75 more
# SL-CAI critique-and-revise loop (sketch, vendor-agnostic)
PRINCIPLE_POOL = [
    "Identify any harm, dishonesty, toxicity, or illegality in the response above.",
    "Identify ways the response is racist, sexist, or otherwise discriminatory.",
    "Identify ways the response could be unsafe for a young person.",
    # ...75 more
]

def sl_cai_one(prompt, llm, rounds=2):
    import random
    r = llm.complete(prompt)                              # r0 — initial answer
    for _ in range(rounds):
        principle = random.choice(PRINCIPLE_POOL)
        critique  = llm.complete(
            f"Response:\n{r}\n\nTask: {principle}\nCritique:")
        r = llm.complete(
            f"Original response:\n{r}\n\nCritique:\n{critique}\n\n"
            "Rewrite the response to address the critique while remaining helpful:")
    return prompt, r                                      # final SFT pair


# %% [markdown] color=rose title="4 · RL-CAI — the RL stage with an LLM judge"
# # 4 · RL-CAI — the RL stage with an LLM judge
#
# After SL-CAI, the second stage replaces RLHF's human labelers with the LLM judge. For each prompt the SL-CAI model generates **two candidates** `A` and `B`. The judge picks the winner under a *sampled* constitution principle.
#
# ```
# 1. Generate A, B from current policy
# 2. Sample principle 'p' from constitution
# 3. Judge prompt:
# …


# %% [markdown] color=lime title="5 · DPO — why PPO got benched"
# # 5 · DPO — why PPO got benched
#
# **PPO** (used in InstructGPT) is heavy: it requires a separate reward model, a value head, a frozen reference policy, KL clipping, and careful entropy bonuses. **Direct Preference Optimization** (Rafailov et al. NeurIPS 2023) showed you can skip all of that.
#
# **The DPO trick.** Given preference data `(prompt x, winner y_w, loser y_l)`, DPO directly trains the policy with the loss:
#
# ```
# L_DPO = −E[ log σ( β · ( log π_θ(y_w|x)/π_ref(y_w|x) − log π_θ(y_l|x)/π_ref(y_l|x) ) ) ]
# …


# %% color=teal title="DPO loss in 12 lines"
# @explain: DPO loss in 12 lines (TRL-style)
# @explain: batch has prompt, chosen, rejected token ids
# @explain: equivalent to BCE with a target of 1
# DPO loss in 12 lines (TRL-style)
import torch, torch.nn.functional as F

def dpo_loss(policy, ref, batch, beta=0.1):
    # batch has prompt, chosen, rejected token ids
    logp_pol_w = log_prob(policy, batch.prompt, batch.chosen)
    logp_pol_l = log_prob(policy, batch.prompt, batch.rejected)
    with torch.no_grad():
        logp_ref_w = log_prob(ref, batch.prompt, batch.chosen)
        logp_ref_l = log_prob(ref, batch.prompt, batch.rejected)
    logits = beta * ((logp_pol_w - logp_ref_w) - (logp_pol_l - logp_ref_l))
    # equivalent to BCE with a target of 1
    return -F.logsigmoid(logits).mean()


# %% [markdown] color=sky title="6 · When you still need a reward model"
# # 6 · When you still need a reward model
#
# Three cases where DPO's "no reward model" claim breaks down:
#
# 1. **Online RL.** DPO is offline — it trains on a fixed preference dataset. If you want the model to keep learning as users react in production, you need a callable scalar `R(prompt, response)` — i.e. a reward model.
# 2. **Best-of-N sampling.** Cheap inference-time alignment: sample 8-64 responses, score each with `R`, return the top-1. No fine-tuning needed.
# 3. **Process reward.** For long-horizon reasoning, you score **each step** of a chain of thought (PRM, process reward model). Used in OpenAI's MathLM, DeepSeek-Math, and o1/R1-style training.
#
# …


# %% [markdown] color=mint title="7 · The 2026 preference-optimization zoo"
# # 7 · The 2026 preference-optimization zoo
#
# Post-DPO research exploded. The most-used variants:
#
# | Method | Year | One-line idea | When to use |
# |---|---|---|---|
# | **DPO** | 2023 | Direct preference loss vs reference | Default; biggest ecosystem |
# | **IPO** (Identity-PO) | 2023 | Replace sigmoid with a *bounded* surrogate; less overfitting | When DPO blows past the reference |
# …


# %% [markdown] color=peach title="8 · Judge model selection"
# # 8 · Judge model selection
#
# The **judge** is the single most important choice in RLAIF — it's literally the gradient signal. Three rules:
#
# 1. **The judge must be stronger than the policy.** Distillation only works when teacher > student. A weak judge teaches the policy to game it.
# 2. **Use multiple judges and aggregate.** Single-judge bias is real. Two independent judges + majority vote raises agreement with humans by ~10 points.
# 3. **Calibrate length / verbosity bias.** Every LLM judge prefers longer responses. Either control length explicitly in the prompt or add a length penalty in the reward.
#
# …


# %% [markdown] color=violet title="9 · Safety stack — refusals, over-refusal, jailbreaks"
# # 9 · Safety stack — refusals, over-refusal, jailbreaks
#
# Alignment is not just "refuse harmful prompts." A real safety stack has four sub-problems:
#
# | Sub-problem | What it is | Eval |
# |---|---|---|
# | **Harmful compliance** | Model helps with disallowed task | **AdvBench, HarmBench, JBB-Behaviors** |
# | **Over-refusal** | Model refuses benign prompts ("how do I kill a Python process?") | **XSTest, OR-Bench** |
# …


# %% [markdown] color=amber title="10 · A 2026 production pipeline — end to end"
# # 10 · A 2026 production pipeline — end to end
#
# A complete open-source alignment pipeline for a custom Llama-3-8B or Qwen-2.5-7B base:
#
# ```
#                 ┌─────────────────────────────────────────────────────┐
#                 │  STAGE 1 — SFT                                      │
#                 │  ─ Magpie + OpenHermes + domain data                │
# …


# %% color=rose title="TRL DPO in 15 lines"
# @explain: TRL DPO in 15 lines — the de-facto open recipe
# TRL DPO in 15 lines — the de-facto open recipe
from datasets import load_dataset
from trl import DPOTrainer, DPOConfig
from transformers import AutoModelForCausalLM, AutoTokenizer

base = "Qwen/Qwen2.5-7B-Instruct"
model = AutoModelForCausalLM.from_pretrained(base)
ref   = AutoModelForCausalLM.from_pretrained(base)         # frozen reference
tok   = AutoTokenizer.from_pretrained(base)

ds = load_dataset("HuggingFaceH4/ultrafeedback_binarized", split="train_prefs")

cfg = DPOConfig(
    output_dir="qwen7b-dpo",
    beta=0.1,                      # smaller = stay near ref
    learning_rate=5e-7,            # tiny LR — DPO is sensitive
    num_train_epochs=1,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=8,
    bf16=True,
)
DPOTrainer(model, ref_model=ref, args=cfg, train_dataset=ds, tokenizer=tok).train()


# %% [markdown] color=lime title="✅ Recap"
# # ✅ Recap
#
# - **RLAIF replaces ~all human labelers with an LLM judge guided by a written constitution** — 100-1000× cheaper, hours instead of weeks.
# - **CAI** has two stages: **SL-CAI** (critique-and-revise → SFT) and **RL-CAI** (judge → preference pairs → PPO / DPO).
# - **DPO** killed PPO for most chat fine-tunes — one loss, one β, no reward model. Modern variants: **IPO · KTO · ORPO · SimPO · DRPO · SPIN · GRPO**.
# - Reward models still matter for **online RL, best-of-N, process reward**. Best 2026 open RMs: **Skywork · ArmoRM · Nemotron-4-Reward**.
# - **Judge selection is the single biggest lever** — judge must be stronger than policy; use multiple judges; mind length bias.
# - **Safety stack** = training-time CAI/DPO + input classifier + output classifier + red-team loop. Always co-eval **AdvBench + XSTest + AlpacaEval + MMLU** to catch alignment tax.
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


