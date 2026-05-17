# doodlecode format-version: 2
# Auto-converted from module_24_new_transformer_programming.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 24 New Transformer Programming"
# # Module 24 New Transformer Programming
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 24 — New Transformer Programming"
# # Module 24 — New Transformer Programming
#
# > **Source:** the actual inference code in
# > [`DeepSeek-V3/inference/`](https://github.com/deepseek-ai/DeepSeek-V3/tree/main/inference) — the codebase that runs the 671 B-parameter open-weight model.
#
# In M19 you built single-head attention. In M20 you built multi-head causal attention plus the standard transformer block. This module shows how a **production-grade 671 B-parameter LLM** modifies that exact same architecture for inference at scale.
#
# Every modern LLM in 2026 — Llama 3, Mistral, Qwen, DeepSeek — uses some of these tricks. Once you can read the DeepSeek source, you can read all of them.
# …


# %% color=mint title="!pip -q install torch"
# @explain: Run this cell to see the output.
!pip -q install torch
import torch, torch.nn as nn, torch.nn.functional as F, math
torch.manual_seed(0)
print("torch:", torch.__version__)


# %% [markdown] color=peach title="1 · The big picture — what's in `inference/`"
# # 1 · The big picture — what's in `inference/`
#
# The repo organises inference code into a handful of focused files:
#
# | File | Purpose |
# |---|---|
# | `model.py` | the network: `Block`, `MLA`, `MoE`, `RMSNorm`, embeddings |
# | `kernel.py` | low-level FP8 kernels: `act_quant`, `weight_dequant`, `fp8_gemm` |
# …


# %% [markdown] color=violet title="2 · `ModelArgs` — every hyperparameter named"
# # 2 · `ModelArgs` — every hyperparameter named
#
# Top of `model.py` you'll see a dataclass like this (excerpts, simplified for teaching):


# %% color=amber title="----- size -----"
# @explain: ----- size -----
# @explain: ----- attention -----
# @explain: ----- mixture of experts -----
# @explain: ----- positional -----
from dataclasses import dataclass

@dataclass
class ModelArgs:
    # ----- size -----
    max_batch_size: int = 8
    max_seq_len:    int = 4096 * 4
    vocab_size:     int = 102400        # tokenizer vocab
    dim:            int = 2048          # hidden dim of the residual stream
    inter_dim:      int = 10944         # FFN intermediate dim (≈ 5.3× dim)
    moe_inter_dim:  int = 1408          # FFN dim INSIDE each MoE expert (much smaller)
    n_layers:       int = 27            # transformer layers
    n_dense_layers: int = 1             # first N layers use a regular FFN, then MoE

    # ----- attention -----
    n_heads:           int = 16
    q_lora_rank:       int = 0          # 0 = no Q low-rank
    kv_lora_rank:      int = 512        # ← THE KEY: KV is compressed to 512 dims
    qk_nope_head_dim:  int = 128        # head dim for the "no-position" part
    qk_rope_head_dim:  int = 64         # head dim for the rotary part
    v_head_dim:        int = 128

    # ----- mixture of experts -----
    n_routed_experts:    int = 64       # the pool of experts
    n_shared_experts:    int = 2        # always-on experts
    n_activated_experts: int = 6        # how many fire per token

    # ----- positional -----
    rope_theta: float = 10000.0          # rotary base frequency

print(ModelArgs())


# %% [markdown] color=rose title="The two unusual numbers**"
# # The two unusual numbers**
#
# **The two unusual numbers** — they distinguish DeepSeek from a vanilla LLM:
#
# - `kv_lora_rank = 512` — keys and values are stored in a **512-dim latent**, not the full per-head space. That's the **MLA** trick.
# - `n_routed_experts = 64`, `n_activated_experts = 6` — only 6 of 64 experts run for each token. Inference cost ∝ 6, capacity ∝ 64. That's the **MoE** trick.


# %% [markdown] color=lime title="3 · RMSNorm — LayerNorm minus the mean"
# # 3 · RMSNorm — LayerNorm minus the mean
#
# Standard `LayerNorm`: `(x - mean) / std · γ + β`
# DeepSeek's `RMSNorm`: `x / rms(x) · γ`     (no mean subtraction, no bias)
#
# It works because the mean of high-dim vectors is approximately 0 anyway, so dropping it saves arithmetic without hurting accuracy. Used by Llama, Mistral, DeepSeek, Qwen.


# %% color=teal title="rsqrt(x²+ε) · γ                ← saves one division…"
# @explain: rsqrt(x²+ε) · γ                ← saves one division vs naive sqrt
class RMSNorm(nn.Module):
    """The full DeepSeek RMSNorm — six lines, no magic."""
    def __init__(self, dim: int, eps: float = 1e-6):
        super().__init__()
        self.eps = eps
        self.weight = nn.Parameter(torch.ones(dim))   # learnable γ; β is dropped

    def forward(self, x):
        # rsqrt(x²+ε) · γ                ← saves one division vs naive sqrt
        rms = x.pow(2).mean(-1, keepdim=True).add(self.eps).rsqrt()
        return (x * rms) * self.weight


x = torch.randn(2, 4, 8)
print("input  std/mean:", x.std().item(), x.mean().item())
y = RMSNorm(8)(x)
print("output std/mean:", y.std().item(), y.mean().item())


# %% [markdown] color=sky title="4 · Rotary Position Embeddings (RoPE)"
# # 4 · Rotary Position Embeddings (RoPE)
#
# In the original Transformer (M19/M20), position info was *added* to the embeddings:
# `x[t] = token_emb[t] + pos_emb[t]`.
#
# RoPE does it differently: it **rotates** the Q and K vectors by an angle that depends on the position. The dot product `Q·K` now naturally encodes the *relative* position of the two tokens.
#
# Why care: better extrapolation to longer contexts than seen during training. Used everywhere now.


# %% color=mint title="Toy: 4 tokens"
# @explain: Toy: 4 tokens, 8-dim Q vectors
def precompute_rope(dim: int, seq_len: int, base: float = 10000.0):
    """Return cos and sin tables of shape (seq_len, dim/2) for RoPE."""
    inv_freq = 1.0 / (base ** (torch.arange(0, dim, 2).float() / dim))
    t = torch.arange(seq_len).float()
    freqs = torch.outer(t, inv_freq)               # (seq_len, dim/2)
    return freqs.cos(), freqs.sin()


def apply_rope(x, cos, sin):
    """Rotate every (x[..., 2i], x[..., 2i+1]) pair by the position's angle."""
    x1, x2 = x[..., 0::2], x[..., 1::2]
    return torch.stack([x1 * cos - x2 * sin,
                        x1 * sin + x2 * cos], dim=-1).flatten(-2)


# Toy: 4 tokens, 8-dim Q vectors
T, D = 4, 8
cos, sin = precompute_rope(D, T)
q = torch.randn(T, D)
q_rot = apply_rope(q, cos, sin)
print("q     shape:", q.shape)
print("q_rot shape:", q_rot.shape, " — same shape, different values")
print("\ndot(q[1], q[2]) before RoPE:", (q[1] @ q[2]).item())
print("dot(q[1], q[2]) after  RoPE:", (q_rot[1] @ q_rot[2]).item(),
      " ← now depends on positions 1 and 2")


# %% [markdown] color=peach title="5 · Multi-Latent Attention (MLA) — the killer feature"
# # 5 · Multi-Latent Attention (MLA) — the killer feature
#
# In standard MHA (M20), every token has Q, K, V of shape `(n_heads, head_dim)`. The **KV cache** during generation is `2 · n_layers · n_heads · head_dim` per token. For DeepSeek-V3 that would be huge.
#
# **MLA's trick:** project K and V down to a **shared 512-dim latent** before splitting into heads. Cache the latent (small), reconstruct K and V from it (cheap matmul). The cache shrinks ~5×.
#
# Schematically:
# ```
# …


# %% color=violet title="Q full size"
# @explain: Q full size; K/V go through a low-rank latent
class MLAToy(nn.Module):
    """A pedagogical Multi-Latent Attention module.

    Real DeepSeek splits the head dim into a 'no-position' (128) and 'rotary' (64) part
    and uses RoPE only on the rotary part. We omit those details here for clarity —
    the *latent compression* is the headline idea.
    """
    def __init__(self, dim, n_heads, kv_lora_rank=64):
        super().__init__()
        self.n_heads = n_heads
        self.head_dim = dim // n_heads
        self.scale = self.head_dim ** -0.5

        # Q full size; K/V go through a low-rank latent
        self.W_q  = nn.Linear(dim, dim, bias=False)
        self.W_dkv = nn.Linear(dim, kv_lora_rank, bias=False)   # DOWN
        self.W_uk = nn.Linear(kv_lora_rank, dim, bias=False)    # UP for K
        self.W_uv = nn.Linear(kv_lora_rank, dim, bias=False)    # UP for V
        self.W_o  = nn.Linear(dim, dim, bias=False)

    def forward(self, x):
        B, T, D = x.shape
        h, dh = self.n_heads, self.head_dim

        q = self.W_q(x).view(B, T, h, dh).transpose(1, 2)            # (B,h,T,dh)
        c_kv = self.W_dkv(x)                                          # (B, T, lora) — THIS is what gets cached
        k = self.W_uk(c_kv).view(B, T, h, dh).transpose(1, 2)         # reconstruct K
        v = self.W_uv(c_kv).view(B, T, h, dh).transpose(1, 2)         # reconstruct V

        scores = (q @ k.transpose(-2, -1)) * self.scale
        out = (F.softmax(scores, dim=-1) @ v).transpose(1, 2).contiguous().view(B, T, D)
        return self.W_o(out)


mla = MLAToy(dim=64, n_heads=4, kv_lora_rank=16)
x = torch.randn(2, 8, 64)
print("output:", mla(x).shape)
print("compressed cache per token:", 16, "values  vs full KV:", 2*64, "values   ← 8× reduction")


# %% [markdown] color=amber title="6 · Mixture-of-Experts (MoE) + Gate routing"
# # 6 · Mixture-of-Experts (MoE) + Gate routing
#
# In a vanilla transformer, every token passes through one big FFN. In MoE, every token passes through **a few small specialist FFNs (experts)** chosen dynamically by a router.
#
# DeepSeek's pattern (simplified):
# 1. **Gate** — a tiny linear layer scores all experts.
# 2. **Top-K** — pick the top `n_activated` experts per token.
# 3. **Combine** — weighted sum of those experts' outputs.


# %% color=rose title="SwiGLU: silu(w1(x)) * w3(x)  → w2"
# @explain: SwiGLU: silu(w1(x)) * w3(x)  → w2  — used in Llama, Mistral, DeepSeek
# @explain: 1) score every expert
# @explain: 2) keep only the top-k per token
# @explain: 3) dispatch + combine
class Expert(nn.Module):
    """A small FFN — one expert."""
    def __init__(self, dim, hidden):
        super().__init__()
        self.w1 = nn.Linear(dim, hidden, bias=False)
        self.w2 = nn.Linear(hidden, dim, bias=False)
        self.w3 = nn.Linear(dim, hidden, bias=False)
    def forward(self, x):
        # SwiGLU: silu(w1(x)) * w3(x)  → w2  — used in Llama, Mistral, DeepSeek
        return self.w2(F.silu(self.w1(x)) * self.w3(x))


class MoEToy(nn.Module):
    def __init__(self, dim, hidden, n_experts=8, top_k=2):
        super().__init__()
        self.experts = nn.ModuleList([Expert(dim, hidden) for _ in range(n_experts)])
        self.gate    = nn.Linear(dim, n_experts, bias=False)
        self.top_k   = top_k

    def forward(self, x):
        B, T, D = x.shape
        flat = x.reshape(-1, D)                          # (B·T, D)

        # 1) score every expert
        scores = self.gate(flat)                          # (N, n_experts)

        # 2) keep only the top-k per token
        top_w, top_i = scores.topk(self.top_k, dim=-1)    # both (N, k)
        top_w = F.softmax(top_w, dim=-1)                  # weights sum to 1 per token

        # 3) dispatch + combine
        out = torch.zeros_like(flat)
        for k in range(self.top_k):
            exp_idx_per_token = top_i[:, k]                # which expert each token goes to
            for e in range(len(self.experts)):
                mask = (exp_idx_per_token == e)
                if mask.any():
                    contrib = self.experts[e](flat[mask])
                    out[mask] += top_w[mask, k:k+1] * contrib
        return out.view(B, T, D)


moe = MoEToy(dim=32, hidden=64, n_experts=8, top_k=2)
print("MoE output:", moe(torch.randn(2, 4, 32)).shape)
print("\nWith 8 experts and top_k=2, only 25% of expert capacity fires per token.")


# %% [markdown] color=lime title="Production extras**"
# # Production extras**
#
# **Production extras** (in real `model.py` but skipped here for clarity):
# - **Shared experts** — a small set of FFNs that ALL tokens go through, on top of routed.
# - **Auxiliary-loss-free load balancing** — DeepSeek-V3's novelty: balance experts via a learned bias on the router scores, NOT via an extra loss term. Eliminates the trade-off between balance and accuracy.


# %% [markdown] color=teal title="7 · The full Block — putting it together"
# # 7 · The full Block — putting it together
#
# A DeepSeek transformer block:
# ```
# x → RMSNorm → MLA → + → x'             (attention sublayer with residual)
# x' → RMSNorm → MoE → + → x''           (FFN sublayer with residual)
# ```
# First few layers use a regular FFN instead of MoE (`n_dense_layers` in the config) — the early layers benefit less from specialisation.


# %% color=sky title="First few layers: dense FFN"
# @explain: First few layers: dense FFN
# @explain: A 4-layer mini DeepSeek (CPU-runnable in milliseconds)
class Block(nn.Module):
    def __init__(self, dim, n_heads, hidden, n_experts, top_k, layer_id, n_dense_layers=1):
        super().__init__()
        self.ln1  = RMSNorm(dim)
        self.attn = MLAToy(dim, n_heads, kv_lora_rank=dim // 4)
        self.ln2  = RMSNorm(dim)
        # First few layers: dense FFN. Later layers: MoE.
        if layer_id < n_dense_layers:
            self.ffn = Expert(dim, hidden)
        else:
            self.ffn = MoEToy(dim, hidden, n_experts=n_experts, top_k=top_k)

    def forward(self, x):
        x = x + self.attn(self.ln1(x))
        x = x + self.ffn (self.ln2(x))
        return x


# A 4-layer mini DeepSeek (CPU-runnable in milliseconds)
class TinyDeepSeek(nn.Module):
    def __init__(self, vocab_size=1000, dim=64, n_heads=4, hidden=128,
                 n_layers=4, n_experts=8, top_k=2, max_len=128):
        super().__init__()
        self.tok_emb = nn.Embedding(vocab_size, dim)
        self.pos_emb = nn.Embedding(max_len, dim)
        self.blocks  = nn.ModuleList([
            Block(dim, n_heads, hidden, n_experts, top_k, layer_id=i,
                  n_dense_layers=1) for i in range(n_layers)
        ])
        self.ln    = RMSNorm(dim)
        self.head  = nn.Linear(dim, vocab_size, bias=False)

    def forward(self, idx):
        B, T = idx.shape
        x = self.tok_emb(idx) + self.pos_emb(torch.arange(T))
        for blk in self.blocks: x = blk(x)
        return self.head(self.ln(x))


model = TinyDeepSeek()
out = model(torch.randint(0, 1000, (2, 16)))
print("logits :", out.shape)
print("params :", f"{sum(p.numel() for p in model.parameters()):,}")


# %% [markdown] color=mint title="8 · FP8 inference (`kernel.py`) — the speed trick"
# # 8 · FP8 inference (`kernel.py`) — the speed trick
#
# DeepSeek-V3 stores most weights in **FP8** (8-bit floats), not BF16/FP32. That:
#
# - Halves memory vs BF16 (a 671 B model fits in ~700 GB instead of 1.4 TB).
# - Halves matmul FLOPs.
# - Requires **per-block dynamic scaling** so values don't overflow.
#
# …


# %% color=peach title="def fake_fp8_quantize(x"
# @explain: Run this cell to see the output.
def fake_fp8_quantize(x, block_size=128):
    """Per-block dynamic quantisation (the idea behind kernel.py)."""
    n = x.numel()
    x = x.reshape(-1, block_size)
    scales = x.abs().amax(dim=-1, keepdim=True).clamp(min=1e-8)
    fp8_max = 448.0                                           # the largest representable FP8 value
    q = torch.clamp(x / scales * fp8_max, -fp8_max, fp8_max).round() / fp8_max
    return q, scales

def fake_fp8_dequantize(q, scales):
    return (q * scales).reshape(-1)


x = torch.randn(256)
q, scales = fake_fp8_quantize(x, block_size=128)
back = fake_fp8_dequantize(q, scales)
err = (x - back).abs().mean().item()
print(f"reconstruction error after 'FP8' round-trip: {err:.5f}   (small but nonzero)")


# %% [markdown] color=violet title="9 · The autoregressive loop — `generate.py`"
# # 9 · The autoregressive loop — `generate.py`
#
# Once weights are loaded, generation is a small loop. Here it is in spirit:


# %% color=amber title="Nucleus"
# @explain: Nucleus (top-p) sampling: keep the smallest set of tokens whose probability ≥ p
# @explain: sample one token
@torch.no_grad()
def generate(model, prompt_ids, max_new=20, temperature=1.0, top_p=0.9):
    """Greedy / nucleus sampling — the structure of generate.py simplified."""
    idx = prompt_ids                                       # (1, T)
    for _ in range(max_new):
        logits = model(idx)[:, -1, :]                       # only the LAST position matters
        logits = logits / temperature
        probs  = F.softmax(logits, dim=-1)

        # Nucleus (top-p) sampling: keep the smallest set of tokens whose probability ≥ p
        sorted_probs, sorted_idx = probs.sort(descending=True)
        cum = sorted_probs.cumsum(dim=-1)
        keep = cum <= top_p
        keep[..., 0] = True                                  # always keep at least one
        kept_probs = sorted_probs * keep
        kept_probs = kept_probs / kept_probs.sum(dim=-1, keepdim=True)

        # sample one token
        next_pos = torch.multinomial(kept_probs, num_samples=1)
        next_id  = sorted_idx.gather(-1, next_pos)

        idx = torch.cat([idx, next_id], dim=1)
    return idx


prompt = torch.randint(0, 1000, (1, 4))
out = generate(model, prompt, max_new=10)
print("prompt :", prompt.tolist())
print("output :", out.tolist())


# %% [markdown] color=rose title="Production extras**"
# # Production extras**
#
# **Production extras** (in the real `generate.py`):
# - **KV cache** — store the K and V from previous tokens so we don't recompute the whole sequence each step. Generation goes from O(T²) per token to O(T).
# - **Speculative decoding** with the Multi-Token-Prediction (MTP) head — generate several tokens in one forward and verify.
# - **Distributed sharding** across multiple GPUs.


# %% [markdown] color=lime title="10 · Reading the real source — a guided tour"
# # 10 · Reading the real source — a guided tour
#
# When you open `DeepSeek-V3/inference/model.py`, here's the order to read the classes in:
#
# | Read order | Class | What it does |
# |---|---|---|
# | 1 | `RMSNorm` | normalisation — the simplest piece |
# | 2 | `precompute_freqs_cis` + `apply_rotary_emb` | RoPE math |
# …


# %% [markdown] color=teal title="11 · Practice"
# # 11 · Practice
#
# 1. **Verify causality of MLAToy.** Mutate the LAST token of an input and confirm earlier outputs are unchanged. *(Hint: as written above, MLAToy is NOT causal — it's bidirectional. Add a triangular mask before the softmax to make it causal, then test.)*
# 2. **Plot the gate distribution.** Run `MoEToy` on a batch of random tokens. For each expert, count how many tokens chose it. Plot a bar chart — is the load balanced?
# 3. **Compare cache size.** With `dim=2048, n_heads=16, head_dim=128, kv_lora_rank=512`, compute and print the **per-token KV-cache size in floats** for (a) standard MHA and (b) MLA. Verify the ~5× reduction.
# 4. **Replace `MoEToy` with `Expert`** in the Block, run a forward, and compare: which has more params? Which produces visibly different outputs?


# %% color=sky title="1) Make MLA causal and verify"
# @explain: 1) Make MLA causal and verify
# @explain: 3) Cache size comparison
# 1) Make MLA causal and verify
class CausalMLAToy(MLAToy):
    def forward(self, x):
        B, T, D = x.shape
        h, dh = self.n_heads, self.head_dim
        q = self.W_q(x).view(B, T, h, dh).transpose(1, 2)
        c_kv = self.W_dkv(x)
        k = self.W_uk(c_kv).view(B, T, h, dh).transpose(1, 2)
        v = self.W_uv(c_kv).view(B, T, h, dh).transpose(1, 2)
        scores = (q @ k.transpose(-2, -1)) * self.scale
        mask = torch.tril(torch.ones(T, T)).view(1, 1, T, T)
        scores = scores.masked_fill(mask == 0, float("-inf"))
        out = (F.softmax(scores, dim=-1) @ v).transpose(1, 2).contiguous().view(B, T, D)
        return self.W_o(out)

m = CausalMLAToy(64, 4, 16).eval()
x = torch.randn(1, 5, 64)
y1 = m(x.clone())
xm = x.clone(); xm[:, -1] = torch.randn(64)
y2 = m(xm)
diff = (y1 - y2).abs().sum(dim=-1).squeeze().tolist()
print("max diff per pos:", [round(d, 4) for d in diff])
print("(positions 0-3 should be ~0)\n")

# 3) Cache size comparison
dim, n_heads, head_dim, kv_lora_rank = 2048, 16, 128, 512
mha_per_token  = 2 * n_heads * head_dim                # K + V across all heads
mla_per_token  = kv_lora_rank                          # just the latent
print(f"MHA per-token cache: {mha_per_token:>5}  floats")
print(f"MLA per-token cache: {mla_per_token:>5}  floats")
print(f"reduction: {mha_per_token / mla_per_token:.1f}×")


# %% [markdown] color=mint title="Recap"
# # Recap
#
# ✅ Read `ModelArgs` and identify which numbers make a model "MoE" or "MLA"
# ✅ Understand RMSNorm in 6 lines
# ✅ Know what RoPE does (rotation, not addition) and why it generalises better
# ✅ Implement a toy MLA and explain the KV-cache compression
# ✅ Implement a toy MoE with top-K routing
# ✅ Read a real DeepSeek block and trace data through it
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


