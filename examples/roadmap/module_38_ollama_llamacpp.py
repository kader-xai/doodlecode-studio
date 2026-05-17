# doodlecode format-version: 2
# Auto-converted from module_38_ollama_llamacpp.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 38 Ollama Llamacpp"
# # Module 38 Ollama Llamacpp
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 38 — Ollama + llama.cpp"
# # Module 38 — Ollama + llama.cpp
#
# > So far every LLM in this course either ran in Hugging Face Transformers (Python only, slow on CPU) or pretended via flan-t5. Production teams use **`llama.cpp`** — a C++ inference engine that runs **quantised** models on CPU, Apple Silicon, and any GPU. **Ollama** is the friendly wrapper around it (`ollama run llama3`).
# >
# > This module is your introduction to **local-first LLMs** — the foundation for offline apps, on-prem deploys, edge devices, and any time you don't want to pay per token.
#
# ### What you'll cover
# 1. The local-LLM stack — llama.cpp, Ollama, GGUF, quantisation
# …


# %% [markdown] color=mint title="1 · The stack"
# # 1 · The stack
#
# ```
# ┌──────────────────────────────────────────┐
# │  Your Python app (OpenAI client SDK)     │
# └──────────────────────────────────────────┘
#                 ▼  HTTP (OpenAI-compatible)
# ┌──────────────────────────────────────────┐
# …


# %% [markdown] color=peach title="2 · Quantisation in 60 seconds"
# # 2 · Quantisation in 60 seconds
#
# A 7B model in fp16 = ~14 GB. Most laptops can't load that. Quantisation maps each weight to fewer bits.
#
# | Tag | Bits | Size (7B) | Quality vs fp16 | When to use |
# |---|---|---|---|---|
# | `Q8_0` | 8 | ~7.2 GB | ~99% | best quality you can ship to a 16 GB laptop |
# | `Q5_K_M` | 5 (mixed) | ~5.0 GB | ~98% | sweet spot for 8 GB RAM |
# …


# %% [markdown] color=violet title="3 · Install Ollama in Colab"
# # 3 · Install Ollama in Colab
#
# Ollama ships a Linux installer that drops the `ollama` binary at `/usr/local/bin/ollama` and a systemd unit. Colab has no systemd, so we run the daemon ourselves.


# %% color=amber title="!curl -fsSL https://ollama.com/install.sh | sh"
# @explain: Run this cell to see the output.
!curl -fsSL https://ollama.com/install.sh | sh


# %% color=rose title="launch the daemon in the background"
# @explain: launch the daemon in the background; logs to /tmp/ollama.log
# launch the daemon in the background; logs to /tmp/ollama.log
import subprocess, time, os
proc = subprocess.Popen(["ollama", "serve"],
                        stdout=open("/tmp/ollama.log","w"),
                        stderr=subprocess.STDOUT,
                        env={**os.environ, "OLLAMA_MODELS": "/root/.ollama/models"})
time.sleep(3)
!curl -s http://localhost:11434/api/version


# %% [markdown] color=lime title="Pull a tiny model so the demo finishes inside…"
# # Pull a tiny model so the demo finishes inside…
#
# Pull a tiny model so the demo finishes inside Colab's free tier.


# %% color=teal title="~1.3 GB Q4 quant"
# @explain: ~1.3 GB Q4 quant — runs on CPU at a few tok/s
# ~1.3 GB Q4 quant — runs on CPU at a few tok/s
!ollama pull qwen2.5:0.5b-instruct
!ollama list


# %% [markdown] color=sky title="4 · Calling Ollama from Python"
# # 4 · Calling Ollama from Python
#
# Ollama exposes an **OpenAI-compatible** HTTP API at `http://localhost:11434/v1`. So you can use the OpenAI Python SDK with no real OpenAI account.


# %% color=mint title="!pip -q install openai"
# @explain: Run this cell to see the output.
!pip -q install openai


# %% color=peach title="from openai import OpenAI"
# @explain: Run this cell to see the output.
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",   # any non-empty string works
)

resp = client.chat.completions.create(
    model="qwen2.5:0.5b-instruct",
    messages=[
        {"role": "system", "content": "You are a terse assistant. Answer in one sentence."},
        {"role": "user",   "content": "What is RAG?"},
    ],
)
print(resp.choices[0].message.content)


# %% [markdown] color=violet title="5 · Streaming + JSON mode"
# # 5 · Streaming + JSON mode
#


# %% color=amber title="streaming"
# @explain: streaming — yields tokens as they're generated
# streaming — yields tokens as they're generated
stream = client.chat.completions.create(
    model="qwen2.5:0.5b-instruct",
    messages=[{"role":"user","content":"List three reasons to run LLMs locally."}],
    stream=True,
)
for chunk in stream:
    delta = chunk.choices[0].delta.content
    if delta: print(delta, end="", flush=True)
print()


# %% color=rose title="JSON mode"
# @explain: JSON mode — guarantees the response parses as JSON (Ollama enforces this with grammar)
# JSON mode — guarantees the response parses as JSON (Ollama enforces this with grammar)
import json
resp = client.chat.completions.create(
    model="qwen2.5:0.5b-instruct",
    messages=[{"role":"user","content":"Extract: 'Bob is 32 and lives in Paris.' Reply with JSON keys name, age, city."}],
    response_format={"type": "json_object"},
)
print(json.loads(resp.choices[0].message.content))


# %% [markdown] color=lime title="6 · Bare metal — installing llama.cpp from source"
# # 6 · Bare metal — installing llama.cpp from source
#
# Ollama is a friendly wrapper. Underneath sits **llama.cpp**. Compile it yourself when you want maximum control (custom flags, latest features, embedding-only build).


# %% color=teal title="!git clone --depth 1…"
# @explain: Run this cell to see the output.
!git clone --depth 1 https://github.com/ggerganov/llama.cpp /content/llama.cpp
%cd /content/llama.cpp
!cmake -B build -DGGML_NATIVE=OFF -DLLAMA_CURL=OFF -DCMAKE_BUILD_TYPE=Release > /tmp/cmake.log 2>&1
!cmake --build build --config Release -j 4 --target llama-cli llama-server llama-embedding > /tmp/build.log 2>&1
!ls build/bin | head


# %% [markdown] color=sky title="Grab the same model directly as a GGUF file from…"
# # Grab the same model directly as a GGUF file from…
#
# Grab the same model directly as a GGUF file from Hugging Face (Ollama already downloaded it but it's stored in its own format).


# %% color=mint title="!pip -q install huggingface_hub"
# @explain: Run this cell to see the output.
!pip -q install huggingface_hub
from huggingface_hub import hf_hub_download
GGUF = hf_hub_download(
    repo_id="Qwen/Qwen2.5-0.5B-Instruct-GGUF",
    filename="qwen2.5-0.5b-instruct-q4_k_m.gguf",
)
print(GGUF)


# %% color=peach title="one-shot inference via the CLI"
# @explain: one-shot inference via the CLI
# one-shot inference via the CLI
!/content/llama.cpp/build/bin/llama-cli \
    -m {GGUF} \
    -p "Q: What is the capital of Japan? A:" \
    -n 32 -no-cnv 2>/dev/null | tail -n 5


# %% [markdown] color=violet title="7 · llama-server — the production HTTP layer"
# # 7 · llama-server — the production HTTP layer
#
# `llama-server` is llama.cpp's built-in OpenAI-compatible HTTP server. Same client code as before, no Ollama needed.


# %% color=amber title="launch llama-server in the background on port 8080"
# @explain: launch llama-server in the background on port 8080
# launch llama-server in the background on port 8080
import subprocess, time
srv = subprocess.Popen([
    "/content/llama.cpp/build/bin/llama-server",
    "-m", GGUF,
    "--host", "0.0.0.0", "--port", "8080",
    "-c", "2048",          # context length
    "-ngl", "0",           # GPU layers (0 = pure CPU; raise if you have a GPU)
], stdout=open("/tmp/llamasrv.log","w"), stderr=subprocess.STDOUT)
time.sleep(4)
!curl -s http://localhost:8080/v1/models | head


# %% color=rose title="client2 = OpenAI(base_url='http://localhost:8080/v1'"
# @explain: Run this cell to see the output.
client2 = OpenAI(base_url="http://localhost:8080/v1", api_key="x")
resp = client2.chat.completions.create(
    model="qwen2.5",
    messages=[{"role":"user","content":"In one line: what is GGUF?"}],
)
print(resp.choices[0].message.content)
srv.terminate()


# %% [markdown] color=lime title="8 · Picking a model"
# # 8 · Picking a model
#
# | Size | Decent at | Bad at | Memory (Q4) |
# |---|---|---|---|
# | **0.5 – 1.5 B** | classification, simple extraction, edge devices | reasoning, multi-step | ~0.4–1 GB |
# | **3 – 4 B** | chat, RAG over short docs, function-call helpers | long-context reasoning | ~2 GB |
# | **7 – 8 B** | general chat, code completion, tool use | hard math, long planning | ~4–5 GB |
# | **13 – 14 B** | better reasoning, long-form writing | needs GPU for fast inference | ~8 GB |
# …


# %% [markdown] color=teal title="9 · Embeddings via llama.cpp"
# # 9 · Embeddings via llama.cpp
#
# llama.cpp ships an `llama-embedding` binary and the server exposes `/v1/embeddings`. Useful when you want one runtime for both completions and embeddings.


# %% color=sky title="EMB_GGUF = hf_hub_download("
# @explain: Run this cell to see the output.
EMB_GGUF = hf_hub_download(
    repo_id="nomic-ai/nomic-embed-text-v1.5-GGUF",
    filename="nomic-embed-text-v1.5.Q4_K_M.gguf",
)
print(EMB_GGUF)


# %% color=mint title="start the embedding server"
# @explain: start the embedding server
# start the embedding server
import subprocess, time
emb_srv = subprocess.Popen([
    "/content/llama.cpp/build/bin/llama-server",
    "-m", EMB_GGUF, "--embeddings",
    "--host", "0.0.0.0", "--port", "8081",
    "-c", "2048",
], stdout=open("/tmp/embsrv.log","w"), stderr=subprocess.STDOUT)
time.sleep(4)


# %% color=peach title="eclient = OpenAI(base_url='http://localhost:8081/v1'"
# @explain: Run this cell to see the output.
eclient = OpenAI(base_url="http://localhost:8081/v1", api_key="x")
e = eclient.embeddings.create(model="nomic", input=["hello world", "the quick brown fox"])
import numpy as np
v = np.array([d.embedding for d in e.data])
print("shape:", v.shape, "  first 5 dims:", v[0,:5])
emb_srv.terminate()


# %% [markdown] color=violet title="10 · Production notes"
# # 10 · Production notes
#
# | Topic | What to know |
# |---|---|
# | **Modelfile** | Ollama's recipe for a model: base + system prompt + params. Build custom variants with `ollama create`. |
# | **GPU offload** | `-ngl N` (or `OLLAMA_NUM_GPU_LAYERS=N`). Push as many layers to VRAM as fit. |
# | **KV cache** | every request reserves `n_ctx × n_layers × n_kv_heads × head_dim × 2 × bits` bytes. Long context is expensive. |
# | **Continuous batching** | `llama-server` batches concurrent requests automatically — much higher throughput than serial. |
# …


# %% [markdown] color=amber title="✅ Recap"
# # ✅ Recap
#
# - **GGUF** = single-file model format used by llama.cpp + Ollama.
# - **Q4_K_M** is the default quant — ~4 bits/weight, ~97% quality, ~4× smaller than fp16.
# - **Ollama** = friendly wrapper; **llama-server** = bare metal; both speak OpenAI HTTP.
# - Keep your client code OpenAI-shaped → swap base_url to flip between Ollama, llama-server, vLLM, OpenAI.
# - Same engine handles **embeddings** with `--embeddings`.
#
# Next: **M39 — Unsloth fine-tuning** (LoRA on a free Colab GPU).


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


