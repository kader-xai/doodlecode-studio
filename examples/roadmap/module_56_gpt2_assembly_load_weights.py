# doodlecode format-version: 2
# Auto-converted from module_56_gpt2_assembly_load_weights.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 56 Gpt2 Assembly Load Weights"
# # Module 56 Gpt2 Assembly Load Weights
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 56 — Real GPT-2 124M"
# # Module 56 — Real GPT-2 124M
#
# > M55 fed text in. Now we **build the full GPT-2 124M model** (the smallest of OpenAI's 2019 GPT-2 release) at the exact spec, then **download OpenAI's pretrained weights** and load them into our own PyTorch code. By the end of this notebook, **your hand-coded transformer generates real GPT-2 text** — the single most satisfying moment in the entire course.
#
# ### What you'll cover
# 1. The `GPT_CONFIG_124M` spec (and what each number means)
# 2. `LayerNorm`, `GELU`, `FeedForward(4×)` — the GPT-2 block ingredients
# 3. `MultiHeadAttention` — production form with `c_attn` (fused QKV)
# …


# %% [markdown] color=mint title="1 · The `GPT_CONFIG_124M` spec"
# # 1 · The `GPT_CONFIG_124M` spec
#


# %% color=peach title="GPT_CONFIG_124M = {"
# @explain: Run this cell to see the output.
GPT_CONFIG_124M = {
    "vocab_size":     50_257,   # BPE vocab (M55, tiktoken gpt2)
    "context_length": 1_024,    # max positional embeddings
    "emb_dim":        768,      # d_model
    "n_heads":        12,       # multi-head count
    "n_layers":       12,       # transformer blocks
    "drop_rate":      0.1,
    "qkv_bias":       True,     # GPT-2 uses bias on QKV; Llama doesn't
}
print(GPT_CONFIG_124M)


# %% [markdown] color=violet title="Where each number lives"
# # Where each number lives
#
# **Where each number lives.**
# - `vocab_size` → row count of `tok_emb` and `lm_head`.
# - `context_length` → row count of `pos_emb` (training never exceeds this).
# - `emb_dim` → `d_model`; each token is a 768-d vector through the stack.
# - `n_heads`: 12 heads × 64 dims per head = 768.
# - `n_layers`: 12 transformer blocks stacked.
# - `qkv_bias=True`: a small but **load-bearing** detail when matching the OpenAI checkpoint.


# %% [markdown] color=amber title="2 · `LayerNorm`, `GELU`, `FeedForward(4×)`"
# # 2 · `LayerNorm`, `GELU`, `FeedForward(4×)`
#


# %% color=rose title="!pip -q install tiktoken torch tensorflow"
# @explain: Run this cell to see the output.
!pip -q install tiktoken torch tensorflow


# %% color=lime title="import torch"
# @explain: Run this cell to see the output.
import torch, torch.nn as nn

class LayerNorm(nn.Module):
    def __init__(self, emb_dim):
        super().__init__()
        self.eps = 1e-5
        self.scale = nn.Parameter(torch.ones(emb_dim))
        self.shift = nn.Parameter(torch.zeros(emb_dim))
    def forward(self, x):
        mean = x.mean(dim=-1, keepdim=True)
        var  = x.var(dim=-1, keepdim=True, unbiased=False)
        return self.scale * (x - mean) / torch.sqrt(var + self.eps) + self.shift


# %% color=teal title="The tanh-approximation of GELU used by GPT-2"
# @explain: The tanh-approximation of GELU used by GPT-2 (faster than torch.erf-based)
class GELU(nn.Module):
    # The tanh-approximation of GELU used by GPT-2 (faster than torch.erf-based)
    def forward(self, x):
        return 0.5 * x * (
            1 + torch.tanh(
                torch.sqrt(torch.tensor(2.0 / torch.pi)) *
                (x + 0.044715 * x ** 3)
            )
        )

class FeedForward(nn.Module):
    def __init__(self, cfg):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(cfg["emb_dim"], 4 * cfg["emb_dim"]),
            GELU(),
            nn.Linear(4 * cfg["emb_dim"], cfg["emb_dim"]),
        )
    def forward(self, x):
        return self.layers(x)


# %% [markdown] color=sky title="GPT-2's FFN is the classic **expand → activate →…"
# # GPT-2's FFN is the classic **expand → activate →…
#
# GPT-2's FFN is the classic **expand → activate → contract** pattern: `d_model → 4·d_model → d_model`. With `d_model=768` that's a 3 072-wide hidden layer.


# %% [markdown] color=mint title="3 · `MultiHeadAttention` — fused QKV"
# # 3 · `MultiHeadAttention` — fused QKV
#


# %% color=peach title="Three projections fused for speed"
# @explain: Three projections fused for speed; OpenAI calls this c_attn
class MultiHeadAttention(nn.Module):
    def __init__(self, d_in, d_out, context_length, dropout, num_heads, qkv_bias=False):
        super().__init__()
        assert d_out % num_heads == 0
        self.d_out = d_out
        self.num_heads = num_heads
        self.head_dim  = d_out // num_heads

        # Three projections fused for speed; OpenAI calls this c_attn
        self.W_query = nn.Linear(d_in, d_out, bias=qkv_bias)
        self.W_key   = nn.Linear(d_in, d_out, bias=qkv_bias)
        self.W_value = nn.Linear(d_in, d_out, bias=qkv_bias)
        self.out_proj = nn.Linear(d_out, d_out)
        self.dropout = nn.Dropout(dropout)
        self.register_buffer("mask",
            torch.triu(torch.ones(context_length, context_length), diagonal=1))

    def forward(self, x):
        b, T, _ = x.shape
        Q = self.W_query(x).view(b, T, self.num_heads, self.head_dim).transpose(1, 2)
        K = self.W_key(x).view(b, T, self.num_heads, self.head_dim).transpose(1, 2)
        V = self.W_value(x).view(b, T, self.num_heads, self.head_dim).transpose(1, 2)

        attn = (Q @ K.transpose(-2, -1)) / self.head_dim ** 0.5
        attn = attn.masked_fill(self.mask.bool()[:T, :T], -torch.inf)
        attn = torch.softmax(attn, dim=-1)
        attn = self.dropout(attn)

        ctx = (attn @ V).transpose(1, 2).contiguous().view(b, T, self.d_out)
        return self.out_proj(ctx)


# %% [markdown] color=violet title="Same structure as M20"
# # Same structure as M20
#
# Same structure as M20, with two differences that matter for **loading OpenAI weights**:
# - Separate `W_query / W_key / W_value` matrices (the OpenAI checkpoint stores them as **one fused `c_attn`** matrix; we'll split it).
# - `qkv_bias=True` — GPT-2 has bias terms.


# %% [markdown] color=amber title="4 · `TransformerBlock` — pre-norm + residual"
# # 4 · `TransformerBlock` — pre-norm + residual
#


# %% color=rose title="Pre-norm"
# @explain: Pre-norm — Norm BEFORE the sub-layer, residual around the whole thing
class TransformerBlock(nn.Module):
    def __init__(self, cfg):
        super().__init__()
        self.att = MultiHeadAttention(
            d_in=cfg["emb_dim"], d_out=cfg["emb_dim"],
            context_length=cfg["context_length"],
            num_heads=cfg["n_heads"], dropout=cfg["drop_rate"],
            qkv_bias=cfg["qkv_bias"],
        )
        self.ff = FeedForward(cfg)
        self.norm1 = LayerNorm(cfg["emb_dim"])
        self.norm2 = LayerNorm(cfg["emb_dim"])
        self.drop_shortcut = nn.Dropout(cfg["drop_rate"])

    def forward(self, x):
        # Pre-norm — Norm BEFORE the sub-layer, residual around the whole thing
        shortcut = x
        x = self.att(self.norm1(x))
        x = self.drop_shortcut(x)
        x = x + shortcut

        shortcut = x
        x = self.ff(self.norm2(x))
        x = self.drop_shortcut(x)
        x = x + shortcut
        return x


# %% [markdown] color=lime title="Pre-norm vs post-norm.** GPT-2 is **pre-norm**: `x…"
# # Pre-norm vs post-norm.** GPT-2 is **pre-norm**: `x…
#
# **Pre-norm vs post-norm.** GPT-2 is **pre-norm**: `x + sublayer(LN(x))`. Modern models (Llama, Qwen, DeepSeek) keep pre-norm too — it trains much more stably than the post-norm of the original "Attention Is All You Need" paper.


# %% [markdown] color=teal title="5 · `GPTModel` — full assembly"
# # 5 · `GPTModel` — full assembly
#


# %% color=sky title="class GPTModel(nn.Module)"
# @explain: Run this cell to see the output.
class GPTModel(nn.Module):
    def __init__(self, cfg):
        super().__init__()
        self.tok_emb = nn.Embedding(cfg["vocab_size"], cfg["emb_dim"])
        self.pos_emb = nn.Embedding(cfg["context_length"], cfg["emb_dim"])
        self.drop_emb = nn.Dropout(cfg["drop_rate"])
        self.trf_blocks = nn.Sequential(
            *[TransformerBlock(cfg) for _ in range(cfg["n_layers"])]
        )
        self.final_norm = LayerNorm(cfg["emb_dim"])
        self.out_head = nn.Linear(cfg["emb_dim"], cfg["vocab_size"], bias=False)

    def forward(self, in_idx):
        b, T = in_idx.shape
        tok = self.tok_emb(in_idx)
        pos = self.pos_emb(torch.arange(T, device=in_idx.device))
        x = self.drop_emb(tok + pos)
        x = self.trf_blocks(x)
        x = self.final_norm(x)
        logits = self.out_head(x)
        return logits

torch.manual_seed(123)
model = GPTModel(GPT_CONFIG_124M)
print(model)


# %% [markdown] color=mint title="6 · Weight tying — why **124M**, not 163M"
# # 6 · Weight tying — why **124M**, not 163M
#
# The token embedding is `(50 257 × 768)` and the output head is `(768 × 50 257)`. That's the **same matrix**, transposed. Modern transformers **tie** them — share one weight tensor — to halve the embedding parameters and to keep input and output vocab projections in the same space.


# %% color=peach title="untied"
# @explain: untied (what we have right now)
# @explain: Tie them: lm_head.weight points at the same tensor as tok_emb.weight
# untied (what we have right now)
total_params = sum(p.numel() for p in model.parameters())
print(f"untied total: {total_params:,}")

# Tie them: lm_head.weight points at the same tensor as tok_emb.weight
model.out_head.weight = model.tok_emb.weight

total_params_tied = sum(p.numel() for p in model.parameters())
print(f"tied total:   {total_params_tied:,}   # this is the 124M number")


# %% [markdown] color=violet title="Reporting tools that count **unique tensors** (like…"
# # Reporting tools that count **unique tensors** (like…
#
# Reporting tools that count **unique tensors** (like HF) see **124 M**. Untied, the *raw* number is ~163 M. **Both are the same model** — the tied version just doesn't double-count the shared matrix.


# %% [markdown] color=amber title="7 · Parameter budget — where the params live"
# # 7 · Parameter budget — where the params live
#


# %% color=rose title="def count(module)"
# @explain: Run this cell to see the output.
def count(module):
    return sum(p.numel() for p in module.parameters())

print(f"token embedding   : {count(model.tok_emb):>11,}")
print(f"positional emb    : {count(model.pos_emb):>11,}")
print(f"final layer-norm  : {count(model.final_norm):>11,}")
print(f"one transformer blk: {count(model.trf_blocks[0]):>11,}")
print(f"  attention sub-blk: {count(model.trf_blocks[0].att):>11,}")
print(f"  feed-forward sub : {count(model.trf_blocks[0].ff):>11,}")
print(f"all 12 blocks      : {count(model.trf_blocks):>11,}")
print(f"--")
print(f"TOTAL (tied)       : {count(model):>11,}")


# %% [markdown] color=lime title="Mental rule of thumb.** Each transformer block has…"
# # Mental rule of thumb.** Each transformer block has…
#
# **Mental rule of thumb.** Each transformer block has `4·d² + 8·d²·1 ≈ 12·d²` params (attention + FFN). With `d=768` that's ~7.1 M per block × 12 = ~85 M; plus embeddings (50 257 × 768 ≈ 38.6 M, shared in/out), positional (~0.8 M), final LN (~1.5 K) → ~124 M.


# %% [markdown] color=teal title="8 · Download OpenAI's GPT-2 weights & load them"
# # 8 · Download OpenAI's GPT-2 weights & load them
#


# %% color=sky title="Pull Raschka's helper"
# @explain: Pull Raschka's helper — it downloads OpenAI's TF checkpoint and returns
# @explain: `settings` (cfg) + `params` (nested dict of numpy arrays in the OpenAI naming)
# Pull Raschka's helper — it downloads OpenAI's TF checkpoint and returns
# `settings` (cfg) + `params` (nested dict of numpy arrays in the OpenAI naming).
import urllib.request, importlib.util, os
url = "https://raw.githubusercontent.com/rasbt/LLMs-from-scratch/main/ch05/01_main-chapter-code/gpt_download.py"
urllib.request.urlretrieve(url, "/content/gpt_download.py")
spec = importlib.util.spec_from_file_location("gpt_download", "/content/gpt_download.py")
gpt_download = importlib.util.module_from_spec(spec); spec.loader.exec_module(gpt_download)

settings, params = gpt_download.download_and_load_gpt2(model_size="124M", models_dir="/content/gpt2")
print("settings:", settings)
print("top-level params keys:", list(params.keys())[:6])


# %% [markdown] color=mint title="`params` is shaped like the original TF checkpoint"
# # `params` is shaped like the original TF checkpoint
#
# `params` is shaped like the original TF checkpoint:
# ```
# params['wte']                # (50257, 768)  token embedding
# params['wpe']                # (1024, 768)   positional
# params['blocks'][i]['attn']['c_attn']['w']   # (768, 2304)  — fused Q,K,V
# params['blocks'][i]['attn']['c_attn']['b']   # (2304,)
# params['blocks'][i]['attn']['c_proj']['w']   # (768, 768)
# params['blocks'][i]['ln_1']['g'] / ['b']     # scale / shift
# …


# %% color=peach title="split the fused c_attn into Q"
# @explain: split the fused c_attn into Q, K, V
# @explain: tie output head to token embedding (GPT-2 ties them)
import numpy as np

def assign(left, right):
    if left.shape != right.shape:
        raise ValueError(f"shape mismatch: {left.shape} vs {right.shape}")
    return torch.nn.Parameter(torch.tensor(right))

def load_weights_into_gpt(gpt, params):
    gpt.pos_emb.weight = assign(gpt.pos_emb.weight, params['wpe'])
    gpt.tok_emb.weight = assign(gpt.tok_emb.weight, params['wte'])

    for b in range(len(params["blocks"])):
        # split the fused c_attn into Q, K, V
        q_w, k_w, v_w = np.split(params["blocks"][b]["attn"]["c_attn"]["w"], 3, axis=-1)
        q_b, k_b, v_b = np.split(params["blocks"][b]["attn"]["c_attn"]["b"], 3, axis=-1)
        gpt.trf_blocks[b].att.W_query.weight = assign(gpt.trf_blocks[b].att.W_query.weight, q_w.T)
        gpt.trf_blocks[b].att.W_key.weight   = assign(gpt.trf_blocks[b].att.W_key.weight,   k_w.T)
        gpt.trf_blocks[b].att.W_value.weight = assign(gpt.trf_blocks[b].att.W_value.weight, v_w.T)
        gpt.trf_blocks[b].att.W_query.bias   = assign(gpt.trf_blocks[b].att.W_query.bias,   q_b)
        gpt.trf_blocks[b].att.W_key.bias     = assign(gpt.trf_blocks[b].att.W_key.bias,     k_b)
        gpt.trf_blocks[b].att.W_value.bias   = assign(gpt.trf_blocks[b].att.W_value.bias,   v_b)

        gpt.trf_blocks[b].att.out_proj.weight = assign(gpt.trf_blocks[b].att.out_proj.weight,
                                                       params["blocks"][b]["attn"]["c_proj"]["w"].T)
        gpt.trf_blocks[b].att.out_proj.bias   = assign(gpt.trf_blocks[b].att.out_proj.bias,
                                                       params["blocks"][b]["attn"]["c_proj"]["b"])

        gpt.trf_blocks[b].ff.layers[0].weight = assign(gpt.trf_blocks[b].ff.layers[0].weight,
                                                       params["blocks"][b]["mlp"]["c_fc"]["w"].T)
        gpt.trf_blocks[b].ff.layers[0].bias   = assign(gpt.trf_blocks[b].ff.layers[0].bias,
                                                       params["blocks"][b]["mlp"]["c_fc"]["b"])
        gpt.trf_blocks[b].ff.layers[2].weight = assign(gpt.trf_blocks[b].ff.layers[2].weight,
                                                       params["blocks"][b]["mlp"]["c_proj"]["w"].T)
        gpt.trf_blocks[b].ff.layers[2].bias   = assign(gpt.trf_blocks[b].ff.layers[2].bias,
                                                       params["blocks"][b]["mlp"]["c_proj"]["b"])

        gpt.trf_blocks[b].norm1.scale = assign(gpt.trf_blocks[b].norm1.scale, params["blocks"][b]["ln_1"]["g"])
        gpt.trf_blocks[b].norm1.shift = assign(gpt.trf_blocks[b].norm1.shift, params["blocks"][b]["ln_1"]["b"])
        gpt.trf_blocks[b].norm2.scale = assign(gpt.trf_blocks[b].norm2.scale, params["blocks"][b]["ln_2"]["g"])
        gpt.trf_blocks[b].norm2.shift = assign(gpt.trf_blocks[b].norm2.shift, params["blocks"][b]["ln_2"]["b"])

    gpt.final_norm.scale = assign(gpt.final_norm.scale, params["g"])
    gpt.final_norm.shift = assign(gpt.final_norm.shift, params["b"])
    # tie output head to token embedding (GPT-2 ties them)
    gpt.out_head.weight = gpt.tok_emb.weight

load_weights_into_gpt(model, params)
print("loaded OpenAI GPT-2 124M weights into our PyTorch model")


# %% [markdown] color=violet title="Three tricks in that loader"
# # Three tricks in that loader
#
# **Three tricks in that loader.**
# 1. `c_attn` is a **fused** matrix of shape `(768, 3·768)`. We **split along the last axis** to recover Q, K, V.
# 2. TF stores weights as `(in, out)`; PyTorch's `nn.Linear` stores them as `(out, in)`. So every weight gets a `.T` (transpose).
# 3. After loading, we **re-tie** `out_head.weight` to `tok_emb.weight` because OpenAI's checkpoint only ships the token embedding.


# %% [markdown] color=amber title="9 · `generate_text_simple` — greedy decode"
# # 9 · `generate_text_simple` — greedy decode
#


# %% color=rose title="def generate_text_simple(model"
# @explain: Run this cell to see the output.
def generate_text_simple(model, idx, max_new_tokens, context_size):
    model.eval()
    for _ in range(max_new_tokens):
        idx_cond = idx[:, -context_size:]            # crop to context window
        with torch.no_grad():
            logits = model(idx_cond)
        logits = logits[:, -1, :]                    # last position's logits
        next_id = torch.argmax(logits, dim=-1, keepdim=True)
        idx = torch.cat((idx, next_id), dim=1)
    return idx


# %% [markdown] color=lime title="10 · Generate text from the real model"
# # 10 · Generate text from the real model
#


# %% color=teal title="import tiktoken"
# @explain: Run this cell to see the output.
import tiktoken
tok = tiktoken.get_encoding("gpt2")

prompt = "Every effort moves you"
encoded = tok.encode(prompt)
ctx = torch.tensor(encoded).unsqueeze(0)
print("input  :", encoded)

out = generate_text_simple(model, ctx, max_new_tokens=20,
                           context_size=GPT_CONFIG_124M["context_length"])
print("output :", out[0].tolist())
print()
print(tok.decode(out[0].tolist()))


# %% [markdown] color=sky title="✅ Recap"
# # ✅ Recap
#
# You should see something coherent like
# ```
# Every effort moves you toward finding an ideal new way to practice something.
# ```
# That's the real OpenAI GPT-2 124M running inside the code **you** wrote. The model from M19+M20+M24 is no longer a toy — it loads a real checkpoint and produces real English.
#
# > 🔬 **Why this matters.** From here, every modern LLM is "just" this design with bigger numbers, RoPE instead of `pos_emb`, RMSNorm instead of LayerNorm, GQA instead of MHA, SwiGLU instead of GELU-MLP — all swaps we cover in **M61**.
#
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


