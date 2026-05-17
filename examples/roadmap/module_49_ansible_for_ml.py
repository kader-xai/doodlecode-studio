# doodlecode format-version: 2
# Auto-converted from module_49_ansible_for_ml.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 49 Ansible For Ml"
# # Module 49 Ansible For Ml
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 49 — Ansible for ML Provisioning"
# # Module 49 — Ansible for ML Provisioning
#
# > Terraform (M48) creates the **boxes**. Helm (M47) configures things **inside** Kubernetes. **Ansible** configures the **boxes themselves** — installing CUDA drivers on bare-metal training rigs, hardening SSH, mounting NFS for shared model caches, rolling NVIDIA driver updates across 200 servers without dropping the cluster. It's **agentless** (just SSH), **idempotent** (run it 100 times — same result), and shines exactly where your infrastructure isn't fully containerised.
# >
# > Where you'll meet it in ML: on-prem GPU servers, edge devices, training-cluster bootstrap, Kubernetes nodes that need a custom kernel module, and any "we have 30 Linux boxes" situation.
#
# > 🟡 We won't SSH from this notebook (no remote hosts), but every snippet is production-shaped YAML you can drop into a real `playbooks/` folder.
#
# …


# %% [markdown] color=mint title="1 · Where Ansible fits"
# # 1 · Where Ansible fits
#
# | Tool | Role | Stage |
# |---|---|---|
# | **Terraform / OpenTofu** (M48) | declare infrastructure (VPC, EKS, GPU instance) | "Day 0" — provision |
# | **Ansible** | configure the OS / apps **on** that infrastructure | "Day 1" — bootstrap |
# | **Helm** (M47) | configure things inside Kubernetes | "Day 1+" — deploy |
# | **Argo CD / Flux** | continuously reconcile k8s state from Git | "Day 2+" — operate |
# …


# %% [markdown] color=peach title="2 · Mental model"
# # 2 · Mental model
#
# | Concept | What it is |
# |---|---|
# | **Inventory** | a list of hosts + groups |
# | **Playbook** | a YAML file: "for these hosts, run these tasks" |
# | **Task** | one call to a **module** (idempotent action) |
# | **Module** | a unit like `apt`, `copy`, `systemd`, `nvidia.nvidia_driver` |
# …


# %% [markdown] color=violet title="3 · Inventory"
# # 3 · Inventory
#


# %% color=amber title="inventory = '''[gpu_workers]"
# @explain: Run this cell to see the output.
inventory = '''[gpu_workers]
gpu-01 ansible_host=10.0.0.11
gpu-02 ansible_host=10.0.0.12
gpu-03 ansible_host=10.0.0.13

[control_plane]
cp-01 ansible_host=10.0.0.5

[k8s_cluster:children]
gpu_workers
control_plane

[gpu_workers:vars]
ansible_user=ubuntu
ansible_ssh_private_key_file=~/.ssh/ml_cluster.pem
nvidia_driver_branch=550
'''
print(inventory)


# %% [markdown] color=rose title="INI format** is fine for small inventories;…"
# # INI format** is fine for small inventories;…
#
# **INI format** is fine for small inventories; **YAML** scales better. **Dynamic inventory** plugins query AWS/GCP/Azure at runtime so you don't have to hand-maintain IPs.


# %% [markdown] color=lime title="4 · A first task — install Docker on every GPU worker"
# # 4 · A first task — install Docker on every GPU worker
#


# %% color=teal title="playbook = '''---"
# @explain: Run this cell to see the output.
playbook = '''---
- name: Bootstrap GPU workers
  hosts: gpu_workers
  become: true             # sudo
  gather_facts: true       # collect distro / kernel / cpu info first
  tasks:

    - name: Install base packages
      ansible.builtin.apt:
        name:
          - curl
          - ca-certificates
          - gnupg
        state: present
        update_cache: yes

    - name: Add Docker GPG key
      ansible.builtin.apt_key:
        url: https://download.docker.com/linux/ubuntu/gpg
        state: present

    - name: Add Docker apt repo
      ansible.builtin.apt_repository:
        repo: "deb https://download.docker.com/linux/ubuntu {{ ansible_distribution_release }} stable"
        state: present

    - name: Install Docker engine
      ansible.builtin.apt:
        name: ["docker-ce", "docker-ce-cli", "containerd.io"]
        state: present

    - name: Ensure docker is running
      ansible.builtin.systemd:
        name: docker
        state: started
        enabled: yes
'''
print(playbook[:500], "...")


# %% [markdown] color=sky title="Reading guide"
# # Reading guide
#
# **Reading guide.**
# - `hosts: gpu_workers` — pulled from inventory.
# - `become: true` — escalate to root via sudo.
# - Each `task` calls **one module**. Module name → namespace + name (`ansible.builtin.apt`).
# - The whole playbook is **declarative** — re-running it on already-installed hosts is a no-op (next section).


# %% [markdown] color=mint title="5 · Idempotency — Ansible's killer feature"
# # 5 · Idempotency — Ansible's killer feature
#
# Every well-written Ansible module is **idempotent**: it inspects current state and only acts if it differs from desired state.
#
# ```
# First run on a fresh box:
#   TASK [Install Docker engine] ************
#   changed: [gpu-01]
# …


# %% [markdown] color=peach title="6 · Variables, facts, templates"
# # 6 · Variables, facts, templates
#


# %% color=violet title="host-specific"
# @explain: host-specific:
template = '''# /etc/nvidia-container-runtime/config.toml ({{ ansible_managed }})
[nvidia-container-cli]
no-cgroups = false
load-kmods = true
ldconfig = "@/sbin/ldconfig.real"

[nvidia-container-runtime]
runtimes = {{ runtimes | to_json }}

# host-specific:
hostname = "{{ inventory_hostname }}"
gpu_count = {{ ansible_facts.devices.nvidia | length }}
'''
print(template)


# %% [markdown] color=amber title="- `{{ var }}`"
# # - `{{ var }}`
#
# - `{{ var }}` — Jinja2 substitution.
# - `ansible_facts.*` — facts collected on each host (distro, kernel, CPU, GPUs).
# - Filters: `| to_json`, `| default("x")`, `| length`, `| basename`, …
#
# Variable precedence (high → low): CLI `--extra-vars` > task vars > role vars > host_vars > group_vars > defaults. **Memorise this** — it's the source of half of all Ansible debugging.


# %% [markdown] color=rose title="7 · Roles — the unit of reuse"
# # 7 · Roles — the unit of reuse
#


# %% color=lime title="role_layout = '''roles/cuda/"
# @explain: Run this cell to see the output.
role_layout = '''roles/cuda/
├── defaults/main.yml      # default variable values (lowest precedence)
├── vars/main.yml          # role-level vars (higher precedence)
├── tasks/main.yml         # the entry-point task list
├── handlers/main.yml      # restart-on-change handlers
├── templates/             # jinja2 files
├── files/                 # static files to copy
└── meta/main.yml          # dependencies on other roles, license
'''
print(role_layout)


# %% [markdown] color=teal title="Ansible Galaxy** (`ansible-galaxy install…"
# # Ansible Galaxy** (`ansible-galaxy install…
#
# **Ansible Galaxy** (`ansible-galaxy install nvidia.nvidia_driver`) is the package manager for community roles + collections. For ML there are tested roles for: NVIDIA drivers, NCCL, Docker / containerd, k3s / kubeadm, NFS / Lustre clients, Slurm, JupyterHub, MinIO. Use them; don't reinvent.
#
# **Collections** are the modern packaging unit: a bundle of roles + modules + plugins published to Galaxy, e.g. `community.general`, `kubernetes.core`, `nvidia.nvidia_driver`.


# %% [markdown] color=sky title="8 · Handlers — restart-on-change"
# # 8 · Handlers — restart-on-change
#


# %% color=mint title="handler_pattern = '''---"
# @explain: Run this cell to see the output.
handler_pattern = '''---
- hosts: gpu_workers
  become: true
  tasks:

    - name: Render NVIDIA container runtime config
      ansible.builtin.template:
        src: nvidia-container-runtime.toml.j2
        dest: /etc/nvidia-container-runtime/config.toml
        owner: root
        mode: "0644"
      notify: restart docker         # only fires on change

  handlers:
    - name: restart docker
      ansible.builtin.systemd:
        name: docker
        state: restarted
'''
print(handler_pattern)


# %% [markdown] color=peach title="Handlers run **once at the end of a play**, only if…"
# # Handlers run **once at the end of a play**, only if…
#
# Handlers run **once at the end of a play**, only if **notified** by a changed task. This is how you avoid restart storms — bundle ten config edits, restart the daemon once.


# %% [markdown] color=violet title="9 · An ML-real play: NVIDIA driver + CUDA + nvidia-container-toolkit"
# # 9 · An ML-real play: NVIDIA driver + CUDA + nvidia-container-toolkit
#


# %% color=amber title="ml_play = '''---"
# @explain: Run this cell to see the output.
ml_play = '''---
- name: Provision a GPU worker
  hosts: gpu_workers
  become: true
  vars:
    cuda_version: "12.4"
    nvidia_branch: "550"

  pre_tasks:
    - name: Disable nouveau (open-source nvidia driver)
      ansible.builtin.copy:
        dest: /etc/modprobe.d/blacklist-nouveau.conf
        content: |
          blacklist nouveau
          options nouveau modeset=0
      register: nouveau

    - name: Rebuild initramfs if changed
      ansible.builtin.command: update-initramfs -u
      when: nouveau.changed

  roles:
    - role: docker
    - role: nvidia.nvidia_driver       # community role — handles dkms + reboot
      vars: { nvidia_driver_branch: "{{ nvidia_branch }}" }

  tasks:
    - name: Add NVIDIA container toolkit repo
      ansible.builtin.shell: |
        curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey \
            | gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
        curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list \
            | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' \
            | tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
      args: { creates: /etc/apt/sources.list.d/nvidia-container-toolkit.list }

    - name: Install nvidia-container-toolkit
      ansible.builtin.apt:
        name: nvidia-container-toolkit
        state: present
        update_cache: yes
      notify: restart docker

    - name: Configure docker for nvidia runtime
      ansible.builtin.command: nvidia-ctk runtime configure --runtime=docker
      args: { creates: /etc/docker/daemon.json }
      notify: restart docker

    - name: Sanity check — nvidia-smi inside docker
      ansible.builtin.command: docker run --rm --gpus all nvidia/cuda:12.4.0-base-ubuntu22.04 nvidia-smi
      register: smi
      changed_when: false

    - debug: msg="{{ smi.stdout_lines[:3] }}"

  handlers:
    - name: restart docker
      ansible.builtin.systemd: { name: docker, state: restarted }
'''
print(ml_play[:600], "...")


# %% [markdown] color=rose title="This is the canonical 'make a Linux box ready for…"
# # This is the canonical "make a Linux box ready for…
#
# This is the canonical "make a Linux box ready for GPU workloads" play. Run it across 200 hosts and you have a homogeneous training cluster.


# %% [markdown] color=lime title="10 · Production basics"
# # 10 · Production basics
#
# | Topic | What to do |
# |---|---|
# | **`ansible-vault`** | encrypt secret files: `ansible-vault encrypt group_vars/prod/secrets.yml` |
# | **Dynamic inventory** | `aws_ec2`, `gcp_compute`, `kubernetes.core.k8s` plugins query the cloud at runtime |
# | **AWX / Ansible Tower / Semaphore** | UI + RBAC + scheduled runs + audit log |
# | **CI runs** | run `ansible-lint` + `--check` mode in PRs |
# …


# %% [markdown] color=teal title="✅ Recap"
# # ✅ Recap
#
# - **Terraform creates boxes; Ansible configures them; Helm deploys to clusters.**
# - Inventory + playbook + task + role + handler.
# - **Idempotency** is the killer property — modules check current state before acting.
# - Variables flow through a precedence chain (CLI > task > role > host_vars > group_vars > defaults).
# - **Roles + collections** from Galaxy keep you off the reinvention treadmill.
# - Production = AWX/Semaphore + ansible-vault + dynamic inventory + CI runs.
#
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


