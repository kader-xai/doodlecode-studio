# doodlecode format-version: 2
# Auto-converted from module_84_rnn_lstm_gru_deep_dive.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 84 Rnn Lstm Gru Deep Dive"
# # Module 84 Rnn Lstm Gru Deep Dive
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 84 — RNN / LSTM / GRU Deep Dive"
# # Module 84 — RNN / LSTM / GRU Deep Dive
#
# > M22 trained an LSTM forecaster as one part of the time-series module, but no module ever explained **why gates work** or **why we needed LSTMs at all**. This module is that depth pass. Twenty years of sequence-model history compressed into one notebook — and the answer to "in 2026, when do RNNs still beat Transformers?" (the answer is **yes, sometimes**).
#
# ### What you'll cover
# 1. Why sequence models — and the inductive bias they bring
# 2. The **vanilla RNN cell** — runnable in 8 lines
# 3. **Backprop through time (BPTT)** + the **vanishing / exploding gradient** problem
# …


# %% [markdown] color=mint title="1 · Why sequence models"
# # 1 · Why sequence models
#
# A fully-connected net treats `[x₀, x₁, …, x_T]` as one big vector — no notion of order. A CNN (M83) brings translation equivariance for spatial data, but a **shifted timeseries is not the same signal** in the way a shifted image is.
#
# What sequence models bring:
# - **Variable-length input** — you can run them on a 5-step sequence or a 5 000-step one.
# - **Causality (left-to-right)** — at time `t`, the model has only seen `x₀..x_t`.
# - **State carried forward** — the model summarises everything it's seen so far into a fixed-size **hidden state** `h_t`.
# …


# %% [markdown] color=peach title="2 · The vanilla RNN cell"
# # 2 · The vanilla RNN cell
#
# The simplest possible recurrent cell:
#
# $$h_t = \tanh(W_x x_t + W_h h_{t-1} + b)$$
#
# One linear combination, one nonlinearity, output is the new state. That's it.


# %% color=violet title="Roll over a sequence of length T"
# @explain: Roll over a sequence of length T
import torch, torch.nn as nn

class VanillaRNNCell(nn.Module):
    def __init__(self, x_dim, h_dim):
        super().__init__()
        self.Wx = nn.Linear(x_dim, h_dim, bias=False)
        self.Wh = nn.Linear(h_dim, h_dim, bias=True)
    def forward(self, x_t, h_prev):
        return torch.tanh(self.Wx(x_t) + self.Wh(h_prev))

# Roll over a sequence of length T
def run_rnn(cell, x_seq):
    B, T, _ = x_seq.shape
    h = torch.zeros(B, cell.Wh.out_features)
    outputs = []
    for t in range(T):
        h = cell(x_seq[:, t], h)
        outputs.append(h)
    return torch.stack(outputs, dim=1), h     # (B, T, H), (B, H)

cell = VanillaRNNCell(x_dim=8, h_dim=16)
x = torch.randn(4, 20, 8)                       # batch 4, length 20, features 8
out, h_final = run_rnn(cell, x)
print(out.shape, h_final.shape)


# %% [markdown] color=amber title="Three things to notice"
# # Three things to notice
#
# Three things to notice:
#
# - The cell uses the **same `Wx` and `Wh`** at every timestep — that's the analogue of CNN weight sharing (M83).
# - The hidden-state size is your **memory capacity** — bigger is better up to a point, then overfits.
# - There's no nonlinearity *between* timesteps in any direction except `tanh`. That matters in §3.


# %% [markdown] color=rose title="3 · Backprop through time + the vanishing / exploding gradient problem"
# # 3 · Backprop through time + the vanishing / exploding gradient problem
#
# To train, we unroll the cell over `T` steps and call `loss.backward()`. The gradient at step 0 must flow back through every multiplication by `W_h` (and the `tanh` derivative). After `T` steps:
#
# $$\frac{\partial h_T}{\partial h_0} = \prod_{t=1}^{T} W_h^\top \cdot \text{diag}(1 - h_t^2)$$
#
# Two failure modes:
#
# …


# %% color=lime title="Always pair RNN training with gradient clipping"
# @explain: Always pair RNN training with gradient clipping:
# Always pair RNN training with gradient clipping:
for x, y in loader:
    opt.zero_grad()
    pred = model(x)
    loss = criterion(pred, y)
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)   # ← the line
    opt.step()


# %% [markdown] color=teal title="4 · LSTM — Long Short-Term Memory"
# # 4 · LSTM — Long Short-Term Memory
#
# Hochreiter & Schmidhuber (1997) — a structural fix for vanishing gradients. The LSTM adds a **cell state** `c_t` that flows along the top with **only additive updates**, gated by sigmoid functions:
#
# ```
#                     ┌──────────────────────────────────────────────┐
#                     │                                              │
#    x_t          ───►│   ┌──── forget ────► × ──────────────────┐  │
# …


# %% color=sky title="Combine all four gate projections into one matmul…"
# @explain: Combine all four gate projections into one matmul for speed
class LSTMCell(nn.Module):
    """From-scratch LSTM cell. PyTorch's nn.LSTMCell is the production version."""
    def __init__(self, x_dim, h_dim):
        super().__init__()
        # Combine all four gate projections into one matmul for speed
        self.W = nn.Linear(x_dim + h_dim, 4 * h_dim)
        self.h_dim = h_dim
    def forward(self, x_t, state):
        h_prev, c_prev = state
        gates = self.W(torch.cat([x_t, h_prev], dim=-1))
        i, f, g, o = gates.chunk(4, dim=-1)         # input, forget, candidate, output
        i, f, o = torch.sigmoid(i), torch.sigmoid(f), torch.sigmoid(o)
        g = torch.tanh(g)
        c = f * c_prev + i * g
        h = o * torch.tanh(c)
        return h, (h, c)

cell = LSTMCell(8, 16)
h, c = torch.zeros(4, 16), torch.zeros(4, 16)
for t in range(20):
    out, (h, c) = cell(torch.randn(4, 8), (h, c))
print("final hidden:", h.shape, "cell:", c.shape)


# %% [markdown] color=mint title="A practical insight.** Most production LSTM code…"
# # A practical insight.** Most production LSTM code…
#
# **A practical insight.** Most production LSTM code initialises the **forget-gate bias to ~1**:
# ```python
# nn.init.constant_(lstm.bias_ih_l0[h_dim:2*h_dim], 1.0)
# ```
# This makes the forget gate start near `σ(1) ≈ 0.73`, so the cell state mostly persists at init — the network can learn what to forget rather than starting at "forget everything." Small change, big training stability.


# %% [markdown] color=peach title="5 · GRU — Gated Recurrent Unit"
# # 5 · GRU — Gated Recurrent Unit
#
# Cho et al. (2014). Same idea as LSTM with **one fewer gate** and **no separate cell state**. Two gates:
#
# - **Update gate** `z_t` — mixes the previous hidden state with the new candidate.
# - **Reset gate** `r_t` — allows the cell to "forget" the previous hidden state when computing the candidate.
#
# $$\begin{aligned}
# …


# %% [markdown] color=violet title="6 · Bidirectional + stacked + dropout"
# # 6 · Bidirectional + stacked + dropout
#
# Three orthogonal extensions you'll meet in every production RNN:
#
# ### Bidirectional RNN
# Two RNNs run in opposite directions; their outputs are concatenated. Doubles parameters; lets `h_t` see *future* tokens. Only valid for **non-causal** tasks (offline NER, sentiment, machine translation encoder). **Forbidden** for streaming or autoregressive generation.
#
# ```python
# …


# %% [markdown] color=amber title="7 · Seq2seq with attention — the bridge to Transformers"
# # 7 · Seq2seq with attention — the bridge to Transformers
#
# The 2014 **encoder-decoder** architecture (Sutskever et al.) was the first major sequence-to-sequence model. One LSTM **encodes** the source sentence into a single fixed-size vector; a second LSTM **decodes** the target sentence from it.
#
# Two problems:
# 1. **Fixed-size bottleneck** — compressing a 50-word sentence into a single vector loses information.
# 2. **Long-range dependency** — decoder must remember the start of the source through all decoder steps.
#
# …


# %% [markdown] color=rose title="8 · `nn.LSTM` — the production API + four shape gotchas"
# # 8 · `nn.LSTM` — the production API + four shape gotchas
#


# %% color=lime title="Production LSTM in PyTorch"
# @explain: Production LSTM in PyTorch
# @explain: Shape gotcha 1: batch_first
# @explain: Shape gotcha 2: h_n / c_n shape is (num_layers * num_directions, B, H), NOT batch-first
# @explain: Shape gotcha 3: hidden state is per-LAYER, not per-timestep — usually you want y[:, -1]
# @explain: Shape gotcha 4: PACKED sequences — variable length without padding waste
# Production LSTM in PyTorch
lstm = nn.LSTM(
    input_size=64,
    hidden_size=128,
    num_layers=2,
    dropout=0.2,
    bidirectional=False,
    batch_first=True,                   # ← (B, T, F) instead of (T, B, F)
)

# Shape gotcha 1: batch_first
x = torch.randn(32, 50, 64)             # (B=32, T=50, F=64)
y, (h_n, c_n) = lstm(x)

# Shape gotcha 2: h_n / c_n shape is (num_layers * num_directions, B, H), NOT batch-first
print("y shape:", y.shape)              # (B, T, H * num_directions)
print("h_n shape:", h_n.shape)          # (num_layers * num_directions, B, H)

# Shape gotcha 3: hidden state is per-LAYER, not per-timestep — usually you want y[:, -1]
last_hidden = y[:, -1, :]               # the canonical "summary vector" for classification
print("last hidden:", last_hidden.shape)

# Shape gotcha 4: PACKED sequences — variable length without padding waste
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence
lengths = torch.tensor([50, 47, 42, 30, 15])    # actual lengths per batch row
# (caller must pre-sort the batch by descending length in older PyTorch)
packed = pack_padded_sequence(x[:5], lengths, batch_first=True, enforce_sorted=True)
packed_out, _ = lstm(packed)
y_unpacked, _ = pad_packed_sequence(packed_out, batch_first=True)
print("unpacked:", y_unpacked.shape)


# %% [markdown] color=teal title="The four shape rules to keep on a sticky note"
# # The four shape rules to keep on a sticky note
#
# **The four shape rules to keep on a sticky note:**
# 1. `batch_first=True` → input + output are `(B, T, F)`. Without it, defaults are `(T, B, F)`. **Set `batch_first=True`.**
# 2. `h_n` and `c_n` are always `(num_layers × directions, B, hidden_size)` — never batch-first regardless of the flag.
# 3. For classification, **use `y[:, -1, :]`** (the last timestep's output) — *not* `h_n` for stacked / bidirectional LSTMs (it gets confusing fast).
# 4. For ragged batches, **pack** with `pack_padded_sequence` — otherwise PyTorch wastes compute on padding.


# %% [markdown] color=sky title="9 · Where RNNs still beat Transformers in 2026"
# # 9 · Where RNNs still beat Transformers in 2026
#
# Transformers won most of NLP, but RNNs **never went away**. Six places they're still the right call:
#
# | Use case | Why RNN wins |
# |---|---|
# | **Streaming / real-time inference** | RNN is **O(1) per token**; Transformer is **O(N)** without KV cache. For ASR (M65 Whisper streaming), real-time captioning, online anomaly detection, RNNs lead. |
# | **Very long sequences with limited memory** | Transformer self-attention is **O(N²)** memory. An LSTM is **O(1)**. For long ECG / sensor / power-grid traces, RNNs (or SSMs) win. |
# …


# %% [markdown] color=mint title="10 · The modern recurrence revival — Mamba, SSMs, xLSTM, RWKV, RetNet"
# # 10 · The modern recurrence revival — Mamba, SSMs, xLSTM, RWKV, RetNet
#
# After 5 years of "Transformer is all you need," 2023–25 brought a **renaissance of recurrence** under new names:
#
# | Family | Key idea | When it wins |
# |---|---|---|
# | **Linear Attention** (Katharopoulos 2020) | replace softmax-attention with a linear-kernel variant; gives O(N) memory & a recurrent form for inference | sequence modelling at length |
# | **RetNet** (Microsoft, 2023) | retention mechanism; trainable in parallel like Transformer, recurrent at inference like RNN | LLM-style models with long-context inference |
# …


# %% [markdown] color=peach title="✅ Recap"
# # ✅ Recap
#
# - Sequence models carry **causality**, **variable length**, and **compressed state** — that's the inductive bias.
# - The vanilla RNN's `h_t = tanh(W_x x_t + W_h h_{t-1})` is elegant but suffers **vanishing / exploding gradients** during BPTT.
# - **LSTM** fixes vanishing gradients with **additive cell state + gates**. **GRU** is a 25%-smaller equivalent.
# - Always pair RNN training with **gradient clipping**. Initialise the **forget-gate bias near 1**.
# - **Bidirectional**, **stacked**, and **variational dropout** are the three production extensions.
# - **Bahdanau / Luong attention** on top of LSTM seq2seq was the direct ancestor of the Transformer.
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


