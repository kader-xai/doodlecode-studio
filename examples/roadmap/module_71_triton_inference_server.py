# doodlecode format-version: 2
# Auto-converted from module_71_triton_inference_server.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 71 Triton Inference Server"
# # Module 71 Triton Inference Server
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 71 — Triton Inference Server"
# # Module 71 — Triton Inference Server
#
# > **vLLM** (M44) is the right answer for *one model, one type — LLMs on NVIDIA*. **TF Serving** (M40) is the right answer for *one model, one type — Keras*. What if you have ten models — an embedder + a reranker + a tabular XGBoost + an OCR detector + a vision-language model + an LLM — and want **one server, one URL, one set of metrics**? That's **Triton Inference Server**: NVIDIA's open-source, multi-framework, hardware-aware inference engine. It's the layer underneath SageMaker NeoTriton, Vertex AI Prediction, and most NVIDIA NIM endpoints.
#
# ### What you'll cover
# 1. The problem Triton solves
# 2. The **model repository** — file-system convention is the API
# 3. **`config.pbtxt`** — the one config file you'll write a lot
# …


# %% [markdown] color=mint title="1 · The problem"
# # 1 · The problem
#
# A real ML platform has dozens of models in production:
#
# ```
#    /v1/embed          → sentence-transformers (PyTorch)
#    /v1/rerank         → cross-encoder (PyTorch)
#    /v1/classify       → fraud XGBoost (sklearn / ONNX)
# …


# %% [markdown] color=peach title="2 · The model repository — file system is the API"
# # 2 · The model repository — file system is the API
#
# Triton has no admin GUI. You drop files into a directory; Triton serves them.
#
# ```
# models/
# ├── classify/                            ← model name = URL slug
# │   ├── config.pbtxt
# …


# %% [markdown] color=violet title="3 · `config.pbtxt` — the only config you'll write a lot"
# # 3 · `config.pbtxt` — the only config you'll write a lot
#


# %% color=amber title="models/embed/config.pbtxt"
# @explain: models/embed/config.pbtxt
# @explain: THE single most important block — see §5
# @explain: How many copies of this model on each GPU — see §6
# @explain: Optional: pin to specific versions
sample_config = '''
# models/embed/config.pbtxt
name: "embed"
backend: "pytorch"
max_batch_size: 64

input [
  {
    name: "INPUT__0"
    data_type: TYPE_INT64
    dims: [ -1 ]                     # variable sequence length
  }
]

output [
  {
    name: "OUTPUT__0"
    data_type: TYPE_FP32
    dims: [ 384 ]                    # MiniLM embedding dim
  }
]

# THE single most important block — see §5
dynamic_batching {
  preferred_batch_size: [ 8, 16, 32 ]
  max_queue_delay_microseconds: 5000
}

# How many copies of this model on each GPU — see §6
instance_group [
  {
    count: 2
    kind: KIND_GPU
  }
]

# Optional: pin to specific versions
version_policy { specific { versions: [1] } }
'''
print(sample_config)


# %% [markdown] color=rose title="Five `config.pbtxt` knobs you'll touch every time"
# # Five `config.pbtxt` knobs you'll touch every time
#
# **Five `config.pbtxt` knobs you'll touch every time.**
#
# 1. **`backend`** — `pytorch`, `tensorflow`, `onnxruntime`, `tensorrt`, `vllm`, `python`, `dali`.
# 2. **`max_batch_size`** — > 0 enables batching; 0 = no batching.
# 3. **`input` / `output`** — names match what the model exports; **`-1`** means dynamic dim.
# 4. **`dynamic_batching`** — turn on; tune `preferred_batch_size` + `max_queue_delay_microseconds`.
# 5. **`instance_group`** — how many copies of the model per device.


# %% [markdown] color=lime title="4 · Multi-framework backends"
# # 4 · Multi-framework backends
#


# %% color=teal title="Snippet of valid `backend:` values + what they…"
# @explain: Snippet of valid `backend:` values + what they expect under v1/
backends_table = '''
# Snippet of valid `backend:` values + what they expect under v1/

backend: "pytorch"        →  v1/model.pt          (TorchScript) — or  model.py for stateless PyTorch via python backend
backend: "tensorflow"     →  v1/model.savedmodel/ (SavedModel)
backend: "onnxruntime"    →  v1/model.onnx        (ONNX)
backend: "tensorrt"       →  v1/model.plan        (TRT engine — see §8)
backend: "openvino"        →  v1/model.xml        (Intel CPU/iGPU)
backend: "fil"             →  v1/xgboost.model    (Forest Inference Library — XGBoost / LightGBM / cuML)
backend: "vllm"            →  v1/model.json       (vLLM engine — see §10)
backend: "python"          →  v1/model.py         (arbitrary Python class — escape hatch)
backend: "dali"            →  v1/dali.json        (NVIDIA DALI — preprocessing pipelines on GPU)
backend: "tensorrt_llm"    →  v1/<engine dir>      (TRT-LLM — see §8)
'''
print(backends_table)


# %% [markdown] color=sky title="parse, run model, return responses"
# # parse, run model, return responses
#
# **`backend: "python"`** is the universal escape hatch — wrap arbitrary Python in a `TritonPythonModel` class:
#
# ```python
# class TritonPythonModel:
#     def initialize(self, args): ...           # load weights once
#     def execute(self, requests):              # called per batch
#         # parse, run model, return responses
#         return responses
# …


# %% [markdown] color=mint title="5 · Dynamic batching — Triton's signature win"
# # 5 · Dynamic batching — Triton's signature win
#
# The single biggest reason teams pick Triton over a hand-rolled FastAPI server.
#
# ```
#    Without dynamic batching:
#      req A → model.forward([A])  →  reply A
#      req B → model.forward([B])  →  reply B
# …


# %% [markdown] color=peach title="6 · Multi-instance + GPU isolation"
# # 6 · Multi-instance + GPU isolation
#


# %% color=violet title="Two copies on every GPU"
# @explain: Two copies on every GPU — uses tensor cores in parallel for small models
# @explain: Pin to specific GPUs (e.g
# @explain: Mix CPU + GPU copies (e.g
# @explain: Multiple model groups — same model, different rate-budget tiers
multi_instance_examples = '''
# Two copies on every GPU — uses tensor cores in parallel for small models
instance_group [
  { count: 2, kind: KIND_GPU }
]

# Pin to specific GPUs (e.g. dedicate GPU 0 to LLM, GPU 1 to embedder)
instance_group [
  { count: 1, kind: KIND_GPU, gpus: [1] }
]

# Mix CPU + GPU copies (e.g. fallback when GPUs are saturated)
instance_group [
  { count: 2, kind: KIND_GPU },
  { count: 2, kind: KIND_CPU }
]

# Multiple model groups — same model, different rate-budget tiers
instance_group [
  { name: "high_prio", count: 1, kind: KIND_GPU, gpus: [0] },
  { name: "low_prio",  count: 1, kind: KIND_GPU, gpus: [1] }
]
'''
print(multi_instance_examples)


# %% [markdown] color=amber title="When to bump `count > 1`.** If GPU utilisation…"
# # When to bump `count > 1`.** If GPU utilisation…
#
# **When to bump `count > 1`.** If GPU utilisation stays low under load (< 60 %) but latency rises, the model is bottlenecked by **launch + memory copy overhead**, not by compute. A second instance running concurrently uses the otherwise-idle compute. Empirically, 2-4 instances per GPU is the sweet spot for small models (< 1 B params); 1 instance per GPU for 7B+ LLMs.


# %% [markdown] color=rose title="7 · Ensembles + Business Logic Scripting (BLS)"
# # 7 · Ensembles + Business Logic Scripting (BLS)
#
# A production AI request rarely calls *one* model. RAG = embed → search → rerank → LLM. OCR = detect → recognise → spellcheck. Triton has two ways to chain models **inside the server**, without an extra HTTP hop:
#
# ### Ensemble — DAG defined in `config.pbtxt`
# Simple linear or DAG pipelines. Zero Python.
#
# ```
# …


# %% [markdown] color=lime title="8 · TensorRT and TensorRT-LLM — the absolute-fastest backend"
# # 8 · TensorRT and TensorRT-LLM — the absolute-fastest backend
#
# Triton can serve a PyTorch model directly. But for production NVIDIA hardware, compiling to **TensorRT** is the difference between "good" and "as fast as physics allows."
#
# ### TensorRT (general)
# - Ahead-of-time compiler — fuses kernels, picks tactics, runs in INT8 / FP8 / FP16.
# - Input: ONNX or PyTorch (`torch_tensorrt`); output: `.plan` engine file.
# - **2-10× faster** than PyTorch eager on the same GPU.
# …


# %% [markdown] color=teal title="9 · Metrics + Model Analyzer"
# # 9 · Metrics + Model Analyzer
#
# ### Metrics
# Triton exposes Prometheus metrics at `/metrics` out of the box (M50):
#
# ```
# nv_inference_request_success
# nv_inference_request_failure
# …


# %% [markdown] color=sky title="10 · Triton vs vLLM vs TF Serving vs TorchServe"
# # 10 · Triton vs vLLM vs TF Serving vs TorchServe
#
# | Server | Best at | Watch out for |
# |---|---|---|
# | **Triton** | multi-model, multi-framework, NVIDIA, complex pipelines | YAML-shaped pbtxt; learning curve; NVIDIA-centric |
# | **vLLM** (M44) | LLMs only, fast iteration, PagedAttention | one model per process; less polished metrics |
# | **TGI** (HuggingFace) | LLMs, HF integration, simple HTTP | HF licence terms on newer versions |
# | **TF Serving** (M40) | TensorFlow / Keras only | TF-only; aging UX |
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


