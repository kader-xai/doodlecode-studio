# doodlecode format-version: 2
# Auto-converted from module_80_multi_tenant_ai_platform_patterns.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 80 Multi Tenant Ai Platform Patterns"
# # Module 80 Multi Tenant Ai Platform Patterns
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 80 — Multi-Tenant AI Platform Patterns"
# # Module 80 — Multi-Tenant AI Platform Patterns
#
# > Every AI platform that grows past one product hits the same wall: **how do you let many teams (or paying customers) share one platform without their data, models, costs, or noise leaking into each other?** Get this wrong and a single tenant can leak another's RAG corpus, eat all the GPU budget, or DoS the cluster.
# >
# > This module is the production-grade map: **isolation models, request routing, per-tenant LoRAs, quotas, cost attribution (M79), data residency, and tenant lifecycle.**
#
# ### What you'll cover
# 1. The four tenant archetypes
# …


# %% [markdown] color=mint title="1 · The four tenant archetypes"
# # 1 · The four tenant archetypes
#
# | Archetype | Tenants are… | Examples | Drives… |
# |---|---|---|---|
# | **B2B SaaS** | paying customer companies | Notion AI, Intercom Fin, Vanta AI | per-customer data isolation + billing |
# | **Internal platform** | other teams in your company | Spotify ML Platform, Uber Michelangelo, Netflix Metaflow | quota / chargeback / showback (M79) |
# | **Model marketplace** | end-developers calling your hosted models | OpenAI, Anthropic, Together AI, Fireworks | abuse + per-API-key budgets |
# | **Government / regulated** | agencies / banks / hospitals | Palantir, Anthropic Gov, Mistral EU | data residency, audit, FedRAMP / SOC2 / HIPAA |
# …


# %% [markdown] color=peach title="2 · The four isolation models"
# # 2 · The four isolation models
#
# A spectrum from cheapest+leakiest to most-isolated+most-expensive:
#
# ```
#    ┌─────────────────────────────────────────────────────────────────────────────┐
#    │                                                                              │
#    │   shared-everything  →  namespaced  →  silo  →  dedicated stack             │
# …


# %% [markdown] color=violet title="3 · The request path"
# # 3 · The request path
#
# How does a request know which tenant it belongs to? Three steps:
#
# ```
#    1. Edge / gateway extracts tenant_id from
#         - API key (most common)         tenant_id = key_table.lookup(api_key).tenant_id
#         - OIDC JWT claim                tenant_id = jwt.claims["tenant_id"]
# …


# %% color=amber title="A minimal middleware that does extraction +…"
# @explain: A minimal middleware that does extraction + propagation correctly
# @explain: Async-safe context var
# @explain: 1
# @explain: in real life: validate JWT, read claim
# @explain: 2
# A minimal middleware that does extraction + propagation correctly
from fastapi import FastAPI, Request, HTTPException, Depends
import contextvars

# Async-safe context var
_tenant: contextvars.ContextVar[str | None] = contextvars.ContextVar("tenant", default=None)

def tenant_id() -> str:
    """Read inside any handler/service to know who the request belongs to."""
    t = _tenant.get()
    if not t:
        raise HTTPException(status_code=400, detail="No tenant context")
    return t

app = FastAPI()

@app.middleware("http")
async def tenant_middleware(request: Request, call_next):
    # 1. extract (in priority order)
    tid = request.headers.get("x-tenant-id")
    if not tid and "authorization" in request.headers:
        # in real life: validate JWT, read claim
        tid = "demo-tenant-from-jwt"
    if not tid:
        return await call_next(request)        # let unauthenticated routes pass

    # 2. propagate via contextvar (carries across `await`)
    token = _tenant.set(tid)
    try:
        response = await call_next(request)
    finally:
        _tenant.reset(token)
    return response

@app.get("/api/chat")
async def chat(t: str = Depends(tenant_id)):
    return {"answer": f"hi, tenant {t}!"}


# %% [markdown] color=rose title="Two ways propagation breaks"
# # Two ways propagation breaks
#
# **Two ways propagation breaks.**
# 1. **Mixed sync/async stacks** — `contextvars` are async-safe but break across thread-pool executors. Always propagate explicitly through gRPC metadata (M45) or A2A `caller` (M75).
# 2. **Cross-tenant background jobs** — celery / RQ / k8s `Job` workers process tasks from a queue. The tenant must be **on the message**, not the worker's environment.


# %% [markdown] color=lime title="4 · Data isolation — RAG, embeddings, vector DBs, feature stores"
# # 4 · Data isolation — RAG, embeddings, vector DBs, feature stores
#
# The #1 way multi-tenant AI breaks: **tenant A's RAG retrieves tenant B's documents.** Avoid by enforcing tenant scope at *every* read.
#
# ### Pattern A — one collection, `tenant_id` filter (cheap)
# ```python
# results = qdrant.search(
#     collection_name="docs",
# …


# %% [markdown] color=teal title="5 · Per-tenant LoRA — one base model, many fine-tunes"
# # 5 · Per-tenant LoRA — one base model, many fine-tunes
#
# The killer pattern for multi-tenant LLM apps. Frontier base model is shared (a single vLLM pool with PagedAttention — M44); **each tenant has a small (~20-200 MB) LoRA** (M39) that adapts it to their domain / tone / data.


# %% color=sky title="vLLM multi-LoRA: many adapters loaded on one base model"
# @explain: vLLM multi-LoRA: many adapters loaded on one base model, swapped per request
# @explain: Server side — load the base model with --enable-lora and per-tenant adapters
# @explain: Client side — pick the adapter via `model` field
# vLLM multi-LoRA: many adapters loaded on one base model, swapped per request
vllm_multi_lora = '''
# Server side — load the base model with --enable-lora and per-tenant adapters
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3.3-70B-Instruct \
    --enable-lora \
    --lora-modules \
        tenant-acme=s3://my-bucket/loras/acme-v2.tar \
        tenant-foo=s3://my-bucket/loras/foo-v1.tar \
        tenant-bar=s3://my-bucket/loras/bar-v3.tar \
    --max-loras 8 \
    --max-lora-rank 64

# Client side — pick the adapter via `model` field
curl http://vllm:8000/v1/chat/completions \
    -H "Authorization: Bearer $API_KEY" \
    -d '{
        "model": "tenant-acme",                    # ← LoRA name
        "messages": [{"role":"user","content":"…"}]
    }'
'''
print(vllm_multi_lora)


# %% [markdown] color=mint title="Why this scales"
# # Why this scales
#
# **Why this scales.**
# - One **70B base** in VRAM, hot, shared across all tenants → KV cache amortised across the fleet (M60).
# - **Hundreds of LoRAs** hot-swapped on demand at ~10 ms switch cost.
# - Cold tenants paged out to disk; vLLM keeps recently used ones resident.
# - vLLM, **SGLang**, **LoRAX (Predibase)**, and Triton (M71) all support this pattern.
#
# **Per-tenant fine-tuning lifecycle:**
# 1. Tenant ingests training data (chat logs, docs) via your platform UI.
# …


# %% [markdown] color=peach title="6 · Quotas + rate limits + fair-share scheduling"
# # 6 · Quotas + rate limits + fair-share scheduling
#
# A single greedy tenant will eat your platform if you let it. Four layers of defence:
#
# | Layer | Tool | Enforces |
# |---|---|---|
# | **Edge gateway** | API gateway (Kong, Envoy, Apigee), or LiteLLM, or custom | RPS / TPS / monthly $ |
# | **Token-level meter** | LiteLLM, Helicone — counts tokens per call | $/Mtok per tenant tier |
# …


# %% [markdown] color=violet title="7 · Tenant-aware observability"
# # 7 · Tenant-aware observability
#
# Pair this with M50 + M51. Every metric, log, and trace must carry `tenant_id`.
#
# ### OTel attribute
# ```python
# from opentelemetry import trace
# span = trace.get_current_span()
# …


# %% [markdown] color=amber title="8 · Auth + OIDC + scoped tokens"
# # 8 · Auth + OIDC + scoped tokens
#
# The trust chain that makes the whole thing safe.
#
# ```
#    user / service ───►  IdP (Auth0 / Cognito / Okta / Entra / Keycloak)
#                               │ issues OIDC JWT
#                               ▼
# …


# %% [markdown] color=rose title="9 · Tenant lifecycle"
# # 9 · Tenant lifecycle
#
# | Phase | What happens | Gotcha |
# |---|---|---|
# | **Onboard** | provision namespace, DB schema, vector collection, default LoRA, API keys, billing record | atomic — if anything fails, rollback all |
# | **Active** | normal operation, monitored | flag idle tenants for downgrade |
# | **Suspend** | rate-limit to 0, hide UI, keep data | needs to be reversible within SLA |
# | **Trial-end** | gentle email; route to free tier | not deletion |
# …


# %% [markdown] color=lime title="10 · The reference architecture + anti-patterns"
# # 10 · The reference architecture + anti-patterns
#
# ```
#                             ┌─────────────────────────────────────┐
#                             │  IdP (OIDC) + secrets manager       │
#                             └──────────────────┬──────────────────┘
#                                                │
#                             ┌──────────────────▼──────────────────┐
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


