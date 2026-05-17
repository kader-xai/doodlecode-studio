# doodlecode format-version: 2
# Auto-converted from module_47_helm_charts_for_ml.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 47 Helm Charts For Ml"
# # Module 47 Helm Charts For Ml
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 47 — Helm Charts for ML"
# # Module 47 — Helm Charts for ML
#
# > M46 had Pods, Deployments, Services, PVCs — six YAML files for **one** vLLM deployment. Multiply by dev / staging / prod environments and a handful of models, and you're hand-editing dozens of files. **Helm** is the package manager for Kubernetes: bundle related YAML into a **chart**, parameterise it with **values**, install many copies as named **releases**.
# >
# > Almost every ML-native project ships its installation as a Helm chart: KServe, KubeRay, MLflow, Prometheus, NVIDIA GPU Operator. Knowing Helm is non-optional for production ML on k8s.
#
# ### What you'll cover
# 1. The 5-minute mental model — Chart, Values, Release
# …


# %% [markdown] color=mint title="1 · 5-minute mental model"
# # 1 · 5-minute mental model
#
# | Term | What it is | Analogy |
# |---|---|---|
# | **Chart** | a directory of templated YAML + a values schema | a package (`.deb`, `npm` module) |
# | **Values** | parameters you supply at install time | the `--config` flags |
# | **Release** | a *named installation* of a chart in a cluster | `apt install` invocation that you can `apt remove` |
# | **Repository** | a server hosting many charts | apt repo, npm registry |
# …


# %% [markdown] color=peach title="2 · Anatomy of a chart"
# # 2 · Anatomy of a chart
#
# ```
# my-vllm/
# ├── Chart.yaml          # name, version, appVersion, dependencies
# ├── values.yaml         # default parameters
# ├── values.schema.json  # (optional) validate values at install time
# ├── templates/
# …


# %% [markdown] color=violet title="3 · Templates — Go templating + sprig"
# # 3 · Templates — Go templating + sprig
#
# Every file in `templates/` is rendered through Go's `text/template` plus the **sprig** function library.


# %% color=amber title="deployment_tpl = '''apiVersion: apps/v1"
# @explain: Run this cell to see the output.
deployment_tpl = '''apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "my-vllm.fullname" . }}
  labels:
    {{- include "my-vllm.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicas }}
  selector:
    matchLabels:
      {{- include "my-vllm.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "my-vllm.selectorLabels" . | nindent 8 }}
    spec:
      containers:
      - name: vllm
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
        args:
        - --model
        - {{ .Values.model | quote }}
        - --max-model-len
        - {{ .Values.maxModelLen | quote }}
        ports:
        - containerPort: 8000
        {{- with .Values.resources }}
        resources:
          {{- toYaml . | nindent 10 }}
        {{- end }}
        envFrom:
        - secretRef:
            name: {{ include "my-vllm.fullname" . }}-hf-token
'''
print(deployment_tpl[:600], "...")


# %% [markdown] color=rose title="Idioms in that template"
# # Idioms in that template
#
# **Idioms in that template.**
# - `.Values.X` — a parameter from `values.yaml`.
# - `include "my-vllm.fullname" .` — call a named template defined in `_helpers.tpl`.
# - `| nindent 4` — pipe through a function that adds a newline + indents 4 spaces. **The single most common Helm bug: wrong indentation.**
# - `{{- ... -}}` — the dashes trim surrounding whitespace.
# - `toYaml . | nindent N` — splat a values block (like `resources:`) into the template.
# - `{{ .Values.x | quote }}` — wrap in quotes (matters for stringly-typed args).


# %% [markdown] color=lime title="4 · values.yaml — your chart's API"
# # 4 · values.yaml — your chart's API
#


# %% color=teal title="values_yaml = '''replicas: 2"
# @explain: Run this cell to see the output.
values_yaml = '''replicas: 2

image:
  repository: vllm/vllm-openai
  tag: latest
  pullPolicy: IfNotPresent

model: Qwen/Qwen2.5-0.5B-Instruct
maxModelLen: 4096

resources:
  limits:
    nvidia.com/gpu: 1
    memory: 16Gi
    cpu: "4"
  requests:
    nvidia.com/gpu: 1
    memory: 12Gi
    cpu: "2"

service:
  type: ClusterIP
  port: 80

ingress:
  enabled: false
  className: nginx
  host: api.example.com

autoscaling:
  enabled: true
  minReplicas: 1
  maxReplicas: 8
  targetCPU: 70

hf:
  token: ""             # set via --set hf.token=$HF_TOKEN

extraEnv: []            # users can append env vars without forking
'''
print(values_yaml)


# %% [markdown] color=sky title="Design rules for `values.yaml`"
# # Design rules for `values.yaml`
#
# **Design rules for `values.yaml`.**
# 1. Group related fields (`image.*`, `service.*`, `ingress.*`).
# 2. Sensible defaults so `helm install foo my-vllm` *just works*.
# 3. **Add `enabled` toggles** for optional parts (`ingress.enabled`, `autoscaling.enabled`) — wrap their templates in `{{- if .Values.ingress.enabled }}`.
# 4. Always provide an `extraEnv` / `extraArgs` / `nodeSelector` / `tolerations` escape hatch so users don't have to fork the chart.


# %% [markdown] color=mint title="5 · Scaffold a chart in 1 minute"
# # 5 · Scaffold a chart in 1 minute
#
# ```bash
# $ helm create my-vllm        # generates a working starter chart
# $ tree my-vllm
# my-vllm/
# ├── Chart.yaml
# ├── values.yaml
# …


# %% [markdown] color=peach title="6 · install / upgrade / rollback / uninstall"
# # 6 · install / upgrade / rollback / uninstall
#
# ```bash
# # install — release name "llm-prod", chart in ./my-vllm, values from prod.yaml
# helm install llm-prod ./my-vllm -f values-prod.yaml --namespace llm --create-namespace
#
# # upgrade with new values or new chart version
# helm upgrade llm-prod ./my-vllm -f values-prod.yaml --set image.tag=v0.6.5
# …


# %% [markdown] color=violet title="7 · Dependencies — composing charts"
# # 7 · Dependencies — composing charts
#


# %% color=amber title="chart_yaml = '''apiVersion: v2"
# @explain: Run this cell to see the output.
chart_yaml = '''apiVersion: v2
name: my-vllm
description: vLLM deployment with Redis cache
type: application
version: 0.1.0
appVersion: "0.6.4"
dependencies:
  - name: redis
    version: 19.0.0
    repository: https://charts.bitnami.com/bitnami
    condition: redis.enabled
'''
print(chart_yaml)


# %% [markdown] color=rose title="```bash"
# # ```bash
#
# ```bash
# $ helm dependency update my-vllm/   # downloads sub-charts into charts/
# $ helm install demo my-vllm/ \
#     --set redis.enabled=true \
#     --set redis.auth.password=secret123
# ```
#
# Sub-charts let you reuse battle-tested components (Redis, Postgres, Kafka, MinIO) instead of re-templating them. Their values nest under their chart name (`redis.*` above).


# %% [markdown] color=lime title="8 · Hooks — pre-install, test"
# # 8 · Hooks — pre-install, test
#


# %% color=teal title="hook_yaml = '''apiVersion: batch/v1"
# @explain: Run this cell to see the output.
hook_yaml = '''apiVersion: batch/v1
kind: Job
metadata:
  name: {{ include "my-vllm.fullname" . }}-warmup
  annotations:
    "helm.sh/hook": post-install,post-upgrade
    "helm.sh/hook-delete-policy": before-hook-creation,hook-succeeded
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: warmup
        image: curlimages/curl:8.7.1
        command: ["sh","-c","until curl -sf http://{{ include "my-vllm.fullname" . }}/v1/models; do sleep 5; done"]
'''
print(hook_yaml)


# %% [markdown] color=sky title="Common hook phases.** `pre-install`"
# # Common hook phases.** `pre-install`
#
# **Common hook phases.** `pre-install`, `post-install`, `pre-upgrade`, `post-upgrade`, `pre-delete`, `post-delete`, `test`.
#
# **`helm test`** — `templates/tests/*.yaml` annotated with `"helm.sh/hook": test` are run by `helm test <release>`. A typical ML smoke test: hit `/v1/models` and assert it returns the expected model.


# %% [markdown] color=mint title="9 · Helmfile / Argo CD — managing 50 charts"
# # 9 · Helmfile / Argo CD — managing 50 charts
#
# Once you have many charts, `helm install` from a laptop stops scaling. Two paths:
#
# ### Helmfile (script-style)
# ```yaml
# # helmfile.yaml
# releases:
# …


# %% [markdown] color=peach title="10 · ML-specific charts you'll meet"
# # 10 · ML-specific charts you'll meet
#
# | Chart | Installs |
# |---|---|
# | `kserve/kserve` | KServe ModelMesh + InferenceService CRDs |
# | `kuberay/kuberay-operator` | Ray on Kubernetes |
# | `kubeflow/training-operator` | PyTorch / TF / XGBoost distributed training CRDs |
# | `nvidia/gpu-operator` | drivers + device plugin + DCGM exporter |
# …


# %% [markdown] color=violet title="✅ Recap"
# # ✅ Recap
#
# - **Chart** = templates + values + metadata. **Release** = a named installation.
# - `helm create` → edit `values.yaml` → render with `helm template` → `helm install`.
# - Use **sub-charts** to compose (your app + Redis + Postgres).
# - **Hooks** for warmup/migrations; `helm test` for smoke tests.
# - Production: GitOps via **Argo CD**, not laptop `helm install`.
# - The ML-native ecosystem ships almost entirely as Helm charts.
#
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


