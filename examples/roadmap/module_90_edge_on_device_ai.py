# doodlecode format-version: 2
# Auto-converted from module_90_edge_on_device_ai.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 90 Edge On Device Ai"
# # Module 90 Edge On Device Ai
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 90 — Edge / On-device AI"
# # Module 90 — Edge / On-device AI
#
# > Every model in M1-M89 ran in a datacenter. This final module is about running them **on the user's device** — iPhone, Pixel, Mac, AR glasses, drones, ESP32 microcontrollers. The 2024-2026 wave of on-device AI (**Apple Intelligence**, **Gemini Nano**, **Phi-3.5-mini**, **Llama-3.2-1B/3B**, **Qwen-2.5-0.5B**, **MLC-LLM**, **llama.cpp**, **WebGPU**, **TFLite**, **Core ML**, **ONNX Runtime**) crossed the line where a usable 3B LLM fits in 2 GB RAM at >10 tok/s on a $200 phone. By the end of this module you'll know **which model + which runtime + which quantization** for every device class, the **5 quantization formats that matter** (INT8 / INT4 / GPTQ / AWQ / GGUF k-quants), and how to ship a real on-device LLM behind a private, offline UX.
#
# ### What you'll cover
# 1. **Why edge AI now** — privacy, latency, cost, offline, regulation
# 2. The **device taxonomy** — phone-class → laptop-class → MCU-class
# 3. **Quantization deep dive** — INT8, INT4, GPTQ, AWQ, GGUF k-quants
# …


# %% [markdown] color=mint title="1 · Why edge AI now"
# # 1 · Why edge AI now
#
# Four forces aligned in 2024-2026 to push inference off the cloud and onto the device:
#
# | Force | What it means | Example |
# |---|---|---|
# | **Privacy** | Voice / photo / health data never leaves the device | Apple Intelligence ("Private Cloud Compute" only when on-device can't handle it) |
# | **Latency** | No round-trip to a datacenter; <100 ms voice / camera UX | Gemini Nano on Pixel · Siri 2.0 |
# …


# %% [markdown] color=peach title="2 · The device taxonomy"
# # 2 · The device taxonomy
#
# Edge isn't one tier — it's five, and each has a different model / runtime fit.
#
# | Tier | Examples | Compute | RAM | What fits |
# |---|---|---|---|---|
# | **Laptop / desktop** | M-series Mac, RTX 4070+, Snapdragon X Elite | 40-80 TOPS NPU + 10-30 TFLOPS GPU | 16-128 GB | 70B INT4 (Mac), 14B FP16, full Llama-3-70B-Q4 with llama.cpp |
# | **Flagship phone / tablet** | iPhone 16/17 · Pixel 9/10 · S25 · iPad M2/M4 | 17-38 TOPS NPU | 8-16 GB | **3B-8B INT4** (Apple ~3B, Gemini Nano 3.25B, Phi-3.5, Llama-3.2-3B) |
# …


# %% [markdown] color=violet title="3 · Quantization deep dive"
# # 3 · Quantization deep dive
#
# Quantization replaces fp16/fp32 weights with k-bit integers. It's THE technique that made edge LLMs viable.
#
# **The five formats that matter in 2026:**
#
# | Format | Bits | Calibration | Where it wins |
# |---|---|---|---|
# …


# %% color=amber title="llama.cpp / GGUF flow"
# @explain: llama.cpp / GGUF flow — convert + quantize a 3B model
# @explain: (requires ggerganov/llama.cpp built; ~5 min total for a 3B)
# @explain: 1
# @explain: python3 llama.cpp/convert_hf_to_gguf.py meta-llama/Llama-3.2-3B-Instruct \
# @explain: --outfile llama3.2-3b.f16.gguf
# llama.cpp / GGUF flow — convert + quantize a 3B model
# (requires ggerganov/llama.cpp built; ~5 min total for a 3B)

# 1. Convert HF model → GGUF fp16
# python3 llama.cpp/convert_hf_to_gguf.py meta-llama/Llama-3.2-3B-Instruct \
#         --outfile llama3.2-3b.f16.gguf

# 2. Quantize to a smaller k-quant
# ./llama-quantize llama3.2-3b.f16.gguf llama3.2-3b.Q4_K_M.gguf Q4_K_M
#                                                                ^^^^^^
#                              Q2_K   = ~2.6 GB, slight quality loss
#                              Q3_K_M = ~3.3 GB, ok
#                              Q4_K_M = ~4.7 GB, sweet spot for 8B
#                              Q5_K_M = ~5.5 GB
#                              Q6_K   = ~6.6 GB, near-lossless
#                              Q8_0   = ~8.5 GB, lossless reference

# 3. Run with llama.cpp (CLI or server) on phone, Mac, web, Pi:
# ./llama-cli -m llama3.2-3b.Q4_K_M.gguf -p "Hello" -n 64 -t 4


# %% [markdown] color=rose title="4 · Pruning + structured sparsity"
# # 4 · Pruning + structured sparsity
#
# Quantization reduces bits-per-weight. **Pruning** removes weights entirely. The combination of the two is where serious edge gains live.
#
# | Method | Idea | Speedup (real HW) |
# |---|---|---|
# | **Magnitude pruning** | Zero the smallest-|w| 50-90% of weights, fine-tune | ~free in storage; rarely speeds inference (irregular) |
# | **2:4 structured sparsity** (NVIDIA Ampere+) | Of every 4 consecutive weights, exactly 2 are zero | **2× GEMM throughput** on A100/H100/Blackwell |
# …


# %% [markdown] color=lime title="5 · Speculative decoding + Medusa + EAGLE-2"
# # 5 · Speculative decoding + Medusa + EAGLE-2
#
# Quant + prune shrink the model. **Speculative decoding** speeds up *each generated token* — critical at edge, where memory bandwidth is the bottleneck.
#
# ```
# Standard:        decode 1 token  ──>  full forward pass through 8B model   = 100 ms
# Speculative:     draft 5 tokens with a small "draft" model   = 10 ms
#                  verify all 5 with one batched forward of 8B  = 110 ms
# …


# %% [markdown] color=teal title="6 · The 2026 mobile LLM zoo"
# # 6 · The 2026 mobile LLM zoo
#
# Open + closed small models that actually fit on devices:
#
# | Model | Size | License | Notes |
# |---|---|---|---|
# | **Apple "AFM-on-device"** | ~3B | Closed | Powers Apple Intelligence on iPhone 16+; ~16 TOPS Neural Engine |
# | **Gemini Nano-3 / Nano-XS** | 1.8B / 3.25B | Closed | Powers Pixel 9+ AICore + Chrome's built-in `window.ai` |
# …


# %% [markdown] color=sky title="7 · The runtime zoo"
# # 7 · The runtime zoo
#
# Every edge target has 2-3 viable runtimes. The picks below are the 2026 defaults.
#
# | Runtime | Maintainer | Best for | Why |
# |---|---|---|---|
# | **llama.cpp** | Gerganov + 1500 contribs | macOS / Linux / Windows / Android / Termux / Raspberry Pi / WebAssembly | **The reference on-device LLM runtime.** Pure C/C++, no Python, GGUF format, Metal / CUDA / Vulkan / SYCL / OpenCL / CPU back-ends |
# | **MLX** | Apple | Mac (M-series) | Native Metal; share buffer with the GPU; the de-facto Mac LLM stack |
# …


# %% [markdown] color=mint title="8 · NPUs — the hardware running this stack"
# # 8 · NPUs — the hardware running this stack
#
# NPUs are dedicated tensor accelerators outside the CPU/GPU. Every 2025+ phone, Mac, and "Copilot+ PC" has one.
#
# | NPU | TOPS (INT8) | Notable in | Programming |
# |---|---|---|---|
# | **Apple Neural Engine (ANE) — A17/A18/M3/M4** | 17-38 | iPhone 15+, M-Mac | Core ML / MLX (no public ANE kernels) |
# | **Qualcomm Hexagon (Snapdragon 8 Gen 3 / 8 Elite)** | 45-75 | Pixel-non-Tensor, S24/S25, ROG Phone | QNN SDK, Qualcomm AI Hub |
# …


# %% [markdown] color=peach title="9 · WebGPU + WebLLM — a 3B model in a browser tab"
# # 9 · WebGPU + WebLLM — a 3B model in a browser tab
#
# The single most over-the-air-deployable runtime is **the user's browser**. WebGPU (shipped in Chrome / Edge / Safari TP / Firefox-nightly) gives JavaScript direct access to the device GPU; **WebLLM** + **transformers.js** turn that into a fully-offline LLM.
#
# ```html
# <!doctype html><script type="module">
# import * as webllm from "https://esm.run/@mlc-ai/web-llm";
#
# …


# %% [markdown] color=violet title="10 · The 90-module wrap-up — what you can build now"
# # 10 · The 90-module wrap-up — what you can build now
#
# You've gone, in 90 modules and ~7 phases, from `import pandas` to:
#
# | You can ship... | Built on modules |
# |---|---|
# | **A production ML pipeline** (ingest → feature store → CI/CD → monitoring) | M1-M17, M71-M76 |
# | **All six classical model families from scratch** + sklearn deployment | M5-M18 |
# …


# %% color=amber title="Final on-device LLM smoke-test"
# @explain: Final on-device LLM smoke-test (laptop or Colab → save to phone)
# @explain: Pure llama.cpp Python bindings — no torch, no transformers, no GPU
# Final on-device LLM smoke-test (laptop or Colab → save to phone)
# Pure llama.cpp Python bindings — no torch, no transformers, no GPU.

# !pip install -q llama-cpp-python
# !wget -q https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf

from llama_cpp import Llama

llm = Llama(
    model_path="Llama-3.2-3B-Instruct-Q4_K_M.gguf",
    n_ctx=4096,
    n_threads=4,            # phone CPU has ~4-8 perf cores
    n_gpu_layers=0,         # CPU-only path; set -1 to offload all to Metal/CUDA
    verbose=False,
)

out = llm.create_chat_completion(
    messages=[
        {"role": "system", "content": "You are a concise assistant."},
        {"role": "user",   "content": "In one sentence: why does edge AI matter?"},
    ],
    temperature=0.2,
    max_tokens=128,
)
print(out["choices"][0]["message"]["content"])


# %% [markdown] color=rose title="✅ Recap"
# # ✅ Recap
#
# - **Edge AI cleared the line** in 2024-2026: a 3B INT4 LLM in ~1.5 GB at >10 tok/s on a $200 phone.
# - **Five device tiers**: laptop / flagship-phone / mid-phone / wearable / MCU — each pairs with a specific model + runtime.
# - **Quantization is mandatory** at edge. The five formats that matter: **INT8 · GPTQ · AWQ · GGUF k-quants · QAT (LLM.int8 / QLoRA / FP4)**. GGUF k-quants are the on-device default.
# - **Pruning + 2:4 + Wanda + SparseGPT** stack with quantization on GPUs; mostly dense quant on phones.
# - **Speculative decoding** (Medusa · EAGLE-2 · Lookahead) gets 2-4× speedups — critical at edge.
# - **2026 mobile zoo**: Apple AFM-on-device · Gemini Nano · Phi-3.5/4 · Llama-3.2-1B/3B · Qwen-2.5-0.5B/1.5B/3B · SmolLM2 · Gemma-3 · MobileLLM.
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


