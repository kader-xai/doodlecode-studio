# doodlecode format-version: 2
# Auto-converted from module_44_vllm.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 44 Vllm"
# # Module 44 Vllm
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 44 — vLLM"
# # Module 44 — vLLM
#
# > Ollama (M38) is great for laptops and a single user. **vLLM** is what you run when you have a fleet of GPUs and thousands of concurrent users. It's the **production inference server** that powers most "OpenAI-compatible" deployments — Together AI, Anyscale, Fireworks, plus thousands of self-hosted setups. Its core trick is **PagedAttention** (manage the KV-cache like an OS manages memory), which delivers ~24× the throughput of naive HuggingFace generate() at the same latency.
#
# ### What you'll cover
# 1. Why vLLM — PagedAttention + continuous batching in plain English
# 2. Throughput vs latency — what you're really optimising
# 3. Setup — install vLLM (GPU runtime required)
# …


# %% [markdown] color=mint title="1 · Why vLLM — PagedAttention + continuous batching"
# # 1 · Why vLLM — PagedAttention + continuous batching
#
# A naive HuggingFace `model.generate(...)` has two problems at scale:
#
# **Problem 1: KV-cache fragmentation.** Each request reserves a contiguous block big enough for its **maximum** possible output (say 2048 tokens). Most requests finish at 200 tokens → 90% of the GPU's KV memory is wasted on holes.
#
# → **PagedAttention.** vLLM treats KV memory like an OS treats RAM: split it into fixed-size **pages** (typically 16 tokens), allocate pages on-demand as the sequence grows. No more fragmentation, ~3-5× more concurrent requests fit.
#
# …


# %% [markdown] color=peach title="2 · Throughput vs latency"
# # 2 · Throughput vs latency
#
# | You care about | What to tune |
# |---|---|
# | **TTFT** — time to first token (chat UI feel) | small batch, high `gpu_memory_utilization`, **prefix cache** for system prompts |
# | **TPOT** — time per output token (streaming pace) | enable **speculative decoding**, ensure tensor-parallel covers attention |
# | **Throughput** — total tokens/sec across all users | big `max_num_seqs`, enable **chunked prefill**, batch many requests |
# | **Cost / request** | smaller model, AWQ/GPTQ quant, `--enforce-eager=False`, multi-LoRA on one base |
# …


# %% [markdown] color=violet title="3 · Setup"
# # 3 · Setup
#


# %% color=amber title="!nvidia-smi | head -8"
# @explain: Run this cell to see the output.
!nvidia-smi | head -8


# %% color=rose title="vLLM 0.6+ pins specific torch / xformers builds"
# @explain: vLLM 0.6+ pins specific torch / xformers builds — let pip resolve
# vLLM 0.6+ pins specific torch / xformers builds — let pip resolve
!pip -q install vllm==0.6.4


# %% [markdown] color=lime title="4 · Offline batched inference"
# # 4 · Offline batched inference
#


# %% color=teal title="Tiny model so it fits on the free T4"
# @explain: Tiny model so it fits on the free T4 (16 GB)
from vllm import LLM, SamplingParams

# Tiny model so it fits on the free T4 (16 GB)
llm = LLM(model="Qwen/Qwen2.5-0.5B-Instruct",
          gpu_memory_utilization=0.5,   # keep some VRAM free for tooling
          max_model_len=2048)

prompts = [
    "What is RAG in one sentence?",
    "List 3 reasons to use a vector DB.",
    "Explain HNSW like I'm 12.",
    "What is PagedAttention?",
]

params = SamplingParams(temperature=0.0, max_tokens=128)
outputs = llm.generate(prompts, params)

for o in outputs:
    print("Q:", o.prompt[:60], "...")
    print("A:", o.outputs[0].text.strip(), "\n")


# %% [markdown] color=sky title="Notice the API.** `llm.generate(list_of_prompts)`…"
# # Notice the API.** `llm.generate(list_of_prompts)`…
#
# **Notice the API.** `llm.generate(list_of_prompts)` returns one result per prompt. vLLM **batches them automatically**, packs prefill + decode work into one engine step (continuous batching), and runs ~10× faster than calling HF `generate()` in a Python loop.


# %% [markdown] color=mint title="5 · Sampling parameters that matter"
# # 5 · Sampling parameters that matter
#


# %% color=peach title="params = SamplingParams("
# @explain: Run this cell to see the output.
params = SamplingParams(
    temperature=0.7,        # 0 = greedy; >1 = more random
    top_p=0.9,              # nucleus sampling: keep tokens whose cumulative prob ≤ 0.9
    top_k=-1,               # -1 = disabled
    repetition_penalty=1.05,
    max_tokens=256,
    stop=["\n\n", "<|endoftext|>"],
    seed=42,                # reproducible sampling
)
out = llm.generate(["Write a haiku about CUDA cores."], params)
print(out[0].outputs[0].text)


# %% [markdown] color=violet title="For tool-use / structured outputs vLLM also…"
# # For tool-use / structured outputs vLLM also…
#
# For tool-use / structured outputs vLLM also supports **guided decoding** with grammars / JSON schema:
#
# ```python
# from vllm import SamplingParams
# from vllm.sampling_params import GuidedDecodingParams
#
# guided = GuidedDecodingParams(json={"type":"object", "properties":{"name":{"type":"string"},"age":{"type":"integer"}}, "required":["name","age"]})
# params = SamplingParams(temperature=0.0, max_tokens=128, guided_decoding=guided)
# …


# %% [markdown] color=amber title="6 · vLLM serve — OpenAI-compatible HTTP"
# # 6 · vLLM serve — OpenAI-compatible HTTP
#


# %% color=rose title="Spawn vLLM's OpenAI-compatible server in the background"
# @explain: Spawn vLLM's OpenAI-compatible server in the background
# @explain: wait for health
# Spawn vLLM's OpenAI-compatible server in the background
import subprocess, time
srv = subprocess.Popen([
    "python","-m","vllm.entrypoints.openai.api_server",
    "--model", "Qwen/Qwen2.5-0.5B-Instruct",
    "--gpu-memory-utilization", "0.5",
    "--max-model-len", "2048",
    "--port", "8000",
], stdout=open("/tmp/vllm.log","w"), stderr=subprocess.STDOUT)

# wait for health
for _ in range(60):
    time.sleep(2)
    r = subprocess.run(["curl","-s","-o","/dev/null","-w","%{http_code}",
                        "http://localhost:8000/v1/models"], capture_output=True, text=True)
    if r.stdout == "200":
        print("ready"); break
else:
    print("timeout — check /tmp/vllm.log")


# %% [markdown] color=lime title="7 · Hitting it like OpenAI"
# # 7 · Hitting it like OpenAI
#


# %% color=teal title="!pip -q install openai"
# @explain: Run this cell to see the output.
!pip -q install openai
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8000/v1", api_key="x")

resp = client.chat.completions.create(
    model="Qwen/Qwen2.5-0.5B-Instruct",
    messages=[
        {"role":"system","content":"You are a terse assistant."},
        {"role":"user","content":"What's PagedAttention?"},
    ],
)
print(resp.choices[0].message.content)


# %% color=sky title="Streaming works the same as Ollama / OpenAI"
# @explain: Streaming works the same as Ollama / OpenAI — same client code
# Streaming works the same as Ollama / OpenAI — same client code
stream = client.chat.completions.create(
    model="Qwen/Qwen2.5-0.5B-Instruct",
    messages=[{"role":"user","content":"List 3 things vLLM optimises."}],
    stream=True,
)
for chunk in stream:
    d = chunk.choices[0].delta.content
    if d: print(d, end="", flush=True)
print()


# %% [markdown] color=mint title="The point.** Your application code from M38…"
# # The point.** Your application code from M38…
#
# **The point.** Your application code from M38 (Ollama) and from the OpenAI cloud doesn't change at all when you swap the backend to vLLM — only `base_url` does. **This is the whole reason to keep your client code OpenAI-shaped.**


# %% [markdown] color=peach title="8 · Tensor parallelism — splitting one model across GPUs"
# # 8 · Tensor parallelism — splitting one model across GPUs
#
# A 70 B model in fp16 needs ~140 GB of VRAM — no single GPU has that. **Tensor parallelism** splits each weight matrix across `N` GPUs; each GPU does a piece of the matmul, then the results are all-reduced.
#
# ```bash
# # 8× A100 serving Llama-3-70B
# python -m vllm.entrypoints.openai.api_server \
#     --model meta-llama/Meta-Llama-3-70B-Instruct \
# …


# %% [markdown] color=violet title="9 · Prefix caching + speculative decoding"
# # 9 · Prefix caching + speculative decoding
#
# Two features you turn on in production and forget about:
#
# ### Prefix caching (`--enable-prefix-caching`)
# If many requests share a prefix (system prompt, RAG context, function-call schema), vLLM **caches the KV-state** of that prefix and reuses it across requests. Saves the entire prefill cost on cache hits — often 70-90% of total compute for chat workloads.
#
# ### Speculative decoding (`--speculative-model`)
# …


# %% [markdown] color=amber title="10 · Picking the right server"
# # 10 · Picking the right server
#
# | Server | Best at | Watch out for |
# |---|---|---|
# | **vLLM** | best general-purpose throughput; PagedAttention; multi-LoRA | bleeding-edge model support sometimes lags by days |
# | **TGI** (Text Generation Inference, HF) | mature; tight HF integration; tool calling | harder to extend; license restrictions on newer versions |
# | **SGLang** | structured generation; fastest for **agentic** workloads with re-prefill | smaller ecosystem |
# | **TensorRT-LLM** | absolute fastest on NVIDIA; ahead-of-time compile | brittle; long compile; NVIDIA-only |
# …


# %% [markdown] color=rose title="✅ Recap"
# # ✅ Recap
#
# - **PagedAttention** + **continuous batching** = vLLM's two superpowers.
# - One line: `LLM(model=...).generate(prompts)` for offline batches.
# - `python -m vllm.entrypoints.openai.api_server` for an OpenAI-compatible HTTP server.
# - **Tensor parallel** to fit big models; **prefix caching** + **speculative decoding** for production speed.
# - Keep client code OpenAI-shaped → swap Ollama / vLLM / OpenAI by changing `base_url`.
#
# Cleanup:


# %% color=lime title="try: srv.terminate()"
# @explain: Run this cell to see the output.
try: srv.terminate()
except: pass


# %% [markdown] color=teal title="Next: **M45"
# # Next: **M45
#
# Next: **M45 — gRPC** (service-to-service plumbing for AI backends).


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


