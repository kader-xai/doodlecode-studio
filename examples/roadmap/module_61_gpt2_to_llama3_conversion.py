# doodlecode format-version: 2
# Auto-converted from module_61_gpt2_to_llama3_conversion.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 61 Gpt2 To Llama3 Conversion"
# # Module 61 Gpt2 To Llama3 Conversion
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 61 — GPT-2 → Llama 3"
# # Module 61 — GPT-2 → Llama 3
#
# > M56 built **GPT-2 124M**. Every modern LLM — Llama, Qwen, Mistral, DeepSeek, Gemma — is *almost* the same architecture, with four well-known swaps. This module performs each swap in code, on top of the M56 model, and ends with **Llama 3.2-1B weights loaded into your converted stack** producing real text.
#
# ### The four swaps
#
# | Component | GPT-2 (2019) | Llama-style (2023→) |
# |---|---|---|
# …


# %% [markdown] color=mint title="1 · The four swaps"
# # 1 · The four swaps
#
# - **RMSNorm** — Pre-Norm 2.0. Drops the mean centring; just RMS-divide and scale. Trains as well, half the math, fewer FLOPs.
# - **RoPE** — instead of *adding* a positional vector to embeddings, **rotate** the query and key vectors by an angle proportional to position. The dot product `q_i · k_j` then implicitly encodes `i − j`. Composable; works with KV cache; extrapolates better.
# - **SwiGLU** — replace the GELU two-matrix MLP with a **gated** three-matrix MLP. Empirically nicer training curves; standard since PaLM.
# - **GQA (Grouped-Query Attention)** — many query heads share a single KV head. KV cache shrinks `n_heads / n_kv_heads`× — the *single* biggest reason a Llama-3 8B can serve 32K-token contexts on one GPU.


# %% [markdown] color=peach title="2 · RMSNorm"
# # 2 · RMSNorm
#


# %% color=violet title="!pip -q install torch tiktoken huggingface_hub…"
# @explain: Run this cell to see the output.
!pip -q install torch tiktoken huggingface_hub safetensors


# %% color=amber title="rsqrt(mean(x^2) + eps)  →  x / sqrt(mean(x^2) + eps)"
# @explain: rsqrt(mean(x^2) + eps)  →  x / sqrt(mean(x^2) + eps)
import torch, torch.nn as nn

class RMSNorm(nn.Module):
    """Llama's RMSNorm — no mean centring, no bias. Only RMS-divide + a learnable scale."""
    def __init__(self, d, eps=1e-5):
        super().__init__()
        self.eps = eps
        self.weight = nn.Parameter(torch.ones(d))   # gamma; no beta

    def forward(self, x):
        # rsqrt(mean(x^2) + eps)  →  x / sqrt(mean(x^2) + eps)
        rms = torch.rsqrt(x.pow(2).mean(dim=-1, keepdim=True) + self.eps)
        return self.weight * (x * rms)


# %% [markdown] color=rose title="Why this works.** The mean term in LayerNorm exists…"
# # Why this works.** The mean term in LayerNorm exists…
#
# **Why this works.** The mean term in LayerNorm exists to centre activations. Empirically, transformers don't need centring at the LN step — the residual stream handles drift on its own. RMSNorm is one fewer matrix operation per token per layer × `2 × n_layers` LNs per block = ~5-10% wall-clock win.


# %% [markdown] color=lime title="3 · RoPE — rotary positional embeddings"
# # 3 · RoPE — rotary positional embeddings
#
# RoPE rotates each pair of dimensions in the Q/K vector by an angle `θ_d · m` where `m` is the position and `θ_d` is a per-dim base frequency.
#
# $$\theta_d = 10000^{-2d/D}$$
#
# For position `m`, dimension pair `(2d, 2d+1)`:
#
# …


# %% color=teal title="split each head_dim into two halves and rotate them as"
# @explain: split each head_dim into two halves and rotate them as (real, imag) pairs
# @explain: tiny demo
def precompute_rope_freqs(head_dim, max_seq_len, base=10_000.0, device="cpu"):
    """Returns (cos, sin) tables of shape (max_seq_len, head_dim//2)."""
    inv_freq = 1.0 / (base ** (torch.arange(0, head_dim, 2, device=device).float() / head_dim))
    t = torch.arange(max_seq_len, device=device).float()
    freqs = torch.outer(t, inv_freq)                    # (T, head_dim/2)
    return freqs.cos(), freqs.sin()

def apply_rope(x, cos, sin):
    """x: (B, H, T, head_dim).  cos,sin: (T, head_dim/2).  Returns rotated x."""
    # split each head_dim into two halves and rotate them as (real, imag) pairs
    x1, x2 = x[..., : x.shape[-1] // 2], x[..., x.shape[-1] // 2 :]
    cos = cos[None, None, : x.shape[-2], :]            # broadcast to (1,1,T,head_dim/2)
    sin = sin[None, None, : x.shape[-2], :]
    return torch.cat([x1 * cos - x2 * sin,
                      x1 * sin + x2 * cos], dim=-1)

# tiny demo
cos, sin = precompute_rope_freqs(head_dim=8, max_seq_len=4)
q = torch.randn(1, 2, 4, 8)                            # (B=1, H=2, T=4, head_dim=8)
print("rotated q[0,0,0,:]:", apply_rope(q, cos, sin)[0, 0, 0])


# %% [markdown] color=sky title="Two practical notes"
# # Two practical notes
#
# **Two practical notes.**
# - The `(cos, sin)` tables are **precomputed** once (or extended with the context length). They're not learned.
# - Llama-3 uses `base=500_000` (extended from 10 000) which yields a longer effective context window without changing the model.


# %% [markdown] color=mint title="4 · SwiGLU — gated MLP"
# # 4 · SwiGLU — gated MLP
#


# %% color=peach title="class SwiGLU(nn.Module)"
# @explain: Run this cell to see the output.
class SwiGLU(nn.Module):
    """Llama-style gated MLP: (silu(x W_gate) ⊙ x W_up) → W_down"""
    def __init__(self, d_model, d_ff, bias=False):
        super().__init__()
        self.w_gate = nn.Linear(d_model, d_ff, bias=bias)
        self.w_up   = nn.Linear(d_model, d_ff, bias=bias)
        self.w_down = nn.Linear(d_ff,    d_model, bias=bias)

    def forward(self, x):
        return self.w_down(torch.nn.functional.silu(self.w_gate(x)) * self.w_up(x))


# %% [markdown] color=violet title="The shape change.** GPT-2's FFN has **2** matrices:…"
# # The shape change.** GPT-2's FFN has **2** matrices:…
#
# **The shape change.** GPT-2's FFN has **2** matrices: `(d_model → 4·d_model)` then `(4·d_model → d_model)`. SwiGLU has **3** matrices and chooses `d_ff` differently (usually `~2/3 × 4·d_model ≈ 2.66·d_model` so total params match GPT-2's 4× FFN). The extra parameter count buys the **gating** signal — `silu(...)` is the *gate* and the second matrix is the *content* — and that consistently improves training quality.


# %% [markdown] color=amber title="5 · GQA — Grouped-Query Attention"
# # 5 · GQA — Grouped-Query Attention
#


# %% color=rose title="RoPE on Q and K only"
# @explain: RoPE on Q and K only (NOT V)
# @explain: repeat KV heads so they line up with Q heads
class GQA(nn.Module):
    def __init__(self, d_model, n_heads, n_kv_heads, max_seq_len, rope_base=500_000.0):
        super().__init__()
        assert n_heads % n_kv_heads == 0
        self.h_q  = n_heads
        self.h_kv = n_kv_heads
        self.hd   = d_model // n_heads
        self.group = n_heads // n_kv_heads          # how many Q heads share one KV head

        self.W_q = nn.Linear(d_model, n_heads    * self.hd, bias=False)
        self.W_k = nn.Linear(d_model, n_kv_heads * self.hd, bias=False)   # <-- shrunk
        self.W_v = nn.Linear(d_model, n_kv_heads * self.hd, bias=False)
        self.W_o = nn.Linear(d_model, d_model, bias=False)

        cos, sin = precompute_rope_freqs(self.hd, max_seq_len, base=rope_base)
        self.register_buffer("rope_cos", cos)
        self.register_buffer("rope_sin", sin)
        self.register_buffer("mask", torch.triu(torch.ones(max_seq_len, max_seq_len), diagonal=1).bool())

    def forward(self, x):
        B, T, _ = x.shape
        Q = self.W_q(x).view(B, T, self.h_q,  self.hd).transpose(1, 2)
        K = self.W_k(x).view(B, T, self.h_kv, self.hd).transpose(1, 2)
        V = self.W_v(x).view(B, T, self.h_kv, self.hd).transpose(1, 2)

        # RoPE on Q and K only (NOT V)
        Q = apply_rope(Q, self.rope_cos, self.rope_sin)
        K = apply_rope(K, self.rope_cos, self.rope_sin)

        # repeat KV heads so they line up with Q heads
        K = K.repeat_interleave(self.group, dim=1)
        V = V.repeat_interleave(self.group, dim=1)

        attn = (Q @ K.transpose(-2, -1)) / (self.hd ** 0.5)
        attn = attn.masked_fill(self.mask[:T, :T], -torch.inf)
        attn = torch.softmax(attn, dim=-1)
        out  = (attn @ V).transpose(1, 2).contiguous().view(B, T, -1)
        return self.W_o(out)


# %% [markdown] color=lime title="What's new vs M56's `MultiHeadAttention`"
# # What's new vs M56's `MultiHeadAttention`
#
# **What's new vs M56's `MultiHeadAttention`.**
# 1. `W_k` and `W_v` project to **`n_kv_heads × head_dim`**, *not* `n_heads × head_dim`. That's the KV cache shrink.
# 2. **RoPE is applied to Q and K**, not V. (V doesn't need positional information — the softmax already weighted its mixing.)
# 3. We `repeat_interleave` the KV heads so the shapes line up at the dot product.
# 4. No QKV bias (Llama dropped it).
#
# For Llama-3-8B: `n_heads=32, n_kv_heads=8`. KV cache is **4× smaller** than a vanilla MHA model of the same size. That's why an 8B model holds 32K context on a single GPU.


# %% [markdown] color=teal title="6 · `LlamaBlock` — pre-norm + RMSNorm + GQA + SwiGLU"
# # 6 · `LlamaBlock` — pre-norm + RMSNorm + GQA + SwiGLU
#


# %% color=sky title="class LlamaBlock(nn.Module)"
# @explain: Run this cell to see the output.
class LlamaBlock(nn.Module):
    def __init__(self, cfg):
        super().__init__()
        self.n1   = RMSNorm(cfg["d"])
        self.attn = GQA(cfg["d"], cfg["n_heads"], cfg["n_kv_heads"], cfg["ctx"], cfg["rope_base"])
        self.n2   = RMSNorm(cfg["d"])
        self.mlp  = SwiGLU(cfg["d"], cfg["d_ff"])

    def forward(self, x):
        x = x + self.attn(self.n1(x))     # pre-norm residual (same shape as M56)
        x = x + self.mlp(self.n2(x))
        return x


# %% [markdown] color=mint title="Look at the diff vs M56's `TransformerBlock`.**…"
# # Look at the diff vs M56's `TransformerBlock`.**…
#
# **Look at the diff vs M56's `TransformerBlock`.** Same control flow, same pre-norm, same residual. Every change is *inside* a sub-module:
#
# | | M56 | M61 |
# |---|---|---|
# | `n1`, `n2` | `LayerNorm` | `RMSNorm` |
# | `attn` | `MultiHeadAttention` | `GQA` (with RoPE) |
# | `mlp` | `GELU(W₁·x)·W₂` | `SwiGLU(x)` |
#
# …


# %% [markdown] color=peach title="7 · The `LlamaModel`"
# # 7 · The `LlamaModel`
#


# %% color=violet title="Llama-3 does NOT tie input/output embeddings"
# @explain: Llama-3 does NOT tie input/output embeddings (different from GPT-2)
# @explain: A Llama-3.2-1B sized config (16 layers · d_model 2048 · n_heads 32 · n_kv_heads 8)
# @explain: don't actually instantiate at 1B params in Colab unless you have a GPU — just inspect the spec
class LlamaModel(nn.Module):
    def __init__(self, cfg):
        super().__init__()
        self.embed_tokens = nn.Embedding(cfg["vocab"], cfg["d"])
        self.layers = nn.ModuleList([LlamaBlock(cfg) for _ in range(cfg["n_layers"])])
        self.norm   = RMSNorm(cfg["d"])
        self.lm_head = nn.Linear(cfg["d"], cfg["vocab"], bias=False)
        # Llama-3 does NOT tie input/output embeddings (different from GPT-2)
    def forward(self, idx):
        x = self.embed_tokens(idx)
        for layer in self.layers:
            x = layer(x)
        return self.lm_head(self.norm(x))

# A Llama-3.2-1B sized config (16 layers · d_model 2048 · n_heads 32 · n_kv_heads 8)
CFG_LLAMA_1B = {
    "vocab": 128_256,        # Llama-3 BPE
    "ctx":   2048,            # demo cap — real model: 131K
    "d":     2048,
    "n_heads": 32,
    "n_kv_heads": 8,
    "n_layers": 16,
    "d_ff": 8192,
    "rope_base": 500_000.0,
}
torch.manual_seed(0)
# don't actually instantiate at 1B params in Colab unless you have a GPU — just inspect the spec
print(CFG_LLAMA_1B)


# %% [markdown] color=amber title="Three more Llama-3 specifics** the spec captures"
# # Three more Llama-3 specifics** the spec captures
#
# **Three more Llama-3 specifics** the spec captures:
# - `vocab = 128_256` (vs GPT-2's 50 257). Llama uses a larger BPE so each token covers more characters on average — fewer tokens per document.
# - `n_kv_heads = 8` while `n_heads = 32` → GQA with group size 4.
# - Embeddings are **not tied** to the LM head (Llama trains both separately). That's a small Llama-vs-GPT-2 inconsistency to know about when loading weights.


# %% [markdown] color=rose title="8 · Load Llama-3.2-1B weights"
# # 8 · Load Llama-3.2-1B weights
#
# Real models live on Hugging Face. Llama-3.2-1B-Instruct is gated — you must accept the licence once on the HF page, then `huggingface_hub` will let you download it.
#
# ```python
# from huggingface_hub import snapshot_download
# from safetensors.torch import load_file
# import json, pathlib
# …


# %% color=lime title="def load_llama_weights(model"
# @explain: Run this cell to see the output.
def load_llama_weights(model, state, cfg):
    model.embed_tokens.weight.data.copy_(state["model.embed_tokens.weight"])
    for i, layer in enumerate(model.layers):
        p = f"model.layers.{i}"
        layer.n1.weight.data.copy_(state[f"{p}.input_layernorm.weight"])
        layer.n2.weight.data.copy_(state[f"{p}.post_attention_layernorm.weight"])
        layer.attn.W_q.weight.data.copy_(state[f"{p}.self_attn.q_proj.weight"])
        layer.attn.W_k.weight.data.copy_(state[f"{p}.self_attn.k_proj.weight"])
        layer.attn.W_v.weight.data.copy_(state[f"{p}.self_attn.v_proj.weight"])
        layer.attn.W_o.weight.data.copy_(state[f"{p}.self_attn.o_proj.weight"])
        layer.mlp.w_gate.weight.data.copy_(state[f"{p}.mlp.gate_proj.weight"])
        layer.mlp.w_up.weight.data.copy_(state[f"{p}.mlp.up_proj.weight"])
        layer.mlp.w_down.weight.data.copy_(state[f"{p}.mlp.down_proj.weight"])
    model.norm.weight.data.copy_(state["model.norm.weight"])
    model.lm_head.weight.data.copy_(state["lm_head.weight"])
    return model
print("loader defined — call load_llama_weights(model, state, CFG_LLAMA_1B)")


# %% [markdown] color=teal title="Notice what's *missing* compared to M56's loader"
# # Notice what's *missing* compared to M56's loader
#
# **Notice what's *missing* compared to M56's loader.**
# - No transpose. HF's state-dict is *already* PyTorch (out, in) shape — no TF re-shaping.
# - No fused-matrix split. Q / K / V are stored separately.
# - No re-tying of the LM head. Llama-3 trains it separately from `embed_tokens`.
#
# That's why HF's official models are easier to host than re-implementing from a TF dump.


# %% [markdown] color=sky title="9 · Generate"
# # 9 · Generate
#


# %% color=mint title="(Conceptual"
# @explain: (Conceptual — you'd use the AutoTokenizer that ships with the model)
# @explain: from transformers import AutoTokenizer
# @explain: tok = AutoTokenizer.from_pretrained("meta-llama/Llama-3.2-1B")
# @explain: ids = tok("The capital of France is", return_tensors="pt").input_ids
# @explain: # Reuse M57's generate() with EOS = tok.eos_token_id (128009 for Llama-3 instruct)
# (Conceptual — you'd use the AutoTokenizer that ships with the model)
# from transformers import AutoTokenizer
# tok = AutoTokenizer.from_pretrained("meta-llama/Llama-3.2-1B")
# ids = tok("The capital of France is", return_tensors="pt").input_ids
#
# # Reuse M57's generate() with EOS = tok.eos_token_id (128009 for Llama-3 instruct)
# out = generate(model, ids, max_new=20, context_size=CFG_LLAMA_1B["ctx"], temperature=0.7, top_k=50)
# print(tok.decode(out[0]))
print("With the cache from M60 this runs ~10× faster on the same hardware as the naive loop.")


# %% [markdown] color=peach title="You now have a working Llama 3.2-1B.** The…"
# # You now have a working Llama 3.2-1B.** The…
#
# **You now have a working Llama 3.2-1B.** The architecture you wrote, the weights you loaded, generating real text. Add the KV cache from M60 and you have a serviceable inference engine in pure PyTorch.


# %% [markdown] color=violet title="10 · The bigger picture — what else changes"
# # 10 · The bigger picture — what else changes
#
# Beyond the four swaps, the Llama family ecosystem has a few more flavours:
#
# | Family | Extra trick |
# |---|---|
# | **Llama 3 / Qwen 2.5 / Mistral 7B** | GQA + SwiGLU + RoPE (what we built) |
# | **Mixtral / Qwen-MoE / DeepSeek-MoE** | **MoE FFN** — replace the SwiGLU with `n_experts` SwiGLUs + a learned router; only `top_k` experts run per token. Compute is constant; parameter count balloons. (M24 covered MoE conceptually.) |
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


