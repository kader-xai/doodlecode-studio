# doodlecode format-version: 2
# Auto-converted from module_79_finops_for_ai_platforms.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 79 Finops For Ai Platforms"
# # Module 79 Finops For Ai Platforms
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 79 — FinOps for AI Platforms"
# # Module 79 — FinOps for AI Platforms
#
# > Two facts most ML curricula skip:
# > 1. **The bill is the moat.** Frontier-lab budgets are measured in **billions of dollars**. A startup's cloud bill can dwarf its salaries within months of launching.
# > 2. **The bill is the *easiest* lever you have.** Pre-deploy, every architecture choice (M44–M71) is also a $/Mtok choice. Post-deploy, **prompt caching, model routing, quantisation, batching, and spot capacity** can each cut cost by 30–80 %.
# >
# > This module is the disciplined view of money: how to measure it, attribute it, monitor it, and engineer it down without compromising the product.
#
# …


# %% [markdown] color=mint title="1 · The two cost engines"
# # 1 · The two cost engines
#
# Every AI platform's bill is two giant line items:
#
# ```
#                      ┌─────────────── TRAINING ───────────────┐
#                      │  Pre-train: $10M – $1B+ per frontier   │
#                      │  Fine-tune: $100s – $1M per cycle      │
# …


# %% [markdown] color=peach title="2 · The unit economics"
# # 2 · The unit economics
#


# %% color=violet title="A sketch of what 'knowing your unit economics'…"
# @explain: A sketch of what "knowing your unit economics" means in practice
# @explain: Example: a typical chatbot turn — 1.5k context, 500-token answer
# A sketch of what "knowing your unit economics" means in practice
def cost_per_request(
    input_tokens: int,
    output_tokens: int,
    in_price_per_mtok: float,    # $/MTok
    out_price_per_mtok: float,   # $/MTok
    cache_hit_rate: float = 0.0,
    cache_in_price_per_mtok: float = None,
) -> float:
    """Return USD cost per request."""
    cache_in_price = cache_in_price_per_mtok if cache_in_price_per_mtok is not None else in_price_per_mtok
    effective_in = (1 - cache_hit_rate) * in_price_per_mtok + cache_hit_rate * cache_in_price
    return (input_tokens  / 1e6) * effective_in + (output_tokens / 1e6) * out_price_per_mtok

# Example: a typical chatbot turn — 1.5k context, 500-token answer
costs = {
    "GPT-5 (full)":     (5.0,  10.0, 0.5,  0.5),    # made-up indicative numbers
    "Claude Sonnet 4.6":(3.0,   15.0, 0.3,  0.3),
    "Gemini 2.5 Pro":   (1.25,  10.0, 0.125, 0.125),
    "Llama 3.3 70B (self-host vLLM)": (0.4, 0.6, 0.0, 0.0),   # amortised GPU cost
}
for model, (i, o, ci, _) in costs.items():
    c = cost_per_request(1500, 500, i, o, cache_hit_rate=0.5, cache_in_price_per_mtok=ci)
    print(f"{model:<30s}  ${c*1000:.2f} / 1k requests")


# %% [markdown] color=amber title="What the calculation reveals:** for a 50 %…"
# # What the calculation reveals:** for a 50 %…
#
# **What the calculation reveals:** for a 50 % prompt-cache hit rate (M37 / M44 prefix cache), self-hosted Llama on vLLM is often **6-30×** cheaper than frontier hosted APIs — but the **quality gap** has to be acceptable for your use case. The whole job of a platform team is making that trade-off explicit, per route, per user tier.


# %% [markdown] color=rose title="3 · Where the bill actually goes"
# # 3 · Where the bill actually goes
#


# %% color=lime title="bill_breakdown = '''"
# @explain: Run this cell to see the output.
bill_breakdown = '''
Typical breakdown for a $1M/yr AI platform (sub-frontier):
  COMPUTE (training + inference GPU/CPU)   55-70 %
  HOSTED LLM API (OpenAI/Anthropic/etc)    10-25 %
  STORAGE  (object + parallel FS)           5-10 %
  NETWORK egress + LB                       3-8  %
  HUMAN LABELLING + RLHF crews              2-10 %
  EVAL infrastructure                       1-3  %
  TOOLING (Datadog, Langfuse, etc.)         1-3  %
  ─────────────────────────────────────────
  TOTAL                                     100 %
'''
print(bill_breakdown)


# %% [markdown] color=teal title="Two things that *don't* show up in this list and…"
# # Two things that *don't* show up in this list and…
#
# **Two things that *don't* show up in this list and surprise people:**
# - **Network egress** — 1¢/GB on AWS sounds tiny until you ship a 700 GB model checkpoint across regions for DR.
# - **Human labelling** — $20-50/hr × thousands of hours for preference data (M62, M67) easily exceeds $500K/yr for a serious RLHF effort.
#
# Frontier labs invert the ratios: their compute is ~85 % of total spend; human labour is < 5 %.


# %% [markdown] color=sky title="4 · Hosted-API pricing — the 2026 landscape"
# # 4 · Hosted-API pricing — the 2026 landscape
#
# | Provider / Model | Input $/MTok | Output $/MTok | Cached input $/MTok | Best at |
# |---|---|---|---|---|
# | **OpenAI GPT-5 (Pro)** | $5 | $10 | $0.50 | hard reasoning, tool use |
# | **OpenAI GPT-5 mini** | $0.30 | $1.20 | $0.03 | fast, cheap, agentic |
# | **Anthropic Claude Sonnet 4.6** | $3 | $15 | $0.30 | long context, code, agents |
# | **Anthropic Claude Haiku 4** | $0.80 | $4 | $0.08 | fast routing tier |
# …


# %% [markdown] color=mint title="5 · Inference cost levers"
# # 5 · Inference cost levers
#
# | Lever | Typical saving | When |
# |---|---|---|
# | **Prompt / prefix caching** (M37, M44) | 30-90% input cost | system prompts, RAG contexts shared across users |
# | **Response caching** (Redis) | 50-99% on hits | repeated FAQs, deterministic answers |
# | **Model routing** (above) | 5-15× on average | most chat apps have a long tail of simple queries |
# | **Quantisation** (INT8 / FP8 / AWQ — M38, M71) | 2-4× throughput | self-hosted; tolerate ~1-2% quality drop |
# …


# %% [markdown] color=peach title="6 · Training cost levers"
# # 6 · Training cost levers
#
# | Lever | Typical saving | When |
# |---|---|---|
# | **Spot / preemptible GPUs** | 50-80% off list price | tolerant to mid-run preemption; need checkpoint-from-Lustre (M78) |
# | **Reserved / Savings Plans / 1-3yr commit** | 30-60% off | predictable steady-state inference fleet |
# | **FP8 / BF16 mixed precision** (M66 §9) | 1.5-2× throughput | every modern training run |
# | **Better data efficiency** | unbounded (cheaper data = cheaper training) | dedup + curriculum + retain only high-signal data |
# …


# %% [markdown] color=violet title="7 · Tagging + allocation + chargeback"
# # 7 · Tagging + allocation + chargeback
#
# The boring FinOps that pays for itself within a quarter.
#
# ### Tag everything
# Every cloud resource, every Helm release, every model deployment, every job:
#
# ```yaml
# …


# %% [markdown] color=amber title="8 · Cost observability — instrumentation"
# # 8 · Cost observability — instrumentation
#


# %% color=rose title="A minimal request-level cost tracker"
# @explain: A minimal request-level cost tracker — every LLM call goes through this wrapper
# @explain: In real life: send to OTel (M51) + Langfuse + your warehouse
# @explain: example
# A minimal request-level cost tracker — every LLM call goes through this wrapper.
import time, uuid
PRICES = {
    "gpt-5":          (5.0,  10.0, 0.5),
    "gpt-5-mini":     (0.30, 1.20, 0.03),
    "claude-sonnet-4-6":(3.0,  15.0, 0.30),
    "claude-haiku-4": (0.80, 4.00, 0.08),
    "gemini-2.5-pro": (1.25, 10.0, 0.125),
    "gemini-2.5-flash":(0.075,0.30, 0.0075),
}

def track_llm_call(model, prompt_tokens, completion_tokens, cached_in=0,
                   user_id=None, route="default", trace_id=None):
    in_p, out_p, cached_p = PRICES[model]
    cost = ((prompt_tokens - cached_in) / 1e6 * in_p
            + cached_in            / 1e6 * cached_p
            + completion_tokens    / 1e6 * out_p)
    record = {
        "ts": time.time(),
        "trace_id": trace_id or str(uuid.uuid4()),
        "model": model,
        "tokens_in": prompt_tokens,
        "tokens_in_cached": cached_in,
        "tokens_out": completion_tokens,
        "usd": round(cost, 6),
        "user_id": user_id,
        "route": route,
    }
    # In real life: send to OTel (M51) + Langfuse + your warehouse
    print(record)
    return cost

# example
track_llm_call("gpt-5-mini", 1500, 500, cached_in=1000, user_id="u_42", route="search.summary")


# %% [markdown] color=lime title="Tools that do this for you in 2026"
# # Tools that do this for you in 2026
#
# **Tools that do this for you in 2026:**
# - **Langfuse / Helicone / LangSmith / Arize Phoenix** — drop-in proxies that meter every call and attach `trace_id`, model, cost, latency. Pair with M51 OTel.
# - **LiteLLM** — model router with built-in budget enforcement (max $/user, per-route).
# - **AWS Cost Explorer / Anomaly Detection · GCP Recommender · Azure Cost Management** — vendor portals.
# - **Vantage · CloudHealth · Cloudability · Apptio** — third-party FinOps.
# - **OpenCost** — k8s-native cost allocation; pairs with Prometheus (M50).
# - **dcgm-exporter + custom metrics** (M50) — GPU-utilisation × time × cost — proves which jobs are wasting silicon.
#
# …


# %% [markdown] color=teal title="9 · 2026 real-number scoreboard"
# # 9 · 2026 real-number scoreboard
#
# ### Public reported / estimated training costs
#
# | Model | Estimated training cost |
# |---|---|
# | GPT-3 (2020) | ~$5M |
# | GPT-4 | ~$60-80M |
# …


# %% [markdown] color=sky title="10 · The 12-month FinOps playbook"
# # 10 · The 12-month FinOps playbook
#
# ### Month 0-1 — Instrument
# - Pick a metering layer (**Langfuse** or **Helicone** for LLM calls; **OpenCost** for k8s; **OTel** for traces).
# - Tag every resource (`team / env / product / cost_center / owner / workload / model_id`).
# - Wire up a **single dashboard** with $/day, $/Mtok, gross margin per route.
#
# ### Month 2-3 — Quick wins
# …


# %% [markdown] color=mint title="✅ Recap"
# # ✅ Recap
#
# - AI cost = **training** (episodic, capex-like) + **inference** (continuous, opex-like). Inference is where you get most early wins.
# - The single biggest lever is **model routing** — push the long tail to a Haiku / Flash / mini tier.
# - Prompt caching, response caching, quantisation, batching, and speculative decoding each unlock another 30-80%.
# - **Tag everything** (team / env / product / workload / model_id) and **chargeback** — without that, FinOps isn't happening.
# - Use **Langfuse / Helicone / OpenCost / OTel** for token-level cost attribution. Build the **$/route × $/team × margin** dashboard before you need it.
# - Frontier training is **$50M – $1B+**; for everyone else, **don't pretrain** — RAG + SFT + DPO is 100-1000× cheaper.
# - Run the **12-month playbook**: instrument → quick wins → self-host where it pays → budgets → strategic commits.
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


