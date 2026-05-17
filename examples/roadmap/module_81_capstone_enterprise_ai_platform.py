# doodlecode format-version: 2
# Auto-converted from module_81_capstone_enterprise_ai_platform.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 81 Capstone Enterprise Ai Platform"
# # Module 81 Capstone Enterprise Ai Platform
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 81 — Capstone: Enterprise AI Platform"
# # Module 81 — Capstone: Enterprise AI Platform
#
# > 80 modules of fragments. This one is **the platform** — a concrete blueprint that **wires every prior module into one running system**. The premise: you've been hired as platform lead at **Acme Insights**, a 200-employee B2B SaaS, to ship the AI Assistant their enterprise customers (hospitals, banks, retailers) are demanding. You have **one engineer per layer**, **$2M Year-1 cloud budget**, **6 months to GA**.
# >
# > This module isn't another concept primer — it's the **decision log + reference architecture + 26-week build plan** that says *use this module here*. By the end you can scope, staff, and ship this in your own org. It's the portfolio piece a hiring manager actually wants to see.
#
# ### What you'll cover
# 1. The brief — Acme's product, customers, constraints
# …


# %% [markdown] color=mint title="1 · The brief"
# # 1 · The brief
#
# **Acme Insights**, a 200-employee B2B SaaS, sells a workflow tool to hospitals, regional banks, and large retailers. Customers are asking for an **AI assistant** that:
#
# - **Answers questions** about their own internal docs (RAG) — every customer has a unique corpus.
# - **Drafts** emails, reports, summaries — domain-tuned (per customer LoRA).
# - **Takes actions** (creates tickets, schedules tasks, calls APIs) — agentic, with HITL approval.
# - **Ingests data** from their existing systems (Salesforce, ServiceNow, Slack, Drive).
# …


# %% [markdown] color=peach title="2 · The reference architecture"
# # 2 · The reference architecture
#
# ```
#                                     USERS  ◄──── M54 TypeScript frontend (Next.js + Vercel AI SDK)
#                                        │
#                                        ▼
#                   ┌─────── EDGE / GATEWAY ─────────┐
#                   │  CloudFront + ALB                │  ← M46/M47 (k8s + ingress)
# …


# %% [markdown] color=violet title="3 · Layer-by-layer module mapping"
# # 3 · Layer-by-layer module mapping
#
# | Layer | Choice | Primary modules | Why |
# |---|---|---|---|
# | **Frontend** | Next.js + Vercel AI SDK | **M54** | streaming chat, tool-call UI in <1 day |
# | **API gateway** | FastAPI + LiteLLM | **M28**, **M79**, **M80** §3 | one place to auth, rate-limit, meter, route |
# | **Auth / IdP** | Auth0 (later: Cognito for AWS native) | **M80** §8 | OIDC + per-tenant scopes |
# | **Orchestration** | LangGraph + Pydantic AI | **M33**, **M35**, **M59** | stateful agents, structured outputs |
# …


# %% [markdown] color=amber title="4 · The repo layout"
# # 4 · The repo layout
#
# ```
# acme-ai/
# ├── apps/
# │   ├── web/                     # Next.js frontend (M54)
# │   ├── gateway/                 # FastAPI + LiteLLM (M28, M79)
# │   ├── workers/                 # Celery / async (M28)
# …


# %% [markdown] color=rose title="5 · A live request walkthrough — 17 hops, 1.4 s budget"
# # 5 · A live request walkthrough — 17 hops, 1.4 s budget
#
# One real chat turn. Aim for **p99 < 2.5 s**; budget per layer below adds to ~1.4 s steady-state.
#
# ```
#    User types "What's the deductible for customer #4471?" → presses Enter
#
#    1   browser              streaming POST /api/chat                     (5 ms)
# …


# %% [markdown] color=lime title="6 · The 26-week build plan"
# # 6 · The 26-week build plan
#
# ```
# Weeks 0-4   FOUNDATION                                              · M46 M47 M48
#             ┌─ EKS dev cluster, Argo CD, Terraform modules
#             ├─ Auth0 tenant model, FastAPI gateway skeleton           · M28
#             ├─ Postgres + Redis + Qdrant
#             └─ OTel collector + Prometheus + Grafana                  · M50 M51
# …


# %% [markdown] color=teal title="7 · The team"
# # 7 · The team
#
# Eight engineers is the practical minimum. One lead + seven specialists:
#
# | Role | Headcount | Owns | Lean-on modules |
# |---|---|---|---|
# | **Platform Lead** | 1 | architecture, on-call rotation, hiring | all of them |
# | **Backend / API** | 1 | FastAPI gateway, MCP servers, auth | M28, M32, M64, M80 |
# …


# %% [markdown] color=sky title="8 · Day-1 launch checklist"
# # 8 · Day-1 launch checklist
#
# Before turning the GA switch on, **every one** of these must be green:
#
# ### Security (M74)
# - [ ] OWASP LLM Top 10 review signed off
# - [ ] Llama Guard 3 input + output filters in every chat route
# - [ ] Garak + Promptfoo red-team in CI; block deploy on regression
# …


# %% [markdown] color=mint title="9 · Day-90 evolution — what to add next"
# # 9 · Day-90 evolution — what to add next
#
# Post-GA the system runs; now you scale. **What to add in Year 2:**
#
# | Area | Module(s) | Why |
# |---|---|---|
# | **Self-host top route** | M44, M60, M71, M79 | hosted bill is now ≥ $200k/mo; vLLM cluster pays for itself |
# | **DPO on top routes** | M62 | preference fine-tunes from production thumbs-up/down |
# …


# %% [markdown] color=peach title="10 · Failure modes that will hit you"
# # 10 · Failure modes that will hit you
#
# Pre-loaded so you don't have to learn them by suffering:
#
# | Failure | Cause | Module / Fix |
# |---|---|---|
# | **A tenant's RAG returns another tenant's docs** | missing filter on one path | M80 — integration test on every retriever call |
# | **One tenant's traffic eats the whole cluster** | no fair-share scheduling | M80 — Volcano / Kueue; Redis sliding window |
# …


# %% [markdown] color=violet title="✅ Recap"
# # ✅ Recap
#
# - The **reference architecture** is one A4 picture: edge → gateway → orchestration → tools → retrieval → inference → data lake → observability → platform plumbing.
# - Every layer maps to **1-3 prior modules**. M1-M80 was the parts catalogue; this module is the wiring diagram.
# - The **26-week plan** ships v0 → v3 → GA in six months with a team of 8.
# - The **day-1 checklist** is 28 boxes, none optional, all backed by earlier modules.
# - The **failure-mode catalogue** is 10 incidents that every platform meets — runbooks ready.
#
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


