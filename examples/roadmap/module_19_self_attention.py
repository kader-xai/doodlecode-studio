# doodlecode format-version: 2
# Auto-converted from module_19_self_attention.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 19 Self Attention"
# # Module 19 Self Attention
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Self-Attention from Scratch in PyTorch"
# # Self-Attention from Scratch in PyTorch
#
# **Companion notebook to Chapter 5 of the *LLM Fundamentals* course.**
#
# This notebook builds self-attention the StatQuest way — small enough that you can verify every number by hand — then connects it back to the multi-head causal version we use in real LLMs.
#
# By the end you will:
# 1. Code a `SelfAttention` class from scratch.
# …


# %% [markdown] color=mint title="0. Setup"
# # 0. Setup
#
# PyTorch is preinstalled in Colab — no `pip install` needed.


# %% color=peach title="import torch"
# @explain: Run this cell to see the output.
import torch
import torch.nn as nn
import torch.nn.functional as F

print("PyTorch version:", torch.__version__)
print("CUDA available: ", torch.cuda.is_available())


# %% [markdown] color=violet title="1. The one-paragraph mental model"
# # 1. The one-paragraph mental model
#
# For each token in the input, self-attention asks: *"Looking at every other token, how much should I borrow from each, and what should I borrow?"*
#
# We answer that with three projections of every token's embedding:
#
# - **Query (Q)** — "what am I looking for?"
# - **Key (K)** — "what do I contain?"
# …


# %% [markdown] color=amber title="2. Code the `SelfAttention` class"
# # 2. Code the `SelfAttention` class
#
# We use `d_model = 2` so we can read the matrices and check the arithmetic by hand. In a real LLM `d_model` is 768 to 12,288+.
#
# Note: the original *Attention Is All You Need* paper did **not** use bias terms in the Q/K/V projections, so we set `bias=False` to match.


# %% color=rose title="Three learnable projections, no bias"
# @explain: Three learnable projections, no bias (matches the original paper)
# @explain: 1
# @explain: 2
# @explain: 3
# @explain: 4
class SelfAttention(nn.Module):
    """Single-head, non-causal self-attention. As small as it gets."""

    def __init__(self, d_model=2, row_dim=0, col_dim=1):
        super().__init__()
        # Three learnable projections, no bias (matches the original paper)
        self.W_q = nn.Linear(d_model, d_model, bias=False)
        self.W_k = nn.Linear(d_model, d_model, bias=False)
        self.W_v = nn.Linear(d_model, d_model, bias=False)

        self.row_dim = row_dim
        self.col_dim = col_dim

    def forward(self, token_encodings):
        # 1. Project each token's encoding into Q, K, V
        q = self.W_q(token_encodings)
        k = self.W_k(token_encodings)
        v = self.W_v(token_encodings)

        # 2. Compatibility scores: Q @ K^T, shape (n_tokens, n_tokens)
        sims = torch.matmul(q, k.transpose(self.row_dim, self.col_dim))

        # 3. Scale by sqrt(d_k) so dot products don't grow with dimension
        scaled_sims = sims / torch.tensor(k.size(self.col_dim) ** 0.5)

        # 4. Softmax across the keys -> attention weights
        attention_percents = F.softmax(scaled_sims, dim=self.col_dim)

        # 5. Weighted sum of value vectors
        return torch.matmul(attention_percents, v)


# %% [markdown] color=lime title="3. Run it on a toy input"
# # 3. Run it on a toy input
#
# Three tokens, each represented by a 2-dim embedding. Pretend these are the embeddings of, say, *the*, *cat*, *sat*.


# %% color=teal title="3 tokens"
# @explain: 3 tokens, d_model = 2
# 3 tokens, d_model = 2
encodings_matrix = torch.tensor([
    [1.16,  0.23],   # token 0
    [0.57,  1.36],   # token 1
    [4.41, -2.16],   # token 2
])

torch.manual_seed(42)  # reproducible W_q, W_k, W_v initialization
self_attn = SelfAttention(d_model=2, row_dim=0, col_dim=1)

output = self_attn(encodings_matrix)
print("Attention output (one row per input token):")
print(output)


# %% [markdown] color=sky title="4. Verify every step"
# # 4. Verify every step
#
# The whole point of a tiny example is that you can check the math. Let's reproduce what `forward()` did, one step at a time, and confirm we get the same result.
#
# ### 4.1 The learned weight matrices
#
# These are randomly initialized (we set the seed), and would normally get updated by training. PyTorch stores `nn.Linear` weights in **(out_features, in_features)** order, so we transpose to print them in the more natural (in, out) view.


# %% color=mint title="print('W_q:')"
# @explain: Run this cell to see the output.
print("W_q:")
print(self_attn.W_q.weight.transpose(0, 1))
print("\nW_k:")
print(self_attn.W_k.weight.transpose(0, 1))
print("\nW_v:")
print(self_attn.W_v.weight.transpose(0, 1))


# %% [markdown] color=peach title="4.2 Compute Q, K, V manually"
# # 4.2 Compute Q, K, V manually
#
# Each is a (3, 2) matrix: 3 tokens × 2 dims.


# %% color=violet title="q = self_attn.W_q(encodings_matrix)"
# @explain: Run this cell to see the output.
q = self_attn.W_q(encodings_matrix)
k = self_attn.W_k(encodings_matrix)
v = self_attn.W_v(encodings_matrix)

print("Q:\n", q)
print("\nK:\n", k)
print("\nV:\n", v)


# %% [markdown] color=amber title="4.3 Similarities: $Q K^\top$"
# # 4.3 Similarities: $Q K^\top$
#
# A (3, 3) matrix. Entry `[i, j]` is the raw compatibility of query token *i* with key token *j*.


# %% color=rose title="sims = torch.matmul(q"
# @explain: Run this cell to see the output.
sims = torch.matmul(q, k.transpose(0, 1))
print("Similarities (Q @ K^T):\n", sims)


# %% [markdown] color=lime title="4.4 Scale by $\sqrt{d_k}$"
# # 4.4 Scale by $\sqrt{d_k}$
#
# Without scaling, dot products grow with dimension and push softmax into very low-gradient regions, hurting training.


# %% color=teal title="d_k = k.size(1)  # 2 in our toy example"
# @explain: Run this cell to see the output.
d_k = k.size(1)  # 2 in our toy example
scaled_sims = sims / (d_k ** 0.5)
print(f"Scaled similarities (divided by sqrt({d_k})):\n", scaled_sims)


# %% [markdown] color=sky title="4.5 Softmax → attention weights"
# # 4.5 Softmax → attention weights
#
# Softmax along `dim=1` so each **row** sums to 1. Each row says "if I'm token *i*, here's how I distribute my attention across all tokens."
#
# Confirm that every row sums to 1.0.


# %% color=mint title="attention_percents = F.softmax(scaled_sims"
# @explain: Run this cell to see the output.
attention_percents = F.softmax(scaled_sims, dim=1)
print("Attention weights:\n", attention_percents)
print("\nRow sums (should all be 1.0):", attention_percents.sum(dim=1))


# %% [markdown] color=peach title="4.6 Final output: weights @ V"
# # 4.6 Final output: weights @ V
#
# For each token, take the weighted average of all value vectors using its attention weights as the weights. This is the new representation of that token, now informed by every other token.


# %% color=violet title="manual_output = torch.matmul(attention_percents"
# @explain: Run this cell to see the output.
manual_output = torch.matmul(attention_percents, v)
print("Manual attention output:\n", manual_output)
print("\nMatches forward() output? ", torch.allclose(manual_output, output))


# %% [markdown] color=amber title="If that printed `True`, you've verified…"
# # If that printed `True`, you've verified…
#
# If that printed `True`, you've verified self-attention end-to-end. Every step is just a matrix multiply, a divide, and a softmax.


# %% [markdown] color=rose title="5. Connecting back to the full LLM"
# # 5. Connecting back to the full LLM
#
# This single-head, non-causal attention is the conceptual core. To get from here to what runs inside Claude or Llama, you add three things:
#
# ### 5.1 Multiple heads
#
# Instead of one Q/K/V projection, run several smaller ones in parallel and concatenate. Different heads specialize in different patterns (syntax, entity tracking, copying). With `d_model = 768` and 12 heads, each head operates on `head_dim = 64`.
#
# …


# %% color=lime title="One fused projection that produces Q"
# @explain: One fused projection that produces Q, K, V at once
# @explain: x shape: (batch, seq_len, d_model)
# @explain: Step 2-3: scaled dot-product, but per-head
# @explain: Step 3.5: causal mask — forbid attending to future positions
# @explain: Step 4: softmax
import math

class MultiHeadCausalSelfAttention(nn.Module):
    def __init__(self, d_model, num_heads):
        super().__init__()
        assert d_model % num_heads == 0
        self.num_heads = num_heads
        self.head_dim = d_model // num_heads

        # One fused projection that produces Q, K, V at once
        self.qkv_proj = nn.Linear(d_model, 3 * d_model, bias=False)
        self.out_proj = nn.Linear(d_model, d_model, bias=False)

    def forward(self, x):
        # x shape: (batch, seq_len, d_model)
        B, T, C = x.shape

        qkv = self.qkv_proj(x)                                # (B, T, 3C)
        qkv = qkv.view(B, T, 3, self.num_heads, self.head_dim)
        qkv = qkv.permute(2, 0, 3, 1, 4)                       # (3, B, heads, T, head_dim)
        q, k, v = qkv[0], qkv[1], qkv[2]

        # Step 2-3: scaled dot-product, but per-head
        scores = (q @ k.transpose(-2, -1)) / math.sqrt(self.head_dim)

        # Step 3.5: causal mask — forbid attending to future positions
        mask = torch.triu(torch.ones(T, T, device=x.device), diagonal=1).bool()
        scores = scores.masked_fill(mask, float('-inf'))

        # Step 4: softmax
        weights = F.softmax(scores, dim=-1)

        # Step 5: weighted sum
        out = weights @ v                                       # (B, heads, T, head_dim)

        # Recombine heads back into d_model
        out = out.transpose(1, 2).contiguous().view(B, T, C)
        return self.out_proj(out)


# Smoke test on random input
mh_attn = MultiHeadCausalSelfAttention(d_model=64, num_heads=4)
x = torch.randn(2, 10, 64)   # batch=2, seq_len=10, d_model=64
y = mh_attn(x)
print("Input shape: ", x.shape)
print("Output shape:", y.shape)   # same shape — this is the whole point


# %% [markdown] color=teal title="6. Quick exercise"
# # 6. Quick exercise
#
# Try these to lock the concept in:
#
# 1. **Inspect the attention pattern.** Modify the toy `SelfAttention` to also return `attention_percents`, then visualize it as a heatmap (`plt.imshow`). Which token attends most to which?
#
# 2. **Add a causal mask** to the toy class and re-run. Confirm the upper triangle of the attention weights is zero.
#
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


