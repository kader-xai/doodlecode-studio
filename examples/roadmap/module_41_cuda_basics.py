# doodlecode format-version: 2
# Auto-converted from module_41_cuda_basics.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 41 Cuda Basics"
# # Module 41 Cuda Basics
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 41 — CUDA Basics"
# # Module 41 — CUDA Basics
#
# > Every fast LLM kernel — FlashAttention, Mamba, Triton-fused MLPs, Unsloth's gradient checkpointing — bottoms out in **CUDA**. You don't need to write production CUDA C++ to be effective, but you *do* need to understand the **execution model**: threads, warps, blocks, grids, and the memory hierarchy. This module gives you that intuition by writing real kernels with **Numba** (CUDA from Python) and using **CuPy** (NumPy on GPU).
#
# > 🟡 Switch Colab to **GPU runtime** (Runtime → Change runtime type → T4). Without a GPU, almost nothing in this notebook will run.
#
# ### What you'll cover
# 1. Why GPUs are fast — parallelism, not clock speed
# …


# %% [markdown] color=mint title="1 · Why GPUs are fast"
# # 1 · Why GPUs are fast
#
# A modern CPU has ~16 cores, each running ~5 GHz, optimised for **low-latency single-thread** work.
# A T4 GPU has **2 560** CUDA cores at ~1.5 GHz, optimised for **massive throughput** on the same op applied to lots of data.
#
# | | CPU | GPU |
# |---|---|---|
# | Cores | ~16 | thousands |
# …


# %% [markdown] color=peach title="2 · Execution model"
# # 2 · Execution model
#
# ```
#             ┌──────────────────────────── grid ─────────────────────────────┐
#             │   ┌── block ──┐  ┌── block ──┐  ┌── block ──┐                 │
#             │   │ thread... │  │ thread... │  │ thread... │      ... up to  │
#             │   │ thread... │  │ thread... │  │ thread... │      thousands  │
#             │   └───────────┘  └───────────┘  └───────────┘                 │
# …


# %% [markdown] color=violet title="3 · Memory hierarchy"
# # 3 · Memory hierarchy
#
# | Level | Size | Latency | Scope |
# |---|---|---|---|
# | Registers | ~64 KB / SM | 1 cycle | per thread |
# | **Shared memory** | ~48–96 KB / block | ~5 cycles | per block |
# | L1 / L2 cache | MB | tens of cycles | per SM / GPU |
# | **Global memory (HBM)** | GB | hundreds of cycles | whole GPU |
# …


# %% [markdown] color=amber title="4 · First kernel — vector add"
# # 4 · First kernel — vector add
#


# %% color=rose title="!nvidia-smi | head -20"
# @explain: Run this cell to see the output.
!nvidia-smi | head -20


# %% color=lime title="!pip -q install numba cupy-cuda12x   # numba ships…"
# @explain: Run this cell to see the output.
!pip -q install numba cupy-cuda12x   # numba ships CUDA support; cupy-cuda12x for Colab T4


# %% color=teal title="launch config"
# @explain: launch config
import numpy as np
from numba import cuda

@cuda.jit
def vec_add(a, b, c):
    i = cuda.grid(1)             # global thread index along dim 0
    if i < a.size:
        c[i] = a[i] + b[i]

N = 1_000_000
a = np.random.randn(N).astype(np.float32)
b = np.random.randn(N).astype(np.float32)
c = np.empty_like(a)

# launch config
threads_per_block = 256
blocks_per_grid   = (N + threads_per_block - 1) // threads_per_block

vec_add[blocks_per_grid, threads_per_block](a, b, c)
print("max error vs numpy:", np.abs(c - (a+b)).max())


# %% [markdown] color=sky title="That's CUDA.** A function decorated with…"
# # That's CUDA.** A function decorated with…
#
# **That's CUDA.** A function decorated with `@cuda.jit`, indexed by `cuda.grid(1)`, launched with `kernel[blocks, threads](args)`. Same pattern in CUDA C++, just with more boilerplate.


# %% [markdown] color=mint title="5 · 2-D indexing — image kernel"
# # 5 · 2-D indexing — image kernel
#


# %% color=peach title="@cuda.jit"
# @explain: Run this cell to see the output.
@cuda.jit
def grayscale(rgb, gray):
    x, y = cuda.grid(2)
    if x < rgb.shape[0] and y < rgb.shape[1]:
        r, g, b = rgb[x, y, 0], rgb[x, y, 1], rgb[x, y, 2]
        gray[x, y] = 0.299*r + 0.587*g + 0.114*b   # ITU-R 601 luma

H, W = 1024, 1024
img = np.random.randint(0, 255, (H, W, 3), dtype=np.uint8).astype(np.float32)
out = np.empty((H, W), dtype=np.float32)

tpb = (16, 16)
bpg = ((H + tpb[0]-1)//tpb[0], (W + tpb[1]-1)//tpb[1])
grayscale[bpg, tpb](img, out)
print(out[:2,:5])


# %% [markdown] color=violet title="6 · Shared memory — tiled matmul"
# # 6 · Shared memory — tiled matmul
#
# The naïve matmul reads each element of `A` and `B` from global memory `N` times. The tiled version loads a tile into **shared memory** once, then every thread in the block reuses it. This is the single most important CUDA pattern.


# %% color=amber title="cooperative load of one tile per matrix"
# @explain: cooperative load of one tile per matrix
from numba import cuda, float32
TPB = 16   # tile size

@cuda.jit
def matmul_tiled(A, B, C):
    sA = cuda.shared.array((TPB, TPB), float32)
    sB = cuda.shared.array((TPB, TPB), float32)

    x, y = cuda.grid(2)
    tx, ty = cuda.threadIdx.x, cuda.threadIdx.y

    acc = 0.0
    for tile in range((A.shape[1] + TPB - 1) // TPB):
        # cooperative load of one tile per matrix
        if x < A.shape[0] and tile*TPB + ty < A.shape[1]:
            sA[tx, ty] = A[x, tile*TPB + ty]
        else:
            sA[tx, ty] = 0.0
        if tile*TPB + tx < B.shape[0] and y < B.shape[1]:
            sB[tx, ty] = B[tile*TPB + tx, y]
        else:
            sB[tx, ty] = 0.0

        cuda.syncthreads()           # ensure tile is fully loaded

        for k in range(TPB):
            acc += sA[tx, k] * sB[k, ty]

        cuda.syncthreads()           # before overwriting tiles

    if x < C.shape[0] and y < C.shape[1]:
        C[x, y] = acc

N = 256
A = np.random.randn(N, N).astype(np.float32)
B = np.random.randn(N, N).astype(np.float32)
C = np.zeros((N, N), dtype=np.float32)
matmul_tiled[((N+TPB-1)//TPB,(N+TPB-1)//TPB),(TPB,TPB)](A, B, C)
print("max error vs numpy:", np.abs(C - A@B).max())


# %% [markdown] color=rose title="7 · CuPy — NumPy on the GPU"
# # 7 · CuPy — NumPy on the GPU
#
# 90% of the time you don't *need* a custom kernel — you just want NumPy that runs on the GPU. **CuPy** is a drop-in replacement: same API, runs on CUDA, ~50–200× faster on big arrays.


# %% color=lime title="CPU"
# @explain: CPU
# @explain: GPU (warm-up first to compile cuBLAS handle)
import cupy as cp, time

x_cpu = np.random.randn(8192, 8192).astype(np.float32)
x_gpu = cp.asarray(x_cpu)

# CPU
t = time.time(); _ = x_cpu @ x_cpu; t_cpu = time.time() - t
# GPU (warm-up first to compile cuBLAS handle)
_ = x_gpu @ x_gpu; cp.cuda.Stream.null.synchronize()
t = time.time(); _ = x_gpu @ x_gpu; cp.cuda.Stream.null.synchronize()
t_gpu = time.time() - t

print(f"CPU matmul: {t_cpu:.2f}s   GPU matmul: {t_gpu:.4f}s   speedup: {t_cpu/t_gpu:.0f}×")


# %% [markdown] color=teal title="8 · Profiling"
# # 8 · Profiling
#


# %% color=sky title="CUDA events"
# @explain: CUDA events — accurate kernel timing
# CUDA events — accurate kernel timing
start = cuda.event(); end = cuda.event()
start.record()
vec_add[blocks_per_grid, threads_per_block](a, b, c)
end.record(); end.synchronize()
print(f"vec_add took {cuda.event_elapsed_time(start, end):.3f} ms")


# %% color=mint title="nvidia-smi gives you live GPU utilisation"
# @explain: nvidia-smi gives you live GPU utilisation
# nvidia-smi gives you live GPU utilisation
!nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total --format=csv


# %% [markdown] color=peach title="Occupancy** = (active warps per SM) / (max warps…"
# # Occupancy** = (active warps per SM) / (max warps…
#
# **Occupancy** = (active warps per SM) / (max warps per SM). High occupancy hides memory latency. Tools: NSight Compute (`ncu`), CUPTI, `numba.cuda.detect()`.


# %% [markdown] color=violet title="9 · Bridging to PyTorch — and why **Triton** matters"
# # 9 · Bridging to PyTorch — and why **Triton** matters
#
# PyTorch already exposes thousands of tuned CUDA kernels via `torch.matmul`, `torch.nn.functional.scaled_dot_product_attention`, etc. You write a custom kernel only when:
#
# 1. The op doesn't exist (e.g. **FlashAttention** before it landed in PyTorch)
# 2. You're fusing several ops to skip global-memory round-trips
# 3. You're squeezing a few extra % out of a hot path
#
# …


# %% [markdown] color=amber title="10 · When to write CUDA — and when not to"
# # 10 · When to write CUDA — and when not to
#
# | Situation | What to do |
# |---|---|
# | Standard ML ops (matmul, conv, attention) | Use PyTorch / TF — already optimal |
# | Custom op, performance matters | **Write it in Triton** — 90% of CUDA's speed, 10× less code |
# | Critical hot path, every µs counts | Drop to CUDA C++ + cuBLAS / cuDNN |
# | Just want NumPy-on-GPU | **CuPy** — done in one line |
# …


# %% [markdown] color=rose title="✅ Recap"
# # ✅ Recap
#
# - A GPU has **thousands of cores** running the **same kernel** on different data.
# - Launch shape: `kernel[blocks, threads](args)`. Total threads = blocks × threads.
# - The memory hierarchy is the whole performance story — **load to shared once, reuse**.
# - **CuPy** = NumPy on GPU. **Numba** = CUDA from Python. **Triton** = the modern way to write fast custom ML kernels.
# - Don't write CUDA unless PyTorch / Triton can't already.
#
# Next: **M42 — Vector DB comparison** (FAISS · Pinecone · Weaviate · Qdrant).


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


