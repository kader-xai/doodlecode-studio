# doodlecode format-version: 2
# Auto-converted from module_48_terraform_for_ml.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 48 Terraform For Ml"
# # Module 48 Terraform For Ml
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 48 — Terraform for ML Infrastructure"
# # Module 48 — Terraform for ML Infrastructure
#
# > Helm (M47) configures **inside** a Kubernetes cluster. **Terraform** configures **the cluster itself** — and the VPC, subnets, IAM roles, S3 buckets, RDS instances, GPU node pools, DNS records, secrets stores, and every other cloud thing your ML platform sits on. It's how you turn "click-ops in the AWS console" into a Git-reviewed, reproducible, multi-region infrastructure.
# >
# > By the end of this module you can read 90% of real ML-platform Terraform code and contribute to it.
#
# > 🟡 We won't run `terraform apply` from this notebook (no cloud creds), but every snippet is production-shaped HCL you can drop into a `main.tf`.
#
# …


# %% [markdown] color=mint title="1 · Why IaC, why Terraform"
# # 1 · Why IaC, why Terraform
#
# Without IaC: someone clicks 47 buttons in the AWS console to create your EKS cluster. Two weeks later, nobody remembers exactly what they clicked. The disaster-recovery plan is "we hope".
#
# With IaC: the cluster is **a file in Git**. `terraform apply` recreates it from scratch in 10 minutes. Pull requests review changes. Drift detection catches console-edits.
#
# | Tool | Language | Notes |
# |---|---|---|
# …


# %% [markdown] color=peach title="2 · The 5 building blocks"
# # 2 · The 5 building blocks
#


# %% color=violet title="2) VARIABLE"
# @explain: 2) VARIABLE — typed input
# @explain: 3) DATA — read something that already exists
# @explain: 4) RESOURCE — declare something to be managed
# @explain: 5) OUTPUT — expose values to the caller
terraform_basics = '''# 1) PROVIDER — the SDK for a cloud / SaaS
terraform {
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.60" }
  }
}
provider "aws" {
  region = var.region
}

# 2) VARIABLE — typed input
variable "region"      { type = string,                      default = "us-east-1" }
variable "cluster_name"{ type = string }
variable "tags"        { type = map(string),                 default = { team = "ml" } }

# 3) DATA — read something that already exists
data "aws_caller_identity" "current" {}

# 4) RESOURCE — declare something to be managed
resource "aws_s3_bucket" "models" {
  bucket = "${var.cluster_name}-models"
  tags   = var.tags
}

# 5) OUTPUT — expose values to the caller
output "bucket_arn"   { value = aws_s3_bucket.models.arn }
output "account_id"   { value = data.aws_caller_identity.current.account_id }
'''
print(terraform_basics)


# %% [markdown] color=amber title="Reading guide"
# # Reading guide
#
# **Reading guide.**
# - `provider` = the API client. Each cloud / SaaS has one.
# - `resource "aws_s3_bucket" "models"` — *type* `aws_s3_bucket`, *local name* `models`. Refer to it later as `aws_s3_bucket.models`.
# - `data` = read-only lookup of something that exists outside Terraform.
# - `variable` = typed inputs. Pass at the CLI (`-var`), via `terraform.tfvars`, or env vars.
# - `output` = let parent modules read your computed values.


# %% [markdown] color=rose title="3 · State — the central concept"
# # 3 · State — the central concept
#
# Terraform keeps a **state file** mapping `aws_s3_bucket.models` → the real S3 bucket's ARN. `plan` and `apply` diff *desired* (your code) against *actual* (state) and call provider APIs to reconcile.
#
# | Practice | Why |
# |---|---|
# | **Remote state** (S3 + DynamoDB lock, GCS, Terraform Cloud) | Your laptop ≠ source of truth |
# | **Locking** | Two `apply`s at once corrupts state |
# …


# %% [markdown] color=lime title="4 · Modules — reuse + composition"
# # 4 · Modules — reuse + composition
#


# %% color=teal title="module_call = '''# Use a public"
# @explain: Run this cell to see the output.
module_call = '''# Use a public, battle-tested module from the Terraform registry
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"

  cluster_name    = var.cluster_name
  cluster_version = "1.30"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  eks_managed_node_groups = {
    cpu_general = {
      instance_types = ["m6a.large"]
      min_size = 2, max_size = 10, desired_size = 3
    }
    gpu_inference = {
      instance_types = ["g5.2xlarge"]            # 1× A10G GPU
      min_size = 0, max_size = 8, desired_size = 1
      labels = { workload = "gpu", accelerator = "nvidia-a10g" }
      taints = [{ key = "nvidia.com/gpu", value = "true", effect = "NO_SCHEDULE" }]
    }
  }
}
'''
print(module_call)


# %% [markdown] color=sky title="A **module** is just a directory of `.tf` files"
# # A **module** is just a directory of `.tf` files
#
# A **module** is just a directory of `.tf` files. You can write your own (`./modules/vllm-deployment/`) or pull battle-tested ones from the registry (`terraform-aws-modules/eks/aws`).
#
# Notice how the GPU node group is **scaled from 0** to N — pair with the cluster autoscaler / Karpenter to spin GPUs up only when pods are pending. **Saves real money.**


# %% [markdown] color=mint title="5 · A real ML platform — assembling it"
# # 5 · A real ML platform — assembling it
#
# ```
#                 ┌──────────── VPC ────────────┐
#                 │   public subnets / NAT      │
#                 │   private subnets (3 AZ)    │
#                 └─────────────┬───────────────┘
#                               │
# …


# %% [markdown] color=peach title="6 · The workflow"
# # 6 · The workflow
#
# ```bash
# $ terraform init       # download providers + connect to remote state
# $ terraform fmt        # canonical formatting
# $ terraform validate   # static check
# $ terraform plan -out=plan.tfplan   # what would change?
# $ terraform apply plan.tfplan       # apply that exact plan
# …


# %% [markdown] color=violet title="7 · Workspaces, environments, and remote state"
# # 7 · Workspaces, environments, and remote state
#
# Three common patterns for splitting dev / staging / prod:
#
# | Pattern | How |
# |---|---|
# | **Workspaces** (`terraform workspace`) | Same code, different state files. Quick & simple, but easy to mix up. |
# | **Directory per env** | `envs/dev/`, `envs/staging/`, `envs/prod/` each with its own `main.tf` calling the same modules. **Most common in production.** |
# …


# %% [markdown] color=amber title="8 · Secrets"
# # 8 · Secrets
#
# | Don't | Do |
# |---|---|
# | `variable "db_password" { default = "..." }` in code | use **AWS Secrets Manager** / **GCP Secret Manager** / **Vault** + `data` lookups |
# | Commit `*.tfvars` with secrets | encrypt with **SOPS**, or pass via env vars at apply time |
# | Print secrets in `output` without `sensitive = true` | mark sensitive: `output "x" { value = ..., sensitive = true }` |
# | Trust the state file because it's "internal" | encrypt the state bucket, restrict KMS access |
# …


# %% [markdown] color=rose title="9 · Terraform vs Pulumi vs CDK vs Crossplane"
# # 9 · Terraform vs Pulumi vs CDK vs Crossplane
#
# | Tool | Strengths | Weaknesses |
# |---|---|---|
# | **Terraform / OpenTofu** | huge ecosystem, every cloud, mature state | HCL is limited; loops are awkward |
# | **Pulumi** | real Python/TS — loops, types, tests | smaller community; same provider plugins |
# | **AWS CDK / CDKTF** | concise; great defaults; AWS-first | leaky abstraction; CFN/TF bugs leak through |
# | **Crossplane** | provision from inside k8s; GitOps-native | reconciliation lag; smaller ecosystem |
# …


# %% [markdown] color=lime title="10 · Day-2 + anti-patterns"
# # 10 · Day-2 + anti-patterns
#
# | Topic | What to do |
# |---|---|
# | **Drift detection** | `terraform plan` on schedule (CI) — alerts if console edits diverged |
# | **Module versioning** | pin `version = "~> 5.0"`; bump intentionally |
# | **Atomic blast radius** | many small modules > one mega-stack; dev can't break prod |
# | **Rotation** | rotate the state-bucket KMS key; rotate cloud creds |
# …


# %% [markdown] color=teal title="✅ Recap"
# # ✅ Recap
#
# - Terraform = declare cloud infrastructure in HCL; `plan` shows the diff, `apply` executes.
# - 5 primitives: **provider · resource · data · variable · output**.
# - **State is the central concept** — keep it remote, locked, encrypted.
# - Modules for reuse; directory-per-env for dev/staging/prod.
# - Pair with **Atlantis / Spacelift / Argo CD** for safe PR-driven applies.
# - Terraform provisions infra; **Ansible (M49)** configures the servers/VMs that infra creates.
#
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


