# doodlecode format-version: 2
# Auto-converted from module_62_dpo_from_scratch.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 62 Dpo From Scratch"
# # Module 62 Dpo From Scratch
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 62 — DPO"
# # Module 62 — DPO
#
# > SFT (M39, M59) teaches a model *"these responses are good."* But people don't only know what's good — they know what's **better than** what. **Direct Preference Optimization (DPO)** takes pairs `(chosen, rejected)` and trains the model to prefer the first. It's the algorithm Llama 3, Qwen 2, Mistral-Instruct, and most open-weight chat models use after SFT — without the engineering nightmare of full RLHF/PPO.
# >
# > The whole loss fits in **one formula**. The training loop is just the M57 loop with a custom loss. By the end of this module you can read the DPO paper and recognise every line.
#
# ### What you'll cover
# 1. SFT vs DPO vs PPO — when each one wins
# …


# %% [markdown] color=mint title="1 · SFT vs DPO vs PPO — when each one wins"
# # 1 · SFT vs DPO vs PPO — when each one wins
#
# | Phase | Data shape | Loss | What it teaches |
# |---|---|---|---|
# | **SFT** (M39, M59) | `(prompt, response)` | next-token CE on the response | "this is a good answer" |
# | **DPO** (this module) | `(prompt, chosen, rejected)` | log-ratio of policy/reference on chosen vs rejected | "chosen > rejected" |
# | **PPO** (classic RLHF) | `(prompt, reward_model)` | policy gradient + KL penalty + reward model | "maximise reward; stay near reference" |
#
# …


# %% [markdown] color=peach title="2 · The DPO loss"
# # 2 · The DPO loss
#
# Bradley-Terry says: if humans prefer `y_w` to `y_l` given prompt `x`, then the underlying reward satisfies
#
# $$P(y_w \succ y_l \mid x) = \sigma(r(x, y_w) - r(x, y_l))$$
#
# DPO's clever observation: under a KL-constrained RL objective with a reference policy `π_ref`, the optimal policy `π*` is
#
# …


# %% [markdown] color=violet title="3 · The reference model"
# # 3 · The reference model
#
# `π_ref` is the **frozen copy of your SFT model at the start of DPO training**. Its job:
# - Anchor the policy so it can't drift arbitrarily.
# - Provide the denominator in both log-ratios.
# - Cancel out vocabulary biases (`tokens that are always likely under π_ref` won't fool the gradient).
#
# **Practical notes.**
# …


# %% [markdown] color=amber title="4 · Preference dataset"
# # 4 · Preference dataset
#


# %% color=rose title="!pip -q install torch tiktoken"
# @explain: Run this cell to see the output.
!pip -q install torch tiktoken


# %% color=lime title="Public preference datasets you'll see in the wild"
# @explain: Public preference datasets you'll see in the wild:
# @explain: - Anthropic/hh-rlhf            (helpful + harmless human comparisons)
# @explain: - HuggingFaceH4/UltraFeedback  (GPT-4 labelled, ~64K pairs)
# @explain: - argilla/distilabel-capybara  (multi-turn preference)
# @explain: We'll roll a tiny synthetic dataset here to keep the notebook self-contained
# Public preference datasets you'll see in the wild:
#   - Anthropic/hh-rlhf            (helpful + harmless human comparisons)
#   - HuggingFaceH4/UltraFeedback  (GPT-4 labelled, ~64K pairs)
#   - argilla/distilabel-capybara  (multi-turn preference)
#
# We'll roll a tiny synthetic dataset here to keep the notebook self-contained.
import torch, json, tiktoken
from torch.utils.data import Dataset, DataLoader

PREFERENCES = [
    {
        "prompt":  "What is RAG in one sentence?",
        "chosen":  "Retrieval-Augmented Generation feeds relevant documents into an LLM's prompt so its answer is grounded in retrieved evidence.",
        "rejected": "RAG is a thing.",
    },
    {
        "prompt":  "Explain HNSW like I'm 12.",
        "chosen":  "It's a tower of friend-of-a-friend lists for vectors — you start at a sparse top layer and zoom in to the nearest neighbour layer by layer.",
        "rejected": "Hierarchical Navigable Small World.",
    },
    {
        "prompt":  "Should I use PostgreSQL or MongoDB for a vector store?",
        "chosen":  "Postgres + pgvector is usually the right call: one database, ACID guarantees, hybrid SQL + vector queries.",
        "rejected": "MongoDB.",
    },
] * 10
print("pairs:", len(PREFERENCES))


# %% color=teal title="tok = tiktoken.get_encoding('gpt2')"
# @explain: Run this cell to see the output.
tok = tiktoken.get_encoding("gpt2")
EOT = 50256

def encode_pair(item):
    prompt_ids   = tok.encode(item["prompt"])
    chosen_ids   = tok.encode(item["chosen"])   + [EOT]
    rejected_ids = tok.encode(item["rejected"]) + [EOT]
    return {
        "prompt": prompt_ids,
        "chosen": prompt_ids + chosen_ids,
        "rejected": prompt_ids + rejected_ids,
        "prompt_len": len(prompt_ids),
    }

class DPODataset(Dataset):
    def __init__(self, raw):
        self.rows = [encode_pair(r) for r in raw]
    def __len__(self): return len(self.rows)
    def __getitem__(self, i): return self.rows[i]

ds = DPODataset(PREFERENCES)
print("sample row keys:", list(ds[0].keys()))


# %% color=sky title="DPO collate: pad chosen and rejected separately to…"
# @explain: DPO collate: pad chosen and rejected separately to their own max-in-batch
# @explain: ignore prompt-side AND padding positions; target = next-token shift
# DPO collate: pad chosen and rejected separately to their own max-in-batch
def dpo_collate(batch, pad_id=EOT, ignore_idx=-100):
    def pad_sequence(seqs, max_len):
        return torch.tensor([s + [pad_id] * (max_len - len(s)) for s in seqs])
    def make_labels(full_ids, prompt_len, max_len):
        # ignore prompt-side AND padding positions; target = next-token shift
        labels = torch.full((len(full_ids), max_len - 1), ignore_idx, dtype=torch.long)
        for r, ids in enumerate(full_ids):
            for t in range(prompt_len[r], len(ids) - 1):
                labels[r, t] = ids[t + 1]
        return labels

    chosen_ids   = [b["chosen"]   for b in batch]
    rejected_ids = [b["rejected"] for b in batch]
    prompt_lens  = [b["prompt_len"] for b in batch]

    max_c = max(len(s) for s in chosen_ids)
    max_r = max(len(s) for s in rejected_ids)

    chosen_inputs   = pad_sequence(chosen_ids,   max_c)[:, :-1]
    rejected_inputs = pad_sequence(rejected_ids, max_r)[:, :-1]
    chosen_labels   = make_labels(chosen_ids,   prompt_lens, max_c)
    rejected_labels = make_labels(rejected_ids, prompt_lens, max_r)

    return {
        "chosen_inputs":   chosen_inputs,
        "rejected_inputs": rejected_inputs,
        "chosen_labels":   chosen_labels,
        "rejected_labels": rejected_labels,
    }

loader = DataLoader(ds, batch_size=2, shuffle=True, collate_fn=dpo_collate)
b = next(iter(loader))
print({k: v.shape for k, v in b.items()})


# %% [markdown] color=mint title="Two design points the collate makes"
# # Two design points the collate makes
#
# **Two design points the collate makes.**
# - **Pad chosen and rejected separately** — they have different lengths; padding them to a common max would waste compute on the shorter one.
# - **Mask prompt tokens out of the labels** — exactly like M59's instruction-loss masking. The loss only depends on the model's probability of the **response** tokens.


# %% [markdown] color=peach title="5 · `compute_log_probs` — the helper"
# # 5 · `compute_log_probs` — the helper
#


# %% color=violet title="gather log-prob of the actual label at each position"
# @explain: gather log-prob of the actual label at each position
def compute_log_probs(model, input_ids, labels, ignore_idx=-100):
    """Sum of per-token log-probabilities of the *labelled* (response) tokens."""
    logits = model(input_ids)                                    # (B, T, V)
    log_probs = torch.nn.functional.log_softmax(logits, dim=-1)  # (B, T, V)

    # gather log-prob of the actual label at each position
    safe_labels = labels.clone()
    safe_labels[safe_labels == ignore_idx] = 0                   # gather needs valid indices
    gathered = log_probs.gather(-1, safe_labels.unsqueeze(-1)).squeeze(-1)   # (B, T)

    mask = (labels != ignore_idx).float()
    return (gathered * mask).sum(dim=-1)   # (B,) — sum of log-probs over response tokens


# %% [markdown] color=amber title="This returns one scalar per row: $\log \pi(y \mid…"
# # This returns one scalar per row: $\log \pi(y \mid…
#
# This returns one scalar per row: $\log \pi(y \mid x) = \sum_t \log \pi(y_t \mid x, y_{<t})$ restricted to the response tokens.
#
# Critical detail: **sum, don't average** — DPO compares full sequence log-probabilities (the math doesn't care about length normalisation here; some variants like **length-normalised DPO / SimPO** do).


# %% [markdown] color=rose title="6 · `dpo_loss_batch` — the algorithm"
# # 6 · `dpo_loss_batch` — the algorithm
#


# %% color=lime title="log-ratios"
# @explain: log-ratios
# @explain: metrics
import torch.nn.functional as F

def dpo_loss_batch(policy_model, ref_model, batch, beta=0.1):
    pol_logp_chosen   = compute_log_probs(policy_model, batch["chosen_inputs"],   batch["chosen_labels"])
    pol_logp_rejected = compute_log_probs(policy_model, batch["rejected_inputs"], batch["rejected_labels"])

    with torch.no_grad():                               # reference is frozen
        ref_logp_chosen   = compute_log_probs(ref_model, batch["chosen_inputs"],   batch["chosen_labels"])
        ref_logp_rejected = compute_log_probs(ref_model, batch["rejected_inputs"], batch["rejected_labels"])

    # log-ratios
    logits = beta * ((pol_logp_chosen - ref_logp_chosen)
                     - (pol_logp_rejected - ref_logp_rejected))

    loss = -F.logsigmoid(logits).mean()

    # metrics
    reward_chosen   = (pol_logp_chosen   - ref_logp_chosen).detach()
    reward_rejected = (pol_logp_rejected - ref_logp_rejected).detach()
    return {
        "loss":            loss,
        "reward_chosen":   reward_chosen.mean(),
        "reward_rejected": reward_rejected.mean(),
        "reward_margin":   (reward_chosen - reward_rejected).mean(),
        "reward_accuracy": (reward_chosen > reward_rejected).float().mean(),
    }


# %% [markdown] color=teal title="That's the entire DPO algorithm.** Four log-probs…"
# # That's the entire DPO algorithm.** Four log-probs…
#
# **That's the entire DPO algorithm.** Four log-probs (`policy/reference` × `chosen/rejected`), a difference, a sigmoid, a negative log. Plus four metrics you'll want:
# - `reward_chosen` / `reward_rejected` — what the model "implicitly rewards" each side at (log-prob ratio vs reference).
# - `reward_margin` — how much higher it scores the chosen side. Goes UP during training.
# - `reward_accuracy` — fraction of batch where `chosen > rejected`. Should approach 1.0.


# %% [markdown] color=sky title="7 · The β hyperparameter"
# # 7 · The β hyperparameter
#
# `β` controls how aggressively the policy is allowed to deviate from the reference.
#
# | β | Behaviour |
# |---|---|
# | **β → 0** | the policy is free to do anything — but the gradient is tiny; barely trains |
# | **β = 0.01–0.1** | strong DPO signal; standard range for chat models |
# …


# %% [markdown] color=mint title="8 · Training loop (concept)"
# # 8 · Training loop (concept)
#
# The loop is M57's loop. The only differences are:
# 1. **Two forward passes** per batch (policy + reference).
# 2. **`dpo_loss_batch`** instead of `calc_loss_batch`.
# 3. **Track the four DPO metrics** instead of perplexity.
#
# ```python
# …


# %% [markdown] color=peach title="9 · Failure modes"
# # 9 · Failure modes
#
# | Symptom | Cause | Fix |
# |---|---|---|
# | **`reward_chosen` and `reward_rejected` both fall** ⚠️ | Policy is moving away from BOTH options — it just gets less confident overall | Lower β; add a length normaliser; use **IPO** or **ORPO** instead |
# | **`reward_accuracy` stays near 0.5** | β too small, or LR too small | Bump β to 0.1; LR to 1e-6 |
# | **Hallucinations get worse** | Preference dataset rewards confident-but-wrong | Add SFT mixing (50% SFT loss + 50% DPO loss) |
# | **OOM** | 2× model copies | LoRA-DPO (the reference is "policy minus LoRA"); quantised reference |
# …


# %% [markdown] color=violet title="10 · Where DPO fits in the alignment landscape"
# # 10 · Where DPO fits in the alignment landscape
#
# ```
#                            ┌─────────┐
#                            │ humans  │ → preference labels
#                            └────┬────┘
#                                 ▼
#    pretrain (M57)  →  SFT (M59)  →  DPO (this module)  →  shipped chat model
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


