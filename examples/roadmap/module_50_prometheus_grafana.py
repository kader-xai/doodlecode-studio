# doodlecode format-version: 2
# Auto-converted from module_50_prometheus_grafana.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 50 Prometheus Grafana"
# # Module 50 Prometheus Grafana
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 50 — Prometheus + Grafana"
# # Module 50 — Prometheus + Grafana
#
# > You've shipped vLLM (M44), gRPC (M45), Kubernetes (M46), Helm (M47), Terraform (M48), Ansible (M49). You can't run any of this in production without **observability** — and observability in 2026 still means **Prometheus** for metrics + **Grafana** for dashboards. Almost every ML-native tool (vLLM, Triton, KServe, Argo, NVIDIA DCGM) exposes Prometheus metrics out of the box. Knowing the stack is non-optional.
# >
# > This module is the practical core: instrument a Python service, run Prometheus locally, write PromQL, build a Grafana dashboard, and bolt on alerting.
#
# ### What you'll cover
# 1. The 3 pillars of observability (metrics · logs · traces) and what each is for
# …


# %% [markdown] color=mint title="1 · Three pillars (and what each is good at)"
# # 1 · Three pillars (and what each is good at)
#
# | Pillar | Best for | Tools |
# |---|---|---|
# | **Metrics** | "is the system healthy *right now*?" — low-cardinality, aggregated time-series | Prometheus, VictoriaMetrics, Mimir |
# | **Logs** | "what exactly happened in *this one* request?" | Loki, Elasticsearch, OpenSearch |
# | **Traces** | "where did *this slow request* spend its time?" | OpenTelemetry (M51), Jaeger, Tempo |
#
# …


# %% [markdown] color=peach title="2 · Pull model in 60 seconds"
# # 2 · Pull model in 60 seconds
#
# ```
#                       ┌────── /metrics ──────┐
#                       │                      │
#    ┌──────────────┐   │   ┌──────────────┐   │   ┌──────────────┐
#    │  vLLM pod    ├───▶───│ Prometheus   ├───▶───│   Grafana    │
#    │  /metrics    │       │ (scrapes)    │       │ (queries)    │
# …


# %% [markdown] color=violet title="3 · Metric types"
# # 3 · Metric types
#
# | Type | Goes only ↑? | Use case | Example |
# |---|---|---|---|
# | **Counter** | yes | total events | `http_requests_total` |
# | **Gauge** | up or down | momentary value | `gpu_memory_used_bytes` |
# | **Histogram** | yes (multiple) | distribution; gives you p50/p95/p99 | `http_request_duration_seconds_bucket` |
# | **Summary** | yes (multiple) | client-side quantiles | `rpc_duration_seconds` |
# …


# %% [markdown] color=amber title="4 · Instrument a Python service"
# # 4 · Instrument a Python service
#


# %% color=rose title="!pip -q install prometheus_client"
# @explain: Run this cell to see the output.
!pip -q install prometheus_client


# %% color=lime title="1) define your metrics ONCE at module scope"
# @explain: 1) define your metrics ONCE at module scope (not per request)
# @explain: 2) start the metrics server (sidecar in a real app)
from prometheus_client import (
    Counter, Gauge, Histogram, start_http_server,
    REGISTRY, CONTENT_TYPE_LATEST, generate_latest,
)
import time, random, threading

# 1) define your metrics ONCE at module scope (not per request)
REQ_TOTAL = Counter("llm_requests_total",
                    "Total LLM requests",
                    ["model", "status"])
REQ_LAT = Histogram("llm_request_seconds",
                    "End-to-end LLM request latency",
                    ["model"],
                    buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0))
KV_USED = Gauge("vllm_kv_cache_used_perc",
                "Fraction of KV-cache used",
                ["model"])

# 2) start the metrics server (sidecar in a real app)
start_http_server(9100)
print("metrics: http://localhost:9100/metrics")


# %% color=teal title="3) simulate traffic"
# @explain: 3) simulate traffic — measure with the metrics
# @explain: Spawn a couple of pretend workers
# 3) simulate traffic — measure with the metrics
def fake_request(model="qwen2.5"):
    start = time.time()
    time.sleep(random.uniform(0.05, 1.5))      # pretend the model ran
    ok = random.random() > 0.05                # 5% error
    REQ_TOTAL.labels(model=model, status="ok" if ok else "err").inc()
    REQ_LAT.labels(model=model).observe(time.time() - start)
    KV_USED.labels(model=model).set(random.uniform(0.2, 0.95))

# Spawn a couple of pretend workers
def worker():
    while True:
        fake_request()

for _ in range(4):
    threading.Thread(target=worker, daemon=True).start()

time.sleep(2)
print(generate_latest(REGISTRY).decode().splitlines()[:25])


# %% [markdown] color=sky title="The patterns to internalise"
# # The patterns to internalise
#
# **The patterns to internalise.**
# - **Define metrics once** at module scope. Defining inside a request handler creates duplicates.
# - **Labels turn one metric into many time series**. Be careful — *high-cardinality* labels (user_id, request_id) explode your Prometheus.
# - **`.observe()`** for histograms; **`.inc()`** for counters; **`.set()`** for gauges.
# - The `/metrics` endpoint is plain text in the **Prometheus exposition format**.


# %% [markdown] color=mint title="5 · Run Prometheus + scrape your service"
# # 5 · Run Prometheus + scrape your service
#


# %% color=peach title="prom_yaml = '''global"
# @explain: Run this cell to see the output.
prom_yaml = '''global:
  scrape_interval: 15s

scrape_configs:
  - job_name: my_llm
    static_configs:
      - targets: ['localhost:9100']
        labels: { service: 'llm-api', env: 'dev' }
'''
print(prom_yaml)


# %% [markdown] color=violet title="in a real shell:"
# # in a real shell:
#
# ```bash
# # in a real shell:
# docker run -d --network=host \
#     -v $PWD/prometheus.yml:/etc/prometheus/prometheus.yml \
#     prom/prometheus
#
# # Prometheus UI: http://localhost:9090
# # the same /metrics you exposed → now scraped every 15s
# …


# %% [markdown] color=amber title="6 · PromQL — the 8 functions you'll actually use"
# # 6 · PromQL — the 8 functions you'll actually use
#


# %% color=rose title="2"
# @explain: 2
# @explain: 3
# @explain: 4
# @explain: 5
# @explain: 6
promql_cheatsheet = '''# 1. simple selector — instantaneous value
llm_requests_total

# 2. rate() — per-second over a window (use this for counters!)
rate(llm_requests_total[5m])

# 3. sum + by — aggregate across labels
sum by (model) (rate(llm_requests_total[5m]))

# 4. error rate
sum(rate(llm_requests_total{status="err"}[5m]))
  /
sum(rate(llm_requests_total[5m]))

# 5. p95 latency from a histogram
histogram_quantile(
  0.95,
  sum by (le, model) (rate(llm_request_seconds_bucket[5m]))
)

# 6. avg memory used
avg by (instance) (vllm_kv_cache_used_perc)

# 7. compare to last week — anomaly detection
rate(llm_requests_total[5m])
  / on(model) ignoring(env)
rate(llm_requests_total[5m] offset 1w)

# 8. recording rule — pre-compute expensive queries every minute
# saved in prometheus.rules.yml; queries reference it as `llm:rps:5m`
'''
print(promql_cheatsheet)


# %% [markdown] color=lime title="Things that bite you"
# # Things that bite you
#
# **Things that bite you.**
# - **Always `rate()` a counter** before summing — the raw value is monotonic across pod restarts.
# - **`sum(rate(...))` not `rate(sum(...))`** — order matters; the first is correct.
# - **Use `histogram_quantile()` on the `_bucket` series**, not the `_sum` / `_count`.
# - **Never compare a counter to a gauge directly** — different semantics.


# %% [markdown] color=teal title="7 · Grafana — building an LLM dashboard"
# # 7 · Grafana — building an LLM dashboard
#
# Grafana is the canonical UI on top of Prometheus. Each **panel** runs a PromQL query.
#
# **A solid LLM dashboard has 6-8 panels:**
# 1. **RPS** — `sum by (model) (rate(llm_requests_total[1m]))`
# 2. **Error rate** — the formula from §6
# 3. **p50 / p95 / p99 latency** — three lines from `histogram_quantile`
# …


# %% [markdown] color=sky title="8 · Alertmanager — rules + routing"
# # 8 · Alertmanager — rules + routing
#


# %% color=mint title="alert_rules = '''groups"
# @explain: Run this cell to see the output.
alert_rules = '''groups:
- name: llm
  rules:
  - alert: LLMHighErrorRate
    expr: |
      sum(rate(llm_requests_total{status="err"}[5m]))
        / sum(rate(llm_requests_total[5m])) > 0.02
    for: 10m         # must hold for 10 min before firing — kills flapping
    labels:    { severity: page }
    annotations:
      summary: "LLM error rate >2% for 10m"
      runbook: "https://wiki.example.com/runbooks/llm-errors"

  - alert: LLMP95LatencyHigh
    expr: |
      histogram_quantile(
        0.95,
        sum by (le, model) (rate(llm_request_seconds_bucket[5m]))
      ) > 5
    for: 10m
    labels: { severity: warn }
    annotations: { summary: "p95 latency > 5s" }

  - alert: KVCacheNearFull
    expr: avg by (model) (vllm_kv_cache_used_perc) > 0.9
    for: 5m
    labels: { severity: warn }
    annotations: { summary: "KV cache > 90% — scale up" }
'''
print(alert_rules)


# %% [markdown] color=peach title="Alertmanager** receives firing alerts and…"
# # Alertmanager** receives firing alerts and…
#
# **Alertmanager** receives firing alerts and **routes** them to Slack / PagerDuty / email based on labels. Killer features:
# - **Silences** — mute a class of alerts during planned maintenance.
# - **Inhibition** — if "cluster-down" is firing, don't also page for every "service-down" inside it.
# - **Grouping** — bundle related alerts into one message (`group_by: ['alertname','cluster']`).


# %% [markdown] color=violet title="9 · ML-specific exporters"
# # 9 · ML-specific exporters
#
# Almost every ML-infra component already speaks Prometheus.
#
# | Exporter / source | Metrics |
# |---|---|
# | **DCGM exporter** (NVIDIA) | per-GPU util, memory, power, temp, ECC errors |
# | **vLLM** built-in `/metrics` | `vllm_avg_generation_throughput_toks_per_s`, `vllm_num_requests_*`, `vllm_kv_cache_usage_perc`, `vllm_request_*` histograms |
# …


# %% [markdown] color=amber title="10 · What to actually alert on (RED / USE / SLOs)"
# # 10 · What to actually alert on (RED / USE / SLOs)
#
# | Mental model | Where it shines |
# |---|---|
# | **RED** — Rate, Errors, Duration | per-service alerts (gRPC, HTTP, LLM endpoints) |
# | **USE** — Utilisation, Saturation, Errors | per-resource alerts (GPU, CPU, disk, network, KV-cache) |
# | **SLOs** — error budget burn rate | "is the user-perceived experience OK?" — high-signal alerts only |
#
# …


# %% [markdown] color=rose title="✅ Recap"
# # ✅ Recap
#
# - Prometheus pulls metrics from `/metrics` endpoints; Grafana queries Prometheus; Alertmanager routes alerts.
# - Four metric types: **counter, gauge, histogram, summary** — pick the right one per signal.
# - PromQL: `rate()` on counters → `sum by` → `histogram_quantile`.
# - Alert on **user-impact SLO burn rate**, not raw resource numbers.
# - ML-native exporters (DCGM, vLLM, Triton) make GPU + LLM observability free.
#
# Next: **M51 — OpenTelemetry for LLMs** (the trace half of the observability story).


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


