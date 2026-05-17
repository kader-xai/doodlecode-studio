# doodlecode format-version: 2
# Auto-converted from module_77_gpu_networking_nvlink_ib_roce.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 77 Gpu Networking Nvlink Ib Roce"
# # Module 77 Gpu Networking Nvlink Ib Roce
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 77 — GPU Networking"
# # Module 77 — GPU Networking
#
# > M66 said "all-reduce gradients across GPUs." This module is **how that line actually happens**. Below your `torch.distributed` call sits a stack: **NCCL → CUDA IPC → NVLink (within a node) → RDMA over InfiniBand or RoCE (between nodes)**. Get any layer wrong and your 256-GPU training run becomes a 100-GPU training run with the other 156 GPUs eating coffee. Get them right and you hit the **70-80 % of theoretical peak FLOPs** that frontier labs report.
# >
# > This is the network half of distributed training. There's no Colab demo — you can't fake a 400 Gb/s fabric — but every command and tuning knob here is exactly what you type in production.
#
# ### What you'll cover
# 1. The hierarchy — why "all-reduce" is a multi-layer problem
# …


# %% [markdown] color=mint title="1 · Why all-reduce is a stack"
# # 1 · Why all-reduce is a stack
#
# ```
#    Python                  loss.backward(); optimizer.step()
#         │
#         ▼
#    PyTorch / JAX        torch.distributed → all_reduce
#         │
# …


# %% [markdown] color=peach title="2 · NCCL — the collective library"
# # 2 · NCCL — the collective library
#
# **NVIDIA Collective Communications Library**. Every framework that does multi-GPU training calls into NCCL underneath: PyTorch DDP / FSDP, JAX, DeepSpeed, Megatron, vLLM (M44), TensorRT-LLM.
#
# | Collective | What it does | Where it shows up |
# |---|---|---|
# | **AllReduce** | sum (or avg) a tensor across all ranks; everyone gets the result | DDP gradient sync (M66 §3) |
# | **AllGather** | every rank concatenates everyone's shard into the full tensor | FSDP unsharding (M66 §4) |
# …


# %% [markdown] color=violet title="3 · NVLink + NVSwitch — intra-node"
# # 3 · NVLink + NVSwitch — intra-node
#
# When two GPUs in the same server need to talk, they go over **NVLink** — NVIDIA's point-to-point GPU interconnect.
#
# | Generation | Per-link | Per-GPU aggregate | Used by |
# |---|---|---|---|
# | NVLink 3 | 50 GB/s | 600 GB/s | A100 |
# | NVLink 4 | 100 GB/s | 900 GB/s | H100 |
# …


# %% color=amber title="What the output of `nvidia-smi topo -m` looks like…"
# @explain: What the output of `nvidia-smi topo -m` looks like on an 8x H100 box
# What the output of `nvidia-smi topo -m` looks like on an 8x H100 box.
example_topo = '''
        GPU0   GPU1   GPU2   GPU3   GPU4   GPU5   GPU6   GPU7    CPU Affinity
GPU0     X     NV18   NV18   NV18   NV18   NV18   NV18   NV18    0-47
GPU1    NV18    X     NV18   NV18   NV18   NV18   NV18   NV18    0-47
GPU2    NV18   NV18    X     NV18   NV18   NV18   NV18   NV18    0-47
...
Legend:
  X    = Self
  NV#  = Connection via that many NVLinks (NV18 = 18 NVLinks)
  PIX  = Through a PCIe switch
  PHB  = PCIe host bridge
  SYS  = Across NUMA nodes / sockets — SLOW
'''
print(example_topo)


# %% [markdown] color=rose title="4 · PCIe — the slow fallback"
# # 4 · PCIe — the slow fallback
#
# If two GPUs don't share NVLink (or you're on a workstation), they fall back to **PCIe**:
#
# | PCIe gen | Per-lane | x16 lane GPU |
# |---|---|---|
# | Gen 3 | 1 GB/s | 16 GB/s |
# | Gen 4 | 2 GB/s | 32 GB/s |
# …


# %% [markdown] color=lime title="5 · InfiniBand — the gold-standard inter-node fabric"
# # 5 · InfiniBand — the gold-standard inter-node fabric
#
# When the model doesn't fit on one node (M66 §6 — tensor + pipeline), GPUs on different machines need to talk. **InfiniBand (IB)** is the dominant fabric.
#
# | Generation | Per-port | Notes |
# |---|---|---|
# | HDR | 200 Gb/s | A100-era |
# | **NDR** | **400 Gb/s** | **H100 reference** |
# …


# %% [markdown] color=teal title="6 · RoCE v2 — RDMA over Ethernet"
# # 6 · RoCE v2 — RDMA over Ethernet
#
# InfiniBand is fast but **expensive** and requires a parallel cable plant. **RoCE v2** (RDMA over Converged Ethernet) gives you RDMA semantics over **standard 400/800 Gb Ethernet** with a few requirements:
#
# | Requirement | Why |
# |---|---|
# | **PFC** (Priority Flow Control) | makes Ethernet lossless for the RDMA traffic class |
# | **ECN** (Explicit Congestion Notification) + **DCQCN** | congestion control |
# …


# %% [markdown] color=sky title="7 · GPUDirect RDMA — the trick that makes the rest work"
# # 7 · GPUDirect RDMA — the trick that makes the rest work
#
# Without GPUDirect, sending a tensor from GPU 0 on node A to GPU 0 on node B looks like:
#
# ```
#    GPU 0 (A)  →  pinned host RAM  →  NIC  →  network  →  NIC  →  pinned host RAM  →  GPU 0 (B)
#        (1 copy)        (1 copy)             (transfer)       (1 copy)        (1 copy)
# ```
# …


# %% [markdown] color=mint title="8 · Rail-optimised topology — how DGX racks are wired"
# # 8 · Rail-optimised topology — how DGX racks are wired
#
# The trick that makes 8-GPU servers scale into 1024-GPU pods.
#
# ```
#                               ┌──── Spine switches (IB or RoCE) ────┐
#                               │                                    │
#                           ─────────────────── fat-tree ──────────────
# …


# %% [markdown] color=peach title="9 · Tuning NCCL — env vars + benchmarks"
# # 9 · Tuning NCCL — env vars + benchmarks
#
# ### Env vars you'll set in production
#
# ```bash
# # Tell NCCL what to use
# export NCCL_DEBUG=INFO               # print topology + algorithm choices once at startup
# export NCCL_DEBUG_SUBSYS=ALL         # very verbose (use sparingly)
# …


# %% [markdown] color=violet title="10 · The 2025-26 fabric landscape"
# # 10 · The 2025-26 fabric landscape
#
# ```
#                             INTRA-NODE                       INTER-NODE
#                        ────────────────────             ────────────────────
#    2020   A100         NVLink 3      600 GB/s/GPU       HDR    200 Gb/s
#    2022   H100         NVLink 4      900 GB/s/GPU       NDR    400 Gb/s
#    2024   H200         NVLink 4      900 GB/s/GPU       NDR    400 Gb/s
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


