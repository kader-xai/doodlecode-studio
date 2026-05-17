# doodlecode format-version: 2
# Auto-converted from module_78_bare_metal_provisioning_parallel_storage.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 78 Bare Metal Provisioning Parallel Storage"
# # Module 78 Bare Metal Provisioning Parallel Storage
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 78 — Bare-Metal Provisioning + Parallel Storage"
# # Module 78 — Bare-Metal Provisioning + Parallel Storage
#
# > The course assumed cloud everywhere — `terraform apply` → EKS cluster (M48), `kubectl get nodes` → eight A100s appear (M46). **The frontier doesn't run that way.** Every serious AI lab — Anthropic, OpenAI, xAI, Meta, Mistral — runs at least some of its training fleet on **bare-metal servers** in **co-located data centres** using **parallel filesystems** they themselves operate. This module is that world: the racks, the PXE boots, the Lustre mounts, the IPMI fan curves.
# >
# > You won't run a real MAAS controller from Colab, but every command here is what you'd type in front of an actual rack.
#
# ### What you'll cover
# 1. Bare-metal vs cloud — why frontier labs run both
# …


# %% [markdown] color=mint title="1 · Bare-metal vs cloud — why both"
# # 1 · Bare-metal vs cloud — why both
#
# | Dimension | Cloud (M48 Terraform → EKS) | Bare-metal |
# |---|---|---|
# | **Time to first node** | minutes | weeks of physical install |
# | **Cost per H100/hr** | ~$2.50-5 on-demand; ~$1.50-2.50 reserved | ~$0.40-0.80 amortised over 3 yrs |
# | **GPU availability** | rationed; long waits for H100/B200 in 2024-25 | you own them |
# | **Networking** | best-effort 100/200 Gb | choose your own NDR/XDR IB |
# …


# %% [markdown] color=peach title="2 · MAAS — Metal as a Service"
# # 2 · MAAS — Metal as a Service
#
# Canonical's open-source tool to turn empty racks into a cloud-shaped API.
#
# ```
#    ┌────────────────────────────────────────────────────────────┐
#    │  MAAS region controller (PostgreSQL + Python service)      │
#    │   - inventory of every NIC / disk / BMC                    │
# …


# %% color=violet title="Typical MAAS CLI workflow once you've added racks…"
# @explain: Typical MAAS CLI workflow once you've added racks to the controller
# @explain: Authenticate
# @explain: See pools / machines
# @explain: Tag the GPU nodes for kubeadm
# @explain: Allocate + deploy 4 of them with a Ubuntu 24.04 + user-data file
# Typical MAAS CLI workflow once you've added racks to the controller
maas_cli = '''
# Authenticate
$ maas login admin http://maas:5240/MAAS $API_KEY

# See pools / machines
$ maas admin machines read | jq '.[] | {hostname, status, power_state}'

# Tag the GPU nodes for kubeadm
$ maas admin tag create name=gpu-h100 comment="DGX H100 boxes"
$ maas admin tag update-nodes gpu-h100 add=node1,node2,node3,node4

# Allocate + deploy 4 of them with a Ubuntu 24.04 + user-data file
$ for h in node1 node2 node3 node4; do
    maas admin machine deploy $h \
        distro_series=noble \
        user_data="$(base64 < cloud-init.yaml)" \
        hwe_kernel=ga-24.04 ;
  done

# Power-off everything (Redfish / IPMI under the hood)
$ maas admin machines power-off filter='tags=gpu-h100'
'''
print(maas_cli)


# %% [markdown] color=amber title="Alternatives** you'll meet"
# # Alternatives** you'll meet
#
# **Alternatives** you'll meet:
# - **Foreman + Katello** — Red Hat ecosystem, similar PXE + image story.
# - **Tinkerbell** — CNCF, Kubernetes-native bare-metal provisioning (used by Equinix Metal, OpenStack Ironic alternatives).
# - **Cluster Manager / xCAT / Bright** — HPC-flavoured (Slurm-heavy clusters).
# - **OpenStack Ironic** — bare-metal as part of an OpenStack deployment.
# - **Tarmak / Sidero Metal / Talos Linux** — k8s-first bare-metal stacks.


# %% [markdown] color=rose title="3 · Redfish / IPMI / BMC — the management plane"
# # 3 · Redfish / IPMI / BMC — the management plane
#
# Every server has a **Baseboard Management Controller (BMC)** — a tiny computer that runs even when the server is powered off. It listens on a dedicated network port and gives you:
#
# - **Power** — `power on`, `power off`, `power cycle`.
# - **Console** — KVM-over-IP for BIOS-level debugging.
# - **Sensors** — temperatures, fan RPM, voltages, PSU status.
# - **Inventory** — model numbers, firmware versions.
# …


# %% [markdown] color=lime title="4 · cloud-init — the post-install hook"
# # 4 · cloud-init — the post-install hook
#
# PXE boots the kernel. The kernel mounts root. Then **cloud-init** runs `user_data` — a YAML file that customises the box on first boot.
#
# ```yaml
# # cloud-init.yaml — bare-metal user_data file
# #cloud-config
#
# …


# %% [markdown] color=teal title="5 · Parallel filesystems — the data layer that frontier training needs"
# # 5 · Parallel filesystems — the data layer that frontier training needs
#
# A training cluster reads from a corpus that's bigger than any one node. Writes go to gigabyte checkpoints from every rank simultaneously. A single NFS server collapses under that load. **Parallel filesystems** (PFS) solve it.
#
# ```
#                           ┌──────────── compute nodes ────────────┐
#                           │   GPU0 GPU1 GPU2 GPU3   GPU4 ...      │
#                           └─┬────┬────┬────┬─────────┬────────────┘
# …


# %% [markdown] color=sky title="6 · Local NVMe — the hot tier"
# # 6 · Local NVMe — the hot tier
#
# Even with Lustre at 1 TB/s, the cheapest fast storage is **local NVMe on every GPU node**. Two patterns:
#
# | Pattern | Use |
# |---|---|
# | **Scratch** | per-job, per-node — `/scratch/$JOB_ID/` mounted as `tmpfs` or local NVMe. Wiped on exit. |
# | **Local dataset cache** | every node caches the same shard of the dataset. The training script reads local; only first epoch touches the PFS. |
# …


# %% [markdown] color=mint title="7 · Object storage — checkpoints + dataset cold tier"
# # 7 · Object storage — checkpoints + dataset cold tier
#
# Models like to write **big** checkpoints. Llama-3-405B in fp16 is ~810 GB. Saving every 1000 steps over a 6-month run = thousands of multi-hundred-GB checkpoints. Object storage handles it.
#
# | Layer | What |
# |---|---|
# | **S3 / GCS / Azure Blob** | the default cloud answer. `s3a://` or `s3://` mountable from PyTorch / Spark. |
# | **MinIO** | OSS, S3-compatible. Run on your own NVMe pool. |
# …


# %% [markdown] color=peach title="8 · Slurm vs Kubernetes — scheduling for HPC + ML"
# # 8 · Slurm vs Kubernetes — scheduling for HPC + ML
#
# You have racks, fabric, parallel FS. Now **schedule jobs**.
#
# | Property | **Slurm** | **Kubernetes (M46)** |
# |---|---|---|
# | Heritage | HPC, batch | cloud-native, services |
# | Job shape | `sbatch script.sh`, multi-node MPI | pods, deployments, jobs, statefulsets |
# …


# %% [markdown] color=violet title="9 · Day-2 ops — the silent killers"
# # 9 · Day-2 ops — the silent killers
#
# Hardware breaks. At 1000 GPUs and 5 9s per GPU-hour, expect **~1 GPU failure per day**. The list of things you must monitor:
#
# | Subsystem | What to watch | Tool |
# |---|---|---|
# | **GPU** | ECC errors, NVLink errors, Xid messages, throttling | **DCGM** + `dcgm-exporter` (M50) |
# | **NIC** | IB link errors, RoCE PFC pauses, dropped packets | `ibcheckerrors`, switch telemetry |
# …


# %% [markdown] color=amber title="10 · The 2026 reference architectures"
# # 10 · The 2026 reference architectures
#
# What real frontier shops actually build looks like one of these:
#
# ### **NVIDIA DGX SuperPOD H100/H200 (reference)**
# - Compute: 8× H100/H200 per node × 32-128 nodes per SU (Scalable Unit).
# - Intra-node: NVSwitch (M77).
# - Inter-node: NDR InfiniBand fat-tree, rail-optimised.
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


