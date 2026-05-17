# doodlecode format-version: 2
# Auto-converted from module_67_rlhf_grpo.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 67 Rlhf Grpo"
# # Module 67 Rlhf Grpo
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 67 — RLHF / GRPO"
# # Module 67 — RLHF / GRPO
#
# > M62 covered **DPO** — the simplest, most popular alignment algorithm. This module zooms out to the full alignment landscape. **RLHF (PPO)** is the original recipe that produced ChatGPT. **GRPO** (DeepSeek-R1) is the 2025 algorithm that taught models to *reason* with verifiable rewards. Both belong in your mental model because production-grade post-training mixes all three (SFT → DPO → some RL).
#
# ### What you'll cover
# 1. SFT → DPO → RL — where each one sits and what it adds
# 2. **Classical RLHF**: the 3-stage InstructGPT recipe (SFT, RM, PPO)
# 3. The **reward model** — how preferences become a scalar
# …


# %% [markdown] color=mint title="1 · Where each algorithm sits"
# # 1 · Where each algorithm sits
#
# ```
#    pretrain (M57) ──► SFT (M59) ──► DPO (M62) ──► [optional] RLHF / GRPO ──► ship
#                                        │                    │
#                                        │ pairs (chosen,     │ rollouts + scalar reward
#                                        │  rejected)         │ — much more compute
#                                        ▼                    ▼
# …


# %% [markdown] color=peach title="2 · Classical RLHF — the InstructGPT recipe"
# # 2 · Classical RLHF — the InstructGPT recipe
#
# Three stages, originally published by Christiano (2017) and scaled by Ouyang et al. / OpenAI (2022) for InstructGPT / ChatGPT.
#
# ```
#        Step 1 — SFT                Step 2 — Reward Model       Step 3 — RL (PPO)
#        ┌──────────────┐            ┌───────────────────┐       ┌────────────────────┐
#        │ Pre-trained  │   demos    │  SFT model        │       │  SFT model         │
# …


# %% [markdown] color=violet title="3 · The reward model"
# # 3 · The reward model
#
# Take your SFT model. Replace the LM head with a **scalar head** — a `Linear(d_model, 1)` that reads the last token's hidden state (same trick as M58's classifier). Train on the same `(chosen, rejected)` pairs as DPO with a Bradley-Terry loss:
#
# $$\mathcal{L}_{\text{RM}} = -\log \sigma\big(r_\theta(x, y_w) - r_\theta(x, y_l)\big)$$
#
# After training, `r_θ(x, y)` outputs a number that *correlates* with human preference. You can then **freeze** it and use it as a critic.


# %% color=amber title="Training loss"
# @explain: Training loss — pair-wise (Bradley-Terry)
rm_sketch = '''
class RewardModel(nn.Module):
    def __init__(self, base_model, d_model):
        super().__init__()
        self.base = base_model                   # the SFT model body
        self.value_head = nn.Linear(d_model, 1)  # one scalar per sequence

    def forward(self, input_ids):
        h = self.base(input_ids, output_hidden_states=True).hidden_states[-1]
        return self.value_head(h[:, -1, :])      # last-token logit → scalar reward

# Training loss — pair-wise (Bradley-Terry)
def rm_loss_batch(model, chosen_ids, rejected_ids):
    r_w = model(chosen_ids)
    r_l = model(rejected_ids)
    return -F.logsigmoid(r_w - r_l).mean()
'''
print(rm_sketch)


# %% [markdown] color=rose title="RM gotchas in practice"
# # RM gotchas in practice
#
# **RM gotchas in practice.**
# - **Reward hacking** — the policy quickly finds the RM's blind spots. Always periodically **refresh** the RM by collecting new preferences against the *current* policy.
# - **Calibration** — the absolute scale of `r_θ` is meaningless; only differences matter.
# - **Coverage** — a 1 M-sample RM that never saw your specific failure modes still misses them. RM training data must look like the policy's actual outputs.


# %% [markdown] color=lime title="4 · PPO — the RL stage in five equations"
# # 4 · PPO — the RL stage in five equations
#
# Once you have an RM, **Proximal Policy Optimisation** (Schulman et al., 2017) takes over. PPO is an actor-critic algorithm with three additions:
#
# **(1) Rollouts.** Sample completions from the current policy on prompts $x$:
# $$y \sim \pi_\theta(\cdot \mid x)$$
#
# **(2) Reward + KL penalty.** Each token's reward is the RM score on the *full* sequence, minus a KL term keeping the policy near the SFT reference:
# …


# %% [markdown] color=teal title="5 · Why PPO is painful"
# # 5 · Why PPO is painful
#
# | Pain | Cause | Mitigation |
# |---|---|---|
# | **4 models in memory** | policy + reference + RM + value | LoRA on policy; share weights w/ reference |
# | **Rollouts are the bottleneck** | every step needs `O(generation length)` model calls | batch + vLLM (M44); offload rollouts to a separate worker pool |
# | **Hyperparameter hell** | β, ε, GAE λ, learning rate, batch composition all sensitive | start with the InstructGPT defaults; don't sweep until basics work |
# | **Reward hacking** | policy finds RM blind spots | periodically refresh RM; KL penalty β tuned aggressively |
# …


# %% [markdown] color=sky title="6 · GRPO — what DeepSeek-R1 actually used"
# # 6 · GRPO — what DeepSeek-R1 actually used
#
# DPO needs **preference pairs**. PPO needs a **reward model**. **GRPO** (Group-Relative Policy Optimization, DeepSeek 2024-25) needs **neither** — just a **scalar reward function** (e.g. "did the answer match the gold value?").
#
# The trick: for each prompt $x$, sample **`G` completions** $y_1, \ldots, y_G$. Compute scalar rewards $r_1, \ldots, r_G$. The advantage of each sample is the **standardised reward within the group**:
# $$A_i = \frac{r_i - \text{mean}(r_{1..G})}{\text{std}(r_{1..G})}$$
#
# No value model. The group's own mean and std play the role of the baseline.
# …


# %% color=mint title="Pseudocode"
# @explain: Pseudocode — full implementation in `trl.GRPOTrainer` (2024+) or `openrlhf`
# @explain: 1) sample G completions per prompt
# @explain: 2) compute group-relative advantages
# @explain: 3) compute per-token log-probs under policy and reference
# @explain: 4) ratio + clipped surrogate
grpo_sketch = '''
# Pseudocode — full implementation in `trl.GRPOTrainer` (2024+) or `openrlhf`
import torch, torch.nn.functional as F

def grpo_step(policy, ref_model, prompt_ids, reward_fn, group_size=8, beta=0.04, epsilon=0.2):
    # 1) sample G completions per prompt
    completions = sample_many(policy, prompt_ids, n=group_size)        # (G, T)
    rewards = torch.tensor([reward_fn(c) for c in completions])        # (G,)

    # 2) compute group-relative advantages
    adv = (rewards - rewards.mean()) / (rewards.std() + 1e-8)          # (G,)

    # 3) compute per-token log-probs under policy and reference
    logp     = compute_log_probs(policy, completions)                  # (G, T)
    logp_ref = compute_log_probs(ref_model, completions)               # (G, T)
    logp_old = logp.detach()                                            # save old policy snapshot

    # 4) ratio + clipped surrogate
    ratio = (logp - logp_old).exp()                                     # (G, T)
    unclipped = ratio * adv[:, None]
    clipped   = ratio.clamp(1 - epsilon, 1 + epsilon) * adv[:, None]
    policy_loss = -torch.min(unclipped, clipped).mean()

    # 5) per-token KL to the reference
    kl = (logp - logp_ref).mean()
    loss = policy_loss + beta * kl
    return loss
'''
print(grpo_sketch)


# %% [markdown] color=peach title="Why GRPO matters"
# # Why GRPO matters
#
# **Why GRPO matters.**
# - **No value model** → ~30% less VRAM, ~2× simpler code.
# - **No reward model** *required* — just a scalar reward function. For math/code this can be **`int(pred == gold)`**.
# - **Group baseline** — the group mean acts as a per-prompt baseline. Lower variance than vanilla policy gradient.
# - **Same clipping trick** as PPO so the algorithm inherits its stability.
#
# This is the algorithm that produced **DeepSeek-R1**, the first openly-published "reasoning" model competitive with **o1**. The same trick is used in **Qwen3**, **Llama-Nemotron-Reasoning**, and several closed-source frontier reasoners.


# %% [markdown] color=violet title="7 · RLVR — Reinforcement Learning with Verifiable Rewards"
# # 7 · RLVR — Reinforcement Learning with Verifiable Rewards
#
# GRPO is the *algorithm*. **RLVR** is the *recipe* that makes it work for reasoning: train on tasks where the **reward function is exact and cheap**.
#
# | Task | Reward function | Why it works |
# |---|---|---|
# | **Math** | `int(answer == gold_answer)` | gold answer in the dataset |
# | **Code** | `int(unit_tests_pass)` | run the test suite |
# …


# %% [markdown] color=amber title="8 · Reward hacking — recognise it, kill it"
# # 8 · Reward hacking — recognise it, kill it
#
# Whether you use RM-PPO or RLVR-GRPO, **the policy will try to game the reward**. Classic forms:
#
# | Hack | Example | Fix |
# |---|---|---|
# | **Length bias** | model writes 5-paragraph answers because RM prefers them | length-normalise reward |
# | **Format gaming** | model wraps answers in code blocks the RM likes | diversify training data |
# …


# %% [markdown] color=rose title="9 · What frontier labs actually run in 2025"
# # 9 · What frontier labs actually run in 2025
#
# Approximate post-training pipelines based on open papers + reported recipes:
#
# | Model | Post-training |
# |---|---|
# | **GPT-4o / GPT-5** | SFT → multi-stage RLHF (RM + PPO) with extensive red-teaming RMs |
# | **Claude 3.5 / 3.7 Sonnet** | SFT → **Constitutional AI** (RLAIF) → DPO-flavoured + extensive evals |
# …


# %% [markdown] color=lime title="10 · Decision table — pick your alignment recipe"
# # 10 · Decision table — pick your alignment recipe
#
# | You have… | Reach for | Why |
# |---|---|---|
# | `(prompt, response)` demos | **SFT** (M59) | always step 1 |
# | `(prompt, chosen, rejected)` preference pairs | **DPO** (M62) | simplest, most stable |
# | A trained reward model + lots of compute | **PPO** | classic; if you already have the RM, mature tooling |
# | A scalar reward function (math, code, format) | **GRPO** | no value model; the modern default for verifiable tasks |
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


