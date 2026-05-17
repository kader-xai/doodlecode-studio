# doodlecode format-version: 2
# Auto-converted from module_20_multihead_causal_attention.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 20 Multihead Causal Attention"
# # Module 20 Multihead Causal Attention
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 20 — Multi-Head + Causal Attention"
# # Module 20 — Multi-Head + Causal Attention
#
# *Picks up from Module 19. The transformer's full attention block in ~150 lines of PyTorch.*
#
# In M19 you built single-head self-attention. Real transformers use **multi-head** attention with **causal masking**. This module fills both in.
#
# ### What you'll cover
# 1. Why one head isn't enough
# 2. Multi-head attention — split, run in parallel, concatenate
# …


# %% color=mint title="import torch"
# @explain: Run this cell to see the output.
import torch, torch.nn as nn, torch.nn.functional as F
torch.manual_seed(0)
print("torch:", torch.__version__)


# %% [markdown] color=peach title="1. Why one head isn't enough"
# # 1. Why one head isn't enough
#
# A single attention head computes **one** weighted average per token. That means the model can capture only **one** pattern of "who attends to whom" at a time. But language has many — syntactic, semantic, positional, coreference, etc.
#
# **The fix:** run **h** parallel attention heads. Each has its own Q, K, V projections — so each can specialise.
#
# ### The math
#
# …


# %% [markdown] color=violet title="2. The basic multi-head attention class"
# # 2. The basic multi-head attention class
#


# %% color=amber title="We can stack Q, K, V into ONE projection of size…"
# @explain: We can stack Q, K, V into ONE projection of size 3*d_model
# @explain: 1) project + split into Q, K, V
# @explain: 2) reshape to (B, h, T, d_head)
# @explain: 3) scaled dot-product attention per head
# @explain: 4) merge heads back: (B, h, T, d) -> (B, T, D)
class MultiHeadAttention(nn.Module):
    def __init__(self, d_model: int, n_heads: int, bias: bool = False):
        super().__init__()
        assert d_model % n_heads == 0, "d_model must be divisible by n_heads"
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_head  = d_model // n_heads

        # We can stack Q, K, V into ONE projection of size 3*d_model. Faster.
        self.qkv = nn.Linear(d_model, 3 * d_model, bias=bias)
        self.out = nn.Linear(d_model, d_model, bias=bias)

    def forward(self, x):
        B, T, D = x.shape
        h, d = self.n_heads, self.d_head

        # 1) project + split into Q, K, V
        qkv = self.qkv(x)                                  # (B, T, 3*D)
        q, k, v = qkv.chunk(3, dim=-1)                     # each (B, T, D)

        # 2) reshape to (B, h, T, d_head)
        q = q.view(B, T, h, d).transpose(1, 2)             # (B, h, T, d)
        k = k.view(B, T, h, d).transpose(1, 2)
        v = v.view(B, T, h, d).transpose(1, 2)

        # 3) scaled dot-product attention per head
        scores = q @ k.transpose(-2, -1) / d ** 0.5        # (B, h, T, T)
        weights = F.softmax(scores, dim=-1)
        out = weights @ v                                  # (B, h, T, d)

        # 4) merge heads back: (B, h, T, d) -> (B, T, D)
        out = out.transpose(1, 2).contiguous().view(B, T, D)
        return self.out(out)


# Toy run: batch of 2 sequences, T=4 tokens, d_model=8, 2 heads
mha = MultiHeadAttention(d_model=8, n_heads=2)
x = torch.randn(2, 4, 8)
y = mha(x)
print("input :", x.shape)
print("output:", y.shape)   # same shape as input — that's the point


# %% [markdown] color=rose title="3. Causal masking — no peeking at the future"
# # 3. Causal masking — no peeking at the future
#
# In a **decoder** (GPT-style language model), token `t` must only attend to tokens `≤ t`. Otherwise the model trivially "predicts" the next word by looking at it.
#
# **The fix:** before the softmax, set the future positions in the score matrix to `-∞`. Softmax of `-∞` is 0, so no probability flows from those positions.
#
# The mask is a lower-triangular matrix of 1s:
#
# …


# %% color=lime title="Example score matrix"
# @explain: Example score matrix
# @explain: Apply: where mask == 0, set to -inf
# @explain: After softmax, the upper triangle becomes 0
T = 4
mask = torch.tril(torch.ones(T, T))
print(mask)

# Example score matrix
scores = torch.randn(T, T)
print("\nscores before mask:\n", scores.round(decimals=2))

# Apply: where mask == 0, set to -inf
masked = scores.masked_fill(mask == 0, float("-inf"))
print("\nafter mask:\n", masked.round(decimals=2))

# After softmax, the upper triangle becomes 0
print("\nafter softmax:\n", F.softmax(masked, dim=-1).round(decimals=2))


# %% [markdown] color=teal title="4. Putting it together — `CausalMultiHeadAttention`"
# # 4. Putting it together — `CausalMultiHeadAttention`
#


# %% color=sky title="Pre-build the causal mask up to max_len"
# @explain: Pre-build the causal mask up to max_len (then slice at forward time)
# @explain: Sanity check
class CausalMultiHeadAttention(nn.Module):
    def __init__(self, d_model, n_heads, max_len=1024, dropout=0.0, bias=False):
        super().__init__()
        assert d_model % n_heads == 0
        self.d_model, self.n_heads, self.d_head = d_model, n_heads, d_model // n_heads
        self.qkv = nn.Linear(d_model, 3 * d_model, bias=bias)
        self.out = nn.Linear(d_model, d_model, bias=bias)
        self.dropout = nn.Dropout(dropout)

        # Pre-build the causal mask up to max_len (then slice at forward time)
        self.register_buffer(
            "mask",
            torch.tril(torch.ones(max_len, max_len)).view(1, 1, max_len, max_len),
            persistent=False,
        )

    def forward(self, x):
        B, T, D = x.shape
        h, d = self.n_heads, self.d_head

        q, k, v = self.qkv(x).chunk(3, dim=-1)
        q = q.view(B, T, h, d).transpose(1, 2)
        k = k.view(B, T, h, d).transpose(1, 2)
        v = v.view(B, T, h, d).transpose(1, 2)

        scores = q @ k.transpose(-2, -1) / d ** 0.5             # (B, h, T, T)
        scores = scores.masked_fill(self.mask[:, :, :T, :T] == 0, float("-inf"))
        weights = self.dropout(F.softmax(scores, dim=-1))
        out = weights @ v
        out = out.transpose(1, 2).contiguous().view(B, T, D)
        return self.out(out)


# Sanity check
cmha = CausalMultiHeadAttention(d_model=8, n_heads=2)
y = cmha(torch.randn(2, 4, 8))
print("output shape:", y.shape)


# %% [markdown] color=mint title="Verify the causal property"
# # Verify the causal property
#
# If we change a future token, the **earlier** outputs must NOT change.


# %% color=peach title="Mutate the LAST token"
# @explain: Mutate the LAST token
# @explain: Outputs at positions 0..3 should be IDENTICAL; only position 4 differs
cmha.eval()
x = torch.randn(1, 5, 8)
y1 = cmha(x.clone())

# Mutate the LAST token
x_mod = x.clone()
x_mod[:, -1, :] = torch.randn(8)
y2 = cmha(x_mod)

# Outputs at positions 0..3 should be IDENTICAL; only position 4 differs.
diff_per_pos = (y1 - y2).abs().sum(dim=-1).squeeze()
print("max diff per position:", diff_per_pos.tolist())
print("\n✅ Positions 0-3 are unchanged — the mask works.")


# %% [markdown] color=violet title="5. The full transformer block"
# # 5. The full transformer block
#
# A real transformer layer is **attention + feed-forward + LayerNorms + residual connections**:
#
# ```
# x → LayerNorm → CausalMHA → + → x'
#                               ↑
#                               residual (the '+' is "x + ...")
# …


# %% color=amber title="class FeedForward(nn.Module)"
# @explain: Run this cell to see the output.
class FeedForward(nn.Module):
    def __init__(self, d_model, expansion=4, dropout=0.0):
        super().__init__()
        d_ff = expansion * d_model
        self.net = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.GELU(),
            nn.Linear(d_ff, d_model),
            nn.Dropout(dropout),
        )
    def forward(self, x): return self.net(x)


class TransformerBlock(nn.Module):
    def __init__(self, d_model, n_heads, max_len=1024, dropout=0.0):
        super().__init__()
        self.ln1  = nn.LayerNorm(d_model)
        self.attn = CausalMultiHeadAttention(d_model, n_heads, max_len, dropout)
        self.ln2  = nn.LayerNorm(d_model)
        self.ffn  = FeedForward(d_model, expansion=4, dropout=dropout)

    def forward(self, x):
        x = x + self.attn(self.ln1(x))     # residual + pre-norm
        x = x + self.ffn (self.ln2(x))
        return x


block = TransformerBlock(d_model=8, n_heads=2)
y = block(torch.randn(2, 4, 8))
print("block output:", y.shape)
print("\nparameter count:", sum(p.numel() for p in block.parameters()))


# %% [markdown] color=rose title="Stack N blocks → a tiny transformer"
# # Stack N blocks → a tiny transformer
#


# %% color=lime title="class TinyTransformer(nn.Module)"
# @explain: Run this cell to see the output.
class TinyTransformer(nn.Module):
    def __init__(self, vocab_size, d_model=64, n_heads=4, n_layers=4, max_len=128):
        super().__init__()
        self.tok_emb = nn.Embedding(vocab_size, d_model)
        self.pos_emb = nn.Embedding(max_len,    d_model)
        self.blocks  = nn.Sequential(*[
            TransformerBlock(d_model, n_heads, max_len) for _ in range(n_layers)
        ])
        self.ln   = nn.LayerNorm(d_model)
        self.head = nn.Linear(d_model, vocab_size, bias=False)

    def forward(self, idx):
        B, T = idx.shape
        pos = torch.arange(T, device=idx.device)
        x = self.tok_emb(idx) + self.pos_emb(pos)
        x = self.blocks(x)
        x = self.ln(x)
        return self.head(x)                       # (B, T, vocab) — logits


model = TinyTransformer(vocab_size=100, d_model=64, n_heads=4, n_layers=2)
toy_input = torch.randint(0, 100, (2, 16))         # batch=2, seq=16
logits = model(toy_input)
print("input :", toy_input.shape)
print("logits:", logits.shape, "  ← (B, T, vocab_size)")
print("params:", f"{sum(p.numel() for p in model.parameters()):,}")


# %% [markdown] color=teal title="6. Where this scales to"
# # 6. Where this scales to
#
# The block you just wrote is the same one in GPT-2, GPT-3, GPT-4, Llama, Mistral. The differences in modern models are mostly **engineering optimisations**:
#
# | Optimisation | What it solves | When you'll meet it |
# |---|---|---|
# | **KV cache** | recomputing K/V every step during generation | as soon as you write `model.generate(...)` |
# | **FlashAttention** | the `(B,h,T,T)` matrix doesn't fit in GPU memory at long T | training >2k context |
# …


# %% [markdown] color=sky title="7. Practice"
# # 7. Practice
#
# 1. Add **dropout** to the attention weights (after softmax, before `@ v`). Verify the model still produces the right shape.
# 2. **Plot the attention weights** of one trained block as a heatmap (`(T, T)` matrix). After the lower triangle is intact, weights should sum to 1 along each row.
# 3. Replace `nn.GELU()` with `nn.SiLU()` (also called Swish) — used in Llama and Mistral. Verify the model still runs.
# 4. Implement a **single forward** generation loop — given an input prompt of shape `(1, T)`, run `model(idx)`, take `argmax` of the last position's logits, append, repeat 20 times. Print the generated token IDs.


# %% color=mint title="1) Dropout already added in…"
# @explain: 1) Dropout already added in CausalMultiHeadAttention via self.dropout
# @explain: 2) Inspect attention weights — pull them out of an attention forward pass
# @explain: 4) Greedy single-step "generation"
# 1) Dropout already added in CausalMultiHeadAttention via self.dropout
cmha = CausalMultiHeadAttention(d_model=8, n_heads=2, dropout=0.1)
print("dropout cmha output:", cmha(torch.randn(2, 4, 8)).shape)

# 2) Inspect attention weights — pull them out of an attention forward pass
@torch.no_grad()
def attn_weights(layer, x):
    """Re-run the math but return the softmax output."""
    B, T, D = x.shape; h, d = layer.n_heads, layer.d_head
    q, k, v = layer.qkv(x).chunk(3, dim=-1)
    q = q.view(B, T, h, d).transpose(1, 2)
    k = k.view(B, T, h, d).transpose(1, 2)
    s = q @ k.transpose(-2, -1) / d ** 0.5
    s = s.masked_fill(layer.mask[:, :, :T, :T] == 0, float("-inf"))
    return F.softmax(s, dim=-1)

w = attn_weights(cmha, torch.randn(1, 6, 8))[0, 0]      # head 0 of sample 0
print("\nattention weights (lower-triangular by construction):")
print(w.round(decimals=2))
print("each row sums to 1:", w.sum(dim=-1).round(decimals=4).tolist())

# 4) Greedy single-step "generation"
@torch.no_grad()
def greedy(model, idx, n_new_tokens=20):
    for _ in range(n_new_tokens):
        logits = model(idx)
        next_id = logits[:, -1, :].argmax(dim=-1, keepdim=True)
        idx = torch.cat([idx, next_id], dim=1)
    return idx

prompt = torch.randint(0, 100, (1, 4))
out = greedy(model, prompt, n_new_tokens=10)
print("\nprompt :", prompt.tolist())
print("generated:", out.tolist())


# %% [markdown] color=peach title="Recap"
# # Recap
#
# ✅ Built `MultiHeadAttention` from `nn.Linear` and `chunk`
# ✅ Built a **causal** mask that prevents future-leakage
# ✅ Combined them into a real `TransformerBlock` (LN → MHA → FFN with residuals)
# ✅ Stacked blocks into a `TinyTransformer` you can train
# ✅ Verified causality empirically by mutating future tokens
#
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


