# doodlecode format-version: 2
# Auto-converted from module_51_opentelemetry_for_llms.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 51 Opentelemetry For Llms"
# # Module 51 Opentelemetry For Llms
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 51 — OpenTelemetry for LLMs"
# # Module 51 — OpenTelemetry for LLMs
#
# > M50 covered metrics. **OpenTelemetry (OTel)** unifies the other two pillars — **traces** and **logs** — into one vendor-neutral SDK + protocol. For LLM apps it's transformative: a single trace shows you the full path of one user request across **gateway → retriever → reranker → LLM call → tool call**, with token counts, prompts, and latencies on each step.
# >
# > OTel has become the de-facto standard. Datadog, Honeycomb, Jaeger, Tempo, Splunk, New Relic, Langfuse — they all speak OTel. Instrument once, send anywhere.
#
# ### What you'll cover
# 1. The trace mental model — span, parent, context propagation
# …


# %% [markdown] color=mint title="1 · Trace mental model"
# # 1 · Trace mental model
#
# A **trace** is a tree of **spans**. Each span has a name, start/end times, status, and attributes. A span has a **parent** (its caller), and the root span is the request itself.
#
# ```
# Trace: chat_request_42
# └─ span: gateway.handle              [320 ms]
#    └─ span: retriever.query           [80 ms]
# …


# %% [markdown] color=peach title="2 · OTel architecture"
# # 2 · OTel architecture
#
# ```
# ┌─ your app (Python, Go, Java, …) ─┐         ┌── OTel Collector ──┐         ┌─ backend ─┐
# │  OTel SDK ──── OTLP/gRPC ───────►├──HTTP──►│ receivers/processors├──────►│ Jaeger    │
# │  (spans, metrics, logs)          │         │ /exporters          │       │ Tempo     │
# └──────────────────────────────────┘         └─────────────────────┘       │ Datadog   │
#                                                                             │ Langfuse  │
# …


# %% [markdown] color=violet title="3 · Setup"
# # 3 · Setup
#


# %% color=amber title="!pip -q install \"
# @explain: Run this cell to see the output.
!pip -q install \
    opentelemetry-api \
    opentelemetry-sdk \
    opentelemetry-exporter-otlp \
    opentelemetry-instrumentation-requests \
    opentelemetry-instrumentation-fastapi


# %% [markdown] color=rose title="minimal collector that prints traces to stdout"
# # minimal collector that prints traces to stdout
#
# Run the Collector locally — one container:
# ```bash
# # minimal collector that prints traces to stdout
# docker run -p 4317:4317 -p 4318:4318 \
#     -v $PWD/otel-config.yaml:/etc/otel/config.yaml \
#     otel/opentelemetry-collector-contrib \
#     --config=/etc/otel/config.yaml
# ```
# …


# %% [markdown] color=lime title="4 · Manual spans — the core API"
# # 4 · Manual spans — the core API
#


# %% color=teal title="Wire up: provider → processor → exporter"
# @explain: Wire up: provider → processor → exporter
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource

# Wire up: provider → processor → exporter
provider = TracerProvider(resource=Resource.create({"service.name": "rag-app"}))
provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))   # for demo; OTLP in prod
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)


# %% color=sky title="import time"
# @explain: Run this cell to see the output.
import time, random

def retrieve(query):
    with tracer.start_as_current_span("retriever.query") as span:
        span.set_attribute("query.length", len(query))
        time.sleep(0.05)
        results = ["doc-1", "doc-2", "doc-3"]
        span.set_attribute("retriever.k", len(results))
        return results

def call_llm(query, ctx):
    with tracer.start_as_current_span("llm.completion") as span:
        span.set_attribute("llm.model", "qwen2.5-0.5b")
        span.set_attribute("llm.prompt.tokens", random.randint(40, 80))
        time.sleep(0.15)
        out = f"answer to {query}"
        span.set_attribute("llm.completion.tokens", len(out.split()))
        return out

def chat(query):
    with tracer.start_as_current_span("chat") as parent:
        parent.set_attribute("user.id", "u123")
        ctx = retrieve(query)
        out = call_llm(query, ctx)
        parent.set_attribute("response.length", len(out))
        return out

chat("what is RAG?")


# %% [markdown] color=mint title="Span hygiene"
# # Span hygiene
#
# **Span hygiene.**
# - Use **verbs in span names**: `retriever.query`, `llm.completion`. Not `retriever_called`.
# - Set **status** on errors: `span.set_status(Status(StatusCode.ERROR, "msg"))`.
# - Record exceptions: `span.record_exception(e)`.
# - Don't blow cardinality on attributes (no full prompts as attribute keys; use **events** for big payloads).


# %% [markdown] color=peach title="5 · Auto-instrumentation"
# # 5 · Auto-instrumentation
#


# %% color=violet title="one line per library"
# @explain: one line per library — every requests.get() / FastAPI route
# @explain: emits spans automatically with HTTP method, status, URL etc
# @explain: FastAPIInstrumentor.instrument_app(app)
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# one line per library — every requests.get() / FastAPI route
# emits spans automatically with HTTP method, status, URL etc.
RequestsInstrumentor().instrument()
# FastAPIInstrumentor.instrument_app(app)
print("auto-instrumentation enabled for: requests, fastapi")


# %% [markdown] color=amber title="There are **120+ official auto-instrumentations**"
# # There are **120+ official auto-instrumentations**
#
# There are **120+ official auto-instrumentations** — `psycopg`, `redis`, `aio_pika`, `boto3`, `sqlalchemy`, `grpcio`, `httpx`, `starlette`, `aiokafka`, …  Run:
#
# ```bash
# opentelemetry-bootstrap -a install   # detects installed libs and adds matching otel packages
# opentelemetry-instrument python app.py   # zero-code instrumentation
# ```
#
# For most CRUD apps that's enough — you skip §4 entirely.


# %% [markdown] color=rose title="6 · GenAI semantic conventions"
# # 6 · GenAI semantic conventions
#
# OTel's **semantic conventions** standardise span attribute names so dashboards work across vendors. The **GenAI** spec (stable since 2024) covers LLM calls:
#
# | Attribute | Example |
# |---|---|
# | `gen_ai.system` | `"openai"`, `"anthropic"`, `"vllm"`, `"ollama"` |
# | `gen_ai.request.model` | `"gpt-4o-mini"` |
# …


# %% [markdown] color=lime title="7 · The LLM ecosystem on top of OTel"
# # 7 · The LLM ecosystem on top of OTel
#
# | Project | What it adds |
# |---|---|
# | **OpenLLMetry / Traceloop** | one-line wrapping of OpenAI / Anthropic / LangChain / LlamaIndex SDKs to emit GenAI-spec spans automatically |
# | **Langfuse** | OTel-compatible LLM observability backend with prompt versioning, eval, datasets, cost tracking |
# | **Arize Phoenix** | open-source LLM observability + evals; great for offline analysis |
# | **LangSmith** | LangChain's hosted tracing (proprietary protocol; OTel adapter exists) |
# …


# %% [markdown] color=teal title="8 · Sampling"
# # 8 · Sampling
#
# You can't (and shouldn't) trace 100% of traffic at scale.
#
# | Strategy | When |
# |---|---|
# | **AlwaysOn / AlwaysOff** | dev / never |
# | **TraceIdRatioBased(0.01)** | 1% of all traces — cheap, lossy |
# …


# %% [markdown] color=sky title="9 · Exporters — OTLP everywhere"
# # 9 · Exporters — OTLP everywhere
#


# %% color=mint title="swap ConsoleSpanExporter for OTLP"
# @explain: swap ConsoleSpanExporter for OTLP — same code, different destination
# swap ConsoleSpanExporter for OTLP — same code, different destination
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

otlp = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
provider.add_span_processor(BatchSpanProcessor(otlp))
print("now exporting to OTLP collector at :4317")


# %% [markdown] color=peach title="Common Collector destinations"
# # Common Collector destinations
#
# Common Collector destinations:
# ```yaml
# exporters:
#   otlp/jaeger:    { endpoint: jaeger:4317,         tls: { insecure: true } }
#   otlp/tempo:     { endpoint: tempo:4317 }
#   otlphttp/honeycomb: { endpoint: https://api.honeycomb.io, headers: { x-honeycomb-team: $${HONEYCOMB_KEY} } }
#   otlp/langfuse:  { endpoint: https://us.cloud.langfuse.com:443, headers: { authorization: "Basic $${LF_AUTH}" } }
#   datadog:        { api: { key: $${DD_API_KEY}, site: datadoghq.com } }
# …


# %% [markdown] color=violet title="10 · Putting it together — debugging a real bug"
# # 10 · Putting it together — debugging a real bug
#
# A user reports "the chatbot was super slow on Tuesday at 3 PM."
#
# 1. Open the trace explorer, filter to that user's traces in that window.
# 2. Sort by duration desc — top trace was 8.2 s.
# 3. Open it. The waterfall shows:
#    - `chat` 8.2 s → mostly `retriever.query` 7.9 s
# …


# %% [markdown] color=amber title="✅ Recap"
# # ✅ Recap
#
# - Trace = tree of spans, glued by **context propagation**.
# - Architecture: SDK → OTLP → Collector → backend(s). Always run a Collector.
# - **Manual spans** for your own logic; **auto-instrumentation** for libs.
# - **GenAI semantic conventions** + **OpenLLMetry / Langfuse** make LLM tracing one-line.
# - **Tail-based sampling** in the Collector keeps the interesting traces and drops the rest.
# - Traces answer "where did the time go?" — metrics (M50) only tell you that something is slow.
#
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


