# doodlecode format-version: 2
# Auto-converted from module_66_distributed_training.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 66 Distributed Training"
# # Module 66 Distributed Training
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 66 — Distributed Training"
# # Module 66 — Distributed Training
#
# > M57 trained a tiny GPT on a single CPU. M39 fine-tuned a 7B on one GPU with Unsloth. **Real** pretraining and serious fine-tuning need **many GPUs talking to each other**. This module is the map of how that's done: **DDP**, **FSDP**, **DeepSpeed ZeRO**, plus **tensor + pipeline parallelism** for frontier-scale models. You won't run a 4-GPU job from Colab — but every snippet here is production-shaped code you can drop onto a real cluster.
#
# ### What you'll cover
# 1. **Why** you need distribution — the memory math
# 2. **`torch.distributed` primitives** — process groups, all-reduce, NCCL
# 3. **DDP** — Distributed Data Parallel (the workhorse)
# …


# %% [markdown] color=mint title="1 · The memory math"
# # 1 · The memory math
#
# To train a model in fp16/bf16 with AdamW you need, **per parameter**:
#
# | Tensor | Bytes / param (mixed precision) | Why |
# |---|---|---|
# | Weights (fp16) | 2 | the model |
# | Gradients (fp16) | 2 | one per backward pass |
# …


# %% [markdown] color=peach title="2 · `torch.distributed` primitives — the layer everything sits on"
# # 2 · `torch.distributed` primitives — the layer everything sits on
#


# %% color=violet title="every process learns its identity from env vars set…"
# @explain: every process learns its identity from env vars set by the launcher
# @explain: initialise the process group over NCCL (or "gloo" on CPU-only)
ddp_setup_sketch = '''
import os, torch, torch.distributed as dist

# every process learns its identity from env vars set by the launcher
local_rank = int(os.environ["LOCAL_RANK"])      # 0..gpus_per_node-1
world_size = int(os.environ["WORLD_SIZE"])      # total GPUs across all nodes
rank       = int(os.environ["RANK"])            # global rank

# initialise the process group over NCCL (or "gloo" on CPU-only)
dist.init_process_group(backend="nccl")
torch.cuda.set_device(local_rank)
'''
print(ddp_setup_sketch)


# %% [markdown] color=amber title="The five collective operations everything else is…"
# # The five collective operations everything else is…
#
# **The five collective operations everything else is built on.**
#
# | Operation | What it does | Where it shows up |
# |---|---|---|
# | **`all_reduce(t)`** | sum (or avg) `t` across every rank, write the result back to every rank | DDP gradient sync |
# | **`broadcast(t, src)`** | rank `src` sends `t` to everyone | spreading initial weights |
# | **`all_gather`** | every rank collects everyone's tensor into a list | FSDP unsharding |
# | **`reduce_scatter`** | sum across ranks, then keep only a shard on each | FSDP gradient sharding |
# …


# %% [markdown] color=rose title="3 · DDP — Distributed Data Parallel"
# # 3 · DDP — Distributed Data Parallel
#


# %% [markdown] color=lime title="The simplest distributed strategy.** Each GPU keeps…"
# # The simplest distributed strategy.** Each GPU keeps…
#
# **The simplest distributed strategy.** Each GPU keeps a full copy of the model. Each batch is split across GPUs (one micro-batch per GPU). After backward, gradients are **all-reduced** across GPUs (averaged). Optimiser steps locally, in lockstep with everyone else.
#
# ```
#    GPU 0:  full model + grads + opt state    ←┐
#    GPU 1:  full model + grads + opt state    │ all-reduce gradients every step
#    GPU 2:  full model + grads + opt state    │
#    GPU 3:  full model + grads + opt state    ←┘
# ```


# %% color=teal title="ddp_loop = '''"
# @explain: Run this cell to see the output.
ddp_loop = '''
import torch
import torch.nn as nn
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data.distributed import DistributedSampler

dist.init_process_group(backend="nccl")
local_rank = int(os.environ["LOCAL_RANK"])
torch.cuda.set_device(local_rank)

model = MyTransformer().cuda(local_rank)
model = DDP(model, device_ids=[local_rank])              # wraps the model

sampler = DistributedSampler(dataset, shuffle=True)      # each rank sees a unique slice
loader  = DataLoader(dataset, batch_size=32, sampler=sampler)

optim = torch.optim.AdamW(model.parameters(), lr=3e-5)

for epoch in range(num_epochs):
    sampler.set_epoch(epoch)                             # different shuffle each epoch
    for x, y in loader:
        x = x.cuda(local_rank); y = y.cuda(local_rank)
        optim.zero_grad()
        loss = model(x, labels=y).loss                    # forward through DDP-wrapped model
        loss.backward()                                   # backward → DDP all-reduces grads
        optim.step()
'''
print(ddp_loop)


# %% [markdown] color=sky title="Three places DDP differs from a single-GPU loop"
# # Three places DDP differs from a single-GPU loop
#
# **Three places DDP differs from a single-GPU loop.**
# 1. `DDP(model)` — wrap once. After this, `loss.backward()` triggers an asynchronous all-reduce of every gradient.
# 2. `DistributedSampler` — gives each rank a unique slice of the dataset (no overlap).
# 3. `sampler.set_epoch(epoch)` — required, otherwise every epoch sees the same shuffle.
#
# **When DDP wins.** Model fits on one GPU; you want linear throughput scale-out. This is most fine-tuning workloads under ~7B.
#
# **When DDP breaks.** Model *doesn't* fit on one GPU — every rank still holds the full weights+grads+optimiser. That's where FSDP comes in.


# %% [markdown] color=mint title="4 · FSDP — Fully Sharded Data Parallel"
# # 4 · FSDP — Fully Sharded Data Parallel
#


# %% [markdown] color=peach title="The 2022+ default for large-model training.**…"
# # The 2022+ default for large-model training.**…
#
# **The 2022+ default for large-model training.** Instead of replicating the model on every GPU, **shard** the parameters, gradients, and optimiser state across all GPUs. Each rank holds only its **slice** of each tensor; before a layer's forward pass it `all_gather`s the full weights from every other rank, runs the forward, then immediately re-shards.
#
# ```
#    layer i weights:    [shard₀, shard₁, shard₂, shard₃]
#                         GPU 0   GPU 1   GPU 2   GPU 3
#    forward i:   all_gather → full weights on every rank → matmul → re-shard
#    backward i:  full weights → grad → reduce_scatter → per-rank grad shard
# ```
# …


# %% color=violet title="Wrap one transformer block at a time so each block…"
# @explain: Wrap one transformer block at a time so each block can be re-sharded independently
fsdp_setup = '''
from torch.distributed.fsdp import FullyShardedDataParallel as FSDP
from torch.distributed.fsdp import MixedPrecision, BackwardPrefetch
from torch.distributed.fsdp.wrap import transformer_auto_wrap_policy
from functools import partial

mp_policy = MixedPrecision(
    param_dtype  = torch.bfloat16,
    reduce_dtype = torch.bfloat16,
    buffer_dtype = torch.bfloat16,
)

# Wrap one transformer block at a time so each block can be re-sharded independently
auto_wrap = partial(
    transformer_auto_wrap_policy,
    transformer_layer_cls={ TransformerBlock },              # your block class from M56/M61
)

model = FSDP(
    model.cuda(),
    auto_wrap_policy=auto_wrap,
    mixed_precision=mp_policy,
    backward_prefetch=BackwardPrefetch.BACKWARD_PRE,         # overlap comms with compute
)
'''
print(fsdp_setup)


# %% [markdown] color=amber title="FSDP knobs that matter"
# # FSDP knobs that matter
#
# **FSDP knobs that matter.**
# - **`auto_wrap_policy`** — at what granularity to shard. Per-transformer-block is the default for LLMs.
# - **`MixedPrecision`** — store params in bf16, do the reduce in bf16. Saves bandwidth + memory.
# - **`BackwardPrefetch`** — overlap the gather of layer `i-1` with the backward of layer `i`. Big throughput win.
# - **`activation_checkpointing`** — recompute activations during backward instead of storing them. Trades 1× FLOPs for ~10× activation memory.
# - **`CPUOffload(offload_params=True)`** — keep param shards on CPU when not in use. For when you're memory-starved even after sharding.


# %% [markdown] color=rose title="5 · DeepSpeed ZeRO — same idea, different knob"
# # 5 · DeepSpeed ZeRO — same idea, different knob
#


# %% [markdown] color=lime title="DeepSpeed's **ZeRO** (Zero Redundancy Optimizer)…"
# # DeepSpeed's **ZeRO** (Zero Redundancy Optimizer)…
#
# DeepSpeed's **ZeRO** (Zero Redundancy Optimizer) predated FSDP and is the *other* dominant strategy. It exposes the sharding granularity as **three stages**:
#
# | Stage | Shards | Memory ratio | Notes |
# |---|---|---|---|
# | **ZeRO-1** | optimiser state only | ~4× saving | grads + params still replicated |
# | **ZeRO-2** | + gradients | ~8× saving | params still replicated |
# | **ZeRO-3** | + parameters | full DDP→FSDP equivalent | shard everything, just like FSDP |
# | **ZeRO-Infinity** | + offload to NVMe | ~10× more | for truly massive models on small clusters |
# …


# %% [markdown] color=teal title="6 · Tensor + Pipeline parallelism — when one *layer* > one GPU"
# # 6 · Tensor + Pipeline parallelism — when one *layer* > one GPU
#
# DDP/FSDP/ZeRO solve memory by sharding across the **batch** dimension (data-parallel). They all assume one **layer's forward pass** fits on one GPU. For frontier models (70 B in fp32, 405 B at any precision) that's not true. Two further axes:
#
# ### Tensor Parallelism (TP) — Megatron-LM
# Split each matrix multiply across `k` GPUs. The Q projection in attention becomes `Q = x @ W_q`; with TP=2, we split `W_q` column-wise and run `Q_part = x @ W_q_shard` on each of the 2 GPUs, then `all_gather` the result.
#
# ```
# …


# %% [markdown] color=sky title="7 · 3D parallelism — what frontier labs run"
# # 7 · 3D parallelism — what frontier labs run
#
# For **Llama 3.1 405B** / **DeepSeek-V3** / **GPT-4-class** models you combine all three axes:
#
# ```
#                 ┌──── data-parallel replicas (FSDP / ZeRO-3) ────┐
#                 ▼                                                ▼
#    ┌─ tensor-parallel within node (8× H100, NVLink) ──┐    ┌─ TP ─┐
# …


# %% [markdown] color=mint title="8 · Launchers — how the processes actually start"
# # 8 · Launchers — how the processes actually start
#
# You never call `python my_train.py`. You launch with one of these:
#
# ### `torchrun` (PyTorch built-in)
# ```bash
# torchrun \
#     --nproc_per_node=4 \
# …


# %% [markdown] color=peach title="9 · The small wins that compose"
# # 9 · The small wins that compose
#
# These are **orthogonal** to the parallelism strategy and stack on top of any of DDP/FSDP/DeepSpeed:
#
# | Trick | What it saves | When to enable |
# |---|---|---|
# | **Mixed precision** (`bf16`/`fp16`) | 2× memory + 2-3× speed | always for modern GPUs |
# | **Gradient accumulation** (`k=8`) | scales effective batch size on small GPUs | always — first knob to turn |
# …


# %% [markdown] color=violet title="10 · Practical recipe — fine-tune Llama-3-8B on 4× A100"
# # 10 · Practical recipe — fine-tune Llama-3-8B on 4× A100
#
# The realistic 2026 default for a 7-8B SFT or DPO run, using HuggingFace `accelerate` + `trl`:
#
# ```bash
# # 1. Create accelerate config
# $ accelerate config
# # answer: multi-GPU, 4 GPUs, FSDP yes, transformer_auto_wrap, bf16
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


