# doodlecode format-version: 2
# Auto-converted from module_46_kubernetes_for_ml.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 46 Kubernetes For Ml"
# # Module 46 Kubernetes For Ml
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 46 — Kubernetes for ML"
# # Module 46 — Kubernetes for ML
#
# > By M44 you had a vLLM server, by M45 a gRPC plumbing layer. Now: how do you actually **run that** in production with autoscaling, rolling updates, GPU scheduling, secrets, and survivable storage? The answer for the last decade has been **Kubernetes** (k8s). This module gives you the minimum viable mental model — focused on **the bits that matter for ML**: GPU pods, model storage, autoscaling on QPS, and the ML-native stack on top (KServe, KubeRay, Kubeflow).
#
# > 🟡 You won't run a real cluster from this notebook. Treat the YAML below as **production-shaped reference**: copy it into your own cluster (`minikube`, `kind`, EKS/GKE/AKS) and `kubectl apply -f`.
#
# ### What you'll cover
# 1. The 5 objects that cover 95% of ML deployments
# …


# %% [markdown] color=mint title="1 · The 5 objects that cover 95% of ML deployments"
# # 1 · The 5 objects that cover 95% of ML deployments
#
# ```
#    ┌────────────────────── Cluster ─────────────────────────┐
#    │                                                        │
#    │   Deployment ──manages──► ReplicaSet ──manages──► Pod  │
#    │                                                  │     │
#    │              Service ◄──selector───────►         │     │
# …


# %% [markdown] color=peach title="2 · Pod — a container with **GPU**"
# # 2 · Pod — a container with **GPU**
#


# %% color=violet title="pod_yaml = '''apiVersion: v1"
# @explain: Run this cell to see the output.
pod_yaml = '''apiVersion: v1
kind: Pod
metadata:
  name: vllm-llama-3
  labels: { app: llm }
spec:
  containers:
  - name: vllm
    image: vllm/vllm-openai:latest
    args: ["--model","Qwen/Qwen2.5-0.5B-Instruct","--port","8000"]
    ports: [{containerPort: 8000}]
    resources:
      limits:
        nvidia.com/gpu: 1          # request 1 GPU
        memory: "16Gi"
        cpu:    "4"
      requests:
        nvidia.com/gpu: 1
        memory: "12Gi"
        cpu:    "2"
    volumeMounts:
    - name: hf-cache
      mountPath: /root/.cache/huggingface
  volumes:
  - name: hf-cache
    persistentVolumeClaim: { claimName: hf-cache-pvc }
  nodeSelector:
    accelerator: nvidia-l4         # only schedule on GPU nodes
  tolerations:
  - key: nvidia.com/gpu
    operator: Exists
    effect: NoSchedule
'''
print(pod_yaml)


# %% [markdown] color=amber title="Key bits"
# # Key bits
#
# **Key bits.**
# - `nvidia.com/gpu: 1` is how you ask for a GPU. Cluster needs the **NVIDIA device plugin** installed (one DaemonSet on each GPU node).
# - `nodeSelector` + `tolerations` keep CPU pods off GPU nodes (they're expensive — every µs of idle GPU is wasted money).
# - `requests` are the floor used by the scheduler; `limits` are the ceiling enforced by the kernel cgroup.


# %% [markdown] color=rose title="3 · Deployment — N replicas + rolling updates"
# # 3 · Deployment — N replicas + rolling updates
#


# %% color=lime title="deploy_yaml = '''apiVersion: apps/v1"
# @explain: Run this cell to see the output.
deploy_yaml = '''apiVersion: apps/v1
kind: Deployment
metadata:
  name: vllm-llama-3
spec:
  replicas: 3
  selector:
    matchLabels: { app: llm }
  strategy:
    type: RollingUpdate
    rollingUpdate: { maxSurge: 1, maxUnavailable: 0 }
  template:
    metadata:
      labels: { app: llm }
    spec:
      containers:
      - name: vllm
        image: vllm/vllm-openai:latest
        args: ["--model","Qwen/Qwen2.5-0.5B-Instruct","--port","8000"]
        ports: [{containerPort: 8000, name: http}]
        readinessProbe: { httpGet: { path: /v1/models, port: http }, periodSeconds: 5 }
        livenessProbe:  { httpGet: { path: /health,    port: http }, periodSeconds: 30 }
        resources: { limits: { nvidia.com/gpu: 1 }, requests: { nvidia.com/gpu: 1 } }
'''
print(deploy_yaml[:600], "...")


# %% [markdown] color=teal title="Why probes matter for LLMs"
# # Why probes matter for LLMs
#
# **Why probes matter for LLMs.**
# - `readinessProbe` removes a Pod from the Service while the model is still **loading** (can take minutes for 70B). Without this, the first traffic to a fresh replica errors.
# - `livenessProbe` restarts a Pod that's deadlocked. Use it sparingly — a misconfigured liveness probe under load creates a restart storm.


# %% [markdown] color=sky title="4 · Service + Ingress — networking"
# # 4 · Service + Ingress — networking
#


# %% color=mint title="svc_yaml = '''apiVersion: v1"
# @explain: Run this cell to see the output.
svc_yaml = '''apiVersion: v1
kind: Service
metadata: { name: llm-svc }
spec:
  selector: { app: llm }
  ports:
  - { name: http, port: 80, targetPort: 8000 }
  type: ClusterIP
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: llm-ingress
  annotations:
    nginx.ingress.kubernetes.io/proxy-read-timeout: "600"   # LLM streams are slow
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls: [{ hosts: ["api.example.com"], secretName: api-tls }]
  rules:
  - host: api.example.com
    http:
      paths:
      - { path: /v1, pathType: Prefix, backend: { service: { name: llm-svc, port: { number: 80 } } } }
'''
print(svc_yaml)


# %% [markdown] color=peach title="- **Service** picks Pods by label"
# # - **Service** picks Pods by label
#
# - **Service** picks Pods by label (`app: llm`) and load-balances traffic among them.
# - **Ingress** terminates TLS at the edge and routes by hostname/path. **Bump `proxy-read-timeout`** for LLM streams — defaults are too short.


# %% [markdown] color=violet title="5 · ConfigMap + Secret"
# # 5 · ConfigMap + Secret
#


# %% color=amber title="in the Pod spec"
# @explain: in the Pod spec:
# @explain: envFrom: [{ configMapRef: { name: llm-cfg } }, { secretRef: { name: hf-token } }]
cfg_yaml = '''apiVersion: v1
kind: ConfigMap
metadata: { name: llm-cfg }
data:
  MAX_MODEL_LEN: "4096"
  GPU_MEM_UTIL:  "0.9"
---
apiVersion: v1
kind: Secret
metadata: { name: hf-token }
type: Opaque
stringData:
  HUGGING_FACE_HUB_TOKEN: hf_xxxxxxxxxxxxxxxxxxxxxxxxxx
'''
# in the Pod spec:
#   envFrom: [{ configMapRef: { name: llm-cfg } }, { secretRef: { name: hf-token } }]
print(cfg_yaml)


# %% [markdown] color=rose title="Don't put secrets in Git.** Either use **Sealed…"
# # Don't put secrets in Git.** Either use **Sealed…
#
# **Don't put secrets in Git.** Either use **Sealed Secrets**, **External Secrets Operator** + a real vault (AWS Secrets Manager, HashiCorp Vault, GCP Secret Manager), or your cloud's CSI driver. ConfigMaps are fine for non-sensitive config.


# %% [markdown] color=lime title="6 · PersistentVolume + PVC — model weights"
# # 6 · PersistentVolume + PVC — model weights
#


# %% color=teal title="pvc_yaml = '''apiVersion: v1"
# @explain: Run this cell to see the output.
pvc_yaml = '''apiVersion: v1
kind: PersistentVolumeClaim
metadata: { name: hf-cache-pvc }
spec:
  accessModes: [ ReadWriteMany ]      # so multiple Pods share the cache
  storageClassName: efs-sc            # AWS EFS / GCP Filestore / Azure Files
  resources: { requests: { storage: 200Gi } }
'''
print(pvc_yaml)


# %% [markdown] color=sky title="LLMs love `ReadWriteMany`"
# # LLMs love `ReadWriteMany`
#
# LLMs love `ReadWriteMany`. Why? You don't want every Pod to download a 30 GB model from S3 on cold start — they share one **EFS / Filestore / Azure Files** volume. First Pod warms it; the rest start in seconds.
#
# **Alternative:** bake weights into the **container image**. Faster cold start, slower image pulls, image registry quota. Pick one strategy and stick to it.


# %% [markdown] color=mint title="7 · Job + CronJob — training and batch"
# # 7 · Job + CronJob — training and batch
#


# %% color=peach title="job_yaml = '''apiVersion: batch/v1"
# @explain: Run this cell to see the output.
job_yaml = '''apiVersion: batch/v1
kind: Job
metadata: { name: nightly-eval }
spec:
  backoffLimit: 1
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: eval
        image: my-org/eval:1.4.2
        command: ["python","-m","eval.run","--model","qwen2.5"]
        resources: { limits: { nvidia.com/gpu: 1 } }
---
apiVersion: batch/v1
kind: CronJob
metadata: { name: reindex-corpus }
spec:
  schedule: "0 3 * * *"            # 03:00 UTC daily
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: OnFailure
          containers:
          - name: reindex
            image: my-org/reindex:1.0.0
'''
print(job_yaml)


# %% [markdown] color=violet title="Use **Job** for one-shot work (training run, eval…"
# # Use **Job** for one-shot work (training run, eval…
#
# Use **Job** for one-shot work (training run, eval suite, data backfill). Use **CronJob** for repeating work (nightly re-index of your RAG corpus, weekly model eval, hourly metrics roll-up).


# %% [markdown] color=amber title="8 · Autoscaling — HPA on QPS / GPU"
# # 8 · Autoscaling — HPA on QPS / GPU
#


# %% color=rose title="hpa_yaml = '''apiVersion: autoscaling/v2"
# @explain: Run this cell to see the output.
hpa_yaml = '''apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata: { name: vllm-hpa }
spec:
  scaleTargetRef: { apiVersion: apps/v1, kind: Deployment, name: vllm-llama-3 }
  minReplicas: 1
  maxReplicas: 8
  metrics:
  - type: Resource
    resource: { name: cpu, target: { type: Utilization, averageUtilization: 70 } }
  - type: Pods
    pods:
      metric: { name: vllm_requests_per_second }     # custom metric via Prometheus adapter
      target: { type: AverageValue, averageValue: "30" }
  behavior:
    scaleUp:   { stabilizationWindowSeconds: 30 }
    scaleDown: { stabilizationWindowSeconds: 300 }
'''
print(hpa_yaml)


# %% [markdown] color=lime title="For LLM workloads, raw CPU is a terrible signal** —…"
# # For LLM workloads, raw CPU is a terrible signal** —…
#
# **For LLM workloads, raw CPU is a terrible signal** — your bottleneck is GPU compute and KV-cache memory. Better signals:
# - **Custom metrics** (Prometheus adapter) like `vllm_requests_per_second` or `vllm_gpu_kv_cache_usage_perc`.
# - **DCGM** GPU utilisation via `dcgm-exporter`.
# - For very bursty workloads, **KEDA** with queue depth from Redis Streams / SQS / Kafka.
#
# Also: cluster-level **Cluster Autoscaler** or **Karpenter** brings up new GPU nodes when pods are unschedulable. Pod scaling without node scaling = pending pods.


# %% [markdown] color=teal title="9 · ML-native — KServe, KubeRay, Kubeflow"
# # 9 · ML-native — KServe, KubeRay, Kubeflow
#
# Plain k8s gives you boxes and networking. The **ML-native stack** layered on top gives you:
#
# | Project | What it adds |
# |---|---|
# | **KServe** | a CRD for "InferenceService" → autoscaling LLM/CV/NLP servers, canary routing, scale-to-zero |
# | **KubeRay** | run Ray clusters on k8s — distributed training (PyTorch DDP), batch RAG, agent fleets |
# …


# %% [markdown] color=sky title="10 · Day-2 ops + anti-patterns"
# # 10 · Day-2 ops + anti-patterns
#
# | Topic | What to do |
# |---|---|
# | **GitOps** | Argo CD or Flux — your cluster state lives in Git, never `kubectl apply` from a laptop |
# | **Helm** | bundle related YAML into one releasable chart (M47) |
# | **Secrets** | Sealed Secrets or External Secrets — never plain `Secret` in Git |
# | **Observability** | Prometheus + Grafana (M50), OpenTelemetry traces (M51) |
# …


# %% [markdown] color=mint title="✅ Recap"
# # ✅ Recap
#
# - 5 objects: Pod · Deployment · Service · Ingress · ConfigMap/Secret. PVC for state, Job/CronJob for batch.
# - GPU: `nvidia.com/gpu: 1` resource + node selector + toleration + the GPU Operator on the cluster.
# - Autoscale on **GPU/QPS metrics**, not CPU. Add **KEDA** for queue-driven scaling.
# - ML-native: **KServe** for serving, **KubeRay** for distributed training, **Kubeflow** for pipelines.
# - Day-2: GitOps, Helm, externalised secrets, Prometheus/Grafana (M50), OTel (M51).
#
# Next: **M47 — Helm Charts for ML** (templating + releasing the YAML you just wrote).


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


