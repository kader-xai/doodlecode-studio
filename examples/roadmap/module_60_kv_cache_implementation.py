# doodlecode format-version: 2
# Auto-converted from module_60_kv_cache_implementation.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 60 Kv Cache Implementation"
# # Module 60 Kv Cache Implementation
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 60 — KV-Cache"
# # Module 60 — KV-Cache
#
# > M57's `generate()` re-runs the **whole prompt** through the model every time it produces a new token. Predicting token 1001 re-computes K and V for tokens 1..1000 from scratch. That's an O(N²) blunder we can fix with **memoisation**: cache the keys and values per layer per request, append the new K/V for each new token, and let attention re-use everything already computed. That's the **KV cache** — and it's why a real LLM serving stack can decode at 50 tokens/sec on hardware that would otherwise crawl.
#
# ### What you'll cover
# 1. The decode bottleneck — why naive `generate()` is O(N²) in tokens
# 2. The KV-cache insight — what stays constant between decode steps
# 3. **Modify `CausalMultiHeadAttention`** to accept + return a cache
# …


# %% [markdown] color=mint title="1 · The decode bottleneck"
# # 1 · The decode bottleneck
#
# Take a 200-token prompt and ask for 50 more tokens. The naive `generate()` (M57) calls the model **50 times**, each time feeding it `[prompt + already-generated-tokens]`. The model:
#
# - Step 1: forwards **201** tokens through 12 layers.
# - Step 2: forwards **202** tokens. (200 of those are *identical* to step 1!)
# - …
# - Step 50: forwards **250** tokens.
# …


# %% [markdown] color=peach title="2 · What stays constant"
# # 2 · What stays constant
#
# For a causal LM, **K and V at position `t` depend on token `t` alone** (modulo the weights). They don't change as we generate more tokens to the right.
#
# So the trick is:
# - **Pre-fill** the cache by running the prompt through the model **once**. Save the per-layer `(K, V)` tensors.
# - **Decode** one token at a time. For each step, send only the **new token** through; the attention block uses the *concatenation of the cached K/V and the new K/V*.


# %% [markdown] color=violet title="3 · `CausalMultiHeadAttention` with a cache"
# # 3 · `CausalMultiHeadAttention` with a cache
#


# %% color=amber title="!pip -q install torch tiktoken"
# @explain: Run this cell to see the output.
!pip -q install torch tiktoken


# %% color=rose title="Pre-build a large enough triangular mask once"
# @explain: Pre-build a large enough triangular mask once
# @explain: Attention over the *current* queries (T_new) against *all* keys (T_total)
# @explain: Causal mask: for query position q (within the LAST T_new slots), only attend to k ≤ q
# @explain: Build a per-step mask: query `q` (0-indexed in the new window) maps to absolute T_total-T_new+q
import torch, torch.nn as nn

class CausalMHA(nn.Module):
    def __init__(self, d_in, d_out, context_length, num_heads, dropout=0.0, qkv_bias=True):
        super().__init__()
        assert d_out % num_heads == 0
        self.d_out = d_out
        self.num_heads = num_heads
        self.head_dim  = d_out // num_heads
        self.W_q = nn.Linear(d_in, d_out, bias=qkv_bias)
        self.W_k = nn.Linear(d_in, d_out, bias=qkv_bias)
        self.W_v = nn.Linear(d_in, d_out, bias=qkv_bias)
        self.out_proj = nn.Linear(d_out, d_out)
        self.dropout = nn.Dropout(dropout)
        # Pre-build a large enough triangular mask once.
        self.register_buffer("mask",
            torch.triu(torch.ones(context_length, context_length), diagonal=1).bool())

    def forward(self, x, kv_cache=None):
        """
        x        : (B, T_new, D)              — T_new = full prompt during pre-fill, 1 during decode
        kv_cache : (k_past, v_past) or None   — each (B, H, T_past, head_dim)
        Returns (output, new_kv_cache).
        """
        B, T_new, _ = x.shape
        Q = self.W_q(x).view(B, T_new, self.num_heads, self.head_dim).transpose(1, 2)   # (B,H,T_new,Hd)
        K = self.W_k(x).view(B, T_new, self.num_heads, self.head_dim).transpose(1, 2)
        V = self.W_v(x).view(B, T_new, self.num_heads, self.head_dim).transpose(1, 2)

        if kv_cache is not None:
            K = torch.cat([kv_cache[0], K], dim=2)   # cat along T axis
            V = torch.cat([kv_cache[1], V], dim=2)

        T_total = K.shape[2]

        # Attention over the *current* queries (T_new) against *all* keys (T_total).
        attn = (Q @ K.transpose(-2, -1)) / (self.head_dim ** 0.5)        # (B,H,T_new,T_total)
        # Causal mask: for query position q (within the LAST T_new slots), only attend to k ≤ q.
        # Build a per-step mask: query `q` (0-indexed in the new window) maps to absolute T_total-T_new+q.
        causal = self.mask[T_total - T_new : T_total, :T_total]          # (T_new, T_total)
        attn = attn.masked_fill(causal, -torch.inf)
        attn = self.dropout(torch.softmax(attn, dim=-1))

        ctx = (attn @ V).transpose(1, 2).contiguous().view(B, T_new, self.d_out)
        return self.out_proj(ctx), (K, V)


# %% [markdown] color=lime title="The three changes vs M20"
# # The three changes vs M20
#
# **The three changes vs M20.**
# 1. `forward` takes an optional `kv_cache=(k_past, v_past)`.
# 2. We **concatenate** the new K/V onto the cached ones along the time axis.
# 3. We return the **updated cache** so the caller can pass it back in.
#
# Everything else — the heads, the scaling, the output projection — is unchanged.


# %% [markdown] color=teal title="4 · A tiny model that uses the cache"
# # 4 · A tiny model that uses the cache
#


# %% color=sky title="class TinyBlock(nn.Module)"
# @explain: Run this cell to see the output.
class TinyBlock(nn.Module):
    def __init__(self, cfg):
        super().__init__()
        self.attn = CausalMHA(cfg["d"], cfg["d"], cfg["ctx"], cfg["h"])
        self.ff   = nn.Sequential(nn.Linear(cfg["d"], 4*cfg["d"]), nn.GELU(), nn.Linear(4*cfg["d"], cfg["d"]))
        self.n1   = nn.LayerNorm(cfg["d"])
        self.n2   = nn.LayerNorm(cfg["d"])
    def forward(self, x, kv_cache=None):
        a, new_kv = self.attn(self.n1(x), kv_cache=kv_cache)
        x = x + a
        x = x + self.ff(self.n2(x))
        return x, new_kv

class TinyGPT(nn.Module):
    def __init__(self, cfg):
        super().__init__()
        self.tok = nn.Embedding(cfg["vocab"], cfg["d"])
        self.pos = nn.Embedding(cfg["ctx"], cfg["d"])
        self.blocks = nn.ModuleList([TinyBlock(cfg) for _ in range(cfg["n_layers"])])
        self.norm = nn.LayerNorm(cfg["d"])
        self.head = nn.Linear(cfg["d"], cfg["vocab"], bias=False)
        self.head.weight = self.tok.weight    # tying (M56)
        self.ctx = cfg["ctx"]

    def forward(self, idx, kv_caches=None, pos_offset=0):
        B, T_new = idx.shape
        x = self.tok(idx) + self.pos(torch.arange(pos_offset, pos_offset + T_new, device=idx.device))
        new_caches = []
        for i, blk in enumerate(self.blocks):
            cache = None if kv_caches is None else kv_caches[i]
            x, new_kv = blk(x, kv_cache=cache)
            new_caches.append(new_kv)
        return self.head(self.norm(x)), new_caches

cfg = {"vocab": 50257, "ctx": 512, "d": 128, "h": 4, "n_layers": 4}
torch.manual_seed(0)
model = TinyGPT(cfg)
print(f"params: {sum(p.numel() for p in model.parameters()):,}")


# %% [markdown] color=mint title="Two things worth pointing out"
# # Two things worth pointing out
#
# Two things worth pointing out:
# - `kv_caches` is a **list of per-layer (K, V) tuples**. Layer `i` has its own cache.
# - `pos_offset` tells `pos_emb` how far along we already are — so the new token gets the correct positional embedding (otherwise it'd always be position 0).


# %% [markdown] color=peach title="5 · `generate_with_cache` — pre-fill once, then decode one-at-a-time"
# # 5 · `generate_with_cache` — pre-fill once, then decode one-at-a-time
#


# %% color=violet title="PRE-FILL: run the whole prompt once and capture caches"
# @explain: PRE-FILL: run the whole prompt once and capture caches
# @explain: DECODE: feed only the most recent 1 token + the cache
@torch.no_grad()
def generate_naive(model, idx, max_new_tokens):
    """M57-style: re-runs the whole prefix every step."""
    for _ in range(max_new_tokens):
        logits, _ = model(idx)                         # full pass, no cache
        next_id = torch.argmax(logits[:, -1, :], dim=-1, keepdim=True)
        idx = torch.cat([idx, next_id], dim=1)
    return idx

@torch.no_grad()
def generate_with_cache(model, idx, max_new_tokens):
    """Pre-fill once on the prompt, then decode one new token at a time using the cache."""
    # PRE-FILL: run the whole prompt once and capture caches
    logits, caches = model(idx, kv_caches=None, pos_offset=0)
    next_id = torch.argmax(logits[:, -1, :], dim=-1, keepdim=True)
    out = torch.cat([idx, next_id], dim=1)

    pos = idx.shape[1]
    for _ in range(max_new_tokens - 1):
        # DECODE: feed only the most recent 1 token + the cache
        logits, caches = model(next_id, kv_caches=caches, pos_offset=pos)
        next_id = torch.argmax(logits[:, -1, :], dim=-1, keepdim=True)
        out = torch.cat([out, next_id], dim=1)
        pos += 1
    return out


# %% [markdown] color=amber title="6 · Benchmark — how much faster is it?"
# # 6 · Benchmark — how much faster is it?
#


# %% color=rose title="import time"
# @explain: Run this cell to see the output.
import time, tiktoken
tok = tiktoken.get_encoding("gpt2")
prompt = tok.encode("The quick brown fox jumps over the lazy dog. " * 20)[:200]
ctx_ids = torch.tensor(prompt).unsqueeze(0)
print("prompt length:", ctx_ids.shape[1])

def bench(fn, name, repeat=3, **kw):
    times = []
    for _ in range(repeat):
        t = time.time(); _ = fn(model, ctx_ids, **kw); times.append(time.time() - t)
    return name, min(times)

n, t_naive  = bench(generate_naive,      "naive",      max_new_tokens=50)
n, t_cached = bench(generate_with_cache, "cached",     max_new_tokens=50)
print(f"naive  : {t_naive:.3f}s   ({50/t_naive:.1f} tok/s)")
print(f"cached : {t_cached:.3f}s   ({50/t_cached:.1f} tok/s)")
print(f"speedup: {t_naive/t_cached:.2f}×")


# %% [markdown] color=lime title="On this tiny (4-layer × 128-dim) model and a…"
# # On this tiny (4-layer × 128-dim) model and a…
#
# On this tiny (4-layer × 128-dim) model and a 200-token prompt the cached version is ~**1.5–3× faster** even on CPU. On a real GPT-2 124M with a 1 024-token prompt and 200 tokens generated, it's ~**10–20× faster** — and the gap widens with longer contexts (the savings scale with prompt length).
#
# **Sanity check.** Both versions should produce the same output sequence:


# %% color=teal title="ids1 = generate_naive(model"
# @explain: Run this cell to see the output.
ids1 = generate_naive(model, ctx_ids, max_new_tokens=10)
ids2 = generate_with_cache(model, ctx_ids, max_new_tokens=10)
print("match:", torch.equal(ids1, ids2))


# %% [markdown] color=sky title="7 · Memory math — the cost you pay for that speedup"
# # 7 · Memory math — the cost you pay for that speedup
#
# The KV cache trades **compute** for **VRAM**. Per request, per layer, per head:
#
# $$\text{KV bytes} = 2 \times n_\text{layers} \times n_\text{kv\_heads} \times \text{head\_dim} \times T \times \text{bytes-per-elem}$$
#
# The `2×` is because we cache **K** *and* **V**. For a Llama-3-8B (n_layers=32, n_kv_heads=8, head_dim=128) at fp16:
#
# …


# %% color=mint title="def kv_cache_bytes_per_token(n_layers"
# @explain: Run this cell to see the output.
def kv_cache_bytes_per_token(n_layers, n_kv_heads, head_dim, dtype_bytes=2):
    return 2 * n_layers * n_kv_heads * head_dim * dtype_bytes

def kv_cache_bytes(n_layers, n_kv_heads, head_dim, ctx_tokens, dtype_bytes=2, n_requests=1):
    return kv_cache_bytes_per_token(n_layers, n_kv_heads, head_dim, dtype_bytes) * ctx_tokens * n_requests

print(f"Llama-3-8B @ 8K ctx, fp16, 1 req  : {kv_cache_bytes(32,  8, 128, 8192) / 1e9:>6.2f} GB")
print(f"Llama-3-8B @ 8K ctx, fp16, 32 req : {kv_cache_bytes(32,  8, 128, 8192, n_requests=32) / 1e9:>6.2f} GB")
print(f"GPT-2 124M @ 1K ctx, fp16, 1 req  : {kv_cache_bytes(12, 12,  64, 1024) / 1e6:>6.2f} MB")


# %% [markdown] color=peach title="This is the entire reason `vLLM` exists.** A naive…"
# # This is the entire reason `vLLM` exists.** A naive…
#
# **This is the entire reason `vLLM` exists.** A naive cache allocates one fixed-size buffer per request sized to the *maximum* possible output. If most requests finish early, ~90% of that VRAM is empty. **PagedAttention** (M44 §1) chops the cache into 16-token pages and allocates on demand — same speed, 3–5× more concurrent requests fit.


# %% [markdown] color=violet title="8 · Cache + sampling"
# # 8 · Cache + sampling
#
# Temperature, top-k, top-p — none of them touch the K/V cache. They live in the sampling step on the **logits**. Drop our M57 sampler in place of the `argmax` and you have a proper cached sampler:


# %% color=amber title="def top_k_filter(logits"
# @explain: Run this cell to see the output.
def top_k_filter(logits, k):
    if k is None or k <= 0: return logits
    v, _ = torch.topk(logits, k)
    return torch.where(logits < v[..., -1, None], torch.tensor(-float("inf"), device=logits.device), logits)

@torch.no_grad()
def generate_sampled_with_cache(model, idx, max_new_tokens, temperature=0.8, top_k=50, eos_id=None):
    logits, caches = model(idx, kv_caches=None, pos_offset=0)
    pos = idx.shape[1]
    def sample(last_logits):
        last_logits = top_k_filter(last_logits, top_k)
        probs = torch.softmax(last_logits / max(temperature, 1e-6), dim=-1)
        return torch.multinomial(probs, num_samples=1)

    next_id = sample(logits[:, -1, :])
    out = torch.cat([idx, next_id], dim=1)
    for _ in range(max_new_tokens - 1):
        logits, caches = model(next_id, kv_caches=caches, pos_offset=pos)
        next_id = sample(logits[:, -1, :])
        if eos_id is not None and (next_id == eos_id).all(): break
        out = torch.cat([out, next_id], dim=1); pos += 1
    return out

torch.manual_seed(7)
print(tok.decode(generate_sampled_with_cache(model, ctx_ids, max_new_tokens=15)[0].tolist()))


# %% [markdown] color=rose title="The sampler is a thin slice on top of the model.**…"
# # The sampler is a thin slice on top of the model.**…
#
# **The sampler is a thin slice on top of the model.** Cache or no cache, the logic is identical — that's why every serving stack can swap their sampler without re-validating the model.


# %% [markdown] color=lime title="9 · vLLM and **PagedAttention** (M44 connection)"
# # 9 · vLLM and **PagedAttention** (M44 connection)
#
# What we built here is a **per-request** cache. Production needs much more:
#
# | Limitation we have | What vLLM (M44) does |
# |---|---|
# | One contiguous KV buffer per request, sized for max output | **PagedAttention**: chop the cache into 16-token *pages*, allocate on demand |
# | Cache lives in the Python object — process restart loses it | KV cache lives in a dedicated CUDA allocator |
# …


# %% [markdown] color=teal title="10 · The frontier — speculative decoding, GQA, MLA, SWA"
# # 10 · The frontier — speculative decoding, GQA, MLA, SWA
#
# After you have KV-caching, the next four wins come from **using the cache more cleverly**:
#
# | Technique | What it does |
# |---|---|
# | **Speculative decoding** (M44 §9) | A tiny draft model proposes `k` tokens; the big model verifies them in **one** forward pass against the cache. 1.5–3× decode speedup. |
# | **GQA (Grouped-Query Attention)** | Many query heads share *one* KV head → KV cache shrinks `n_heads / n_kv_heads`×. Llama-3 / Qwen2 / Mistral. M61 covers this. |
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


