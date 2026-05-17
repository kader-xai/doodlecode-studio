# doodlecode format-version: 2
# Auto-converted from module_82_linux_bash_for_ml_engineers.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 82 Linux Bash For Ml Engineers"
# # Module 82 Linux Bash For Ml Engineers
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 82 — Linux + Bash for ML Engineers"
# # Module 82 — Linux + Bash for ML Engineers
#
# > Every ML/AI engineer eventually SSHes into a GPU box at 2 AM because a vLLM pod won't start, training stalled at step 12 of 50 000, or `nvidia-smi` shows three GPUs missing. **The course assumed you knew Linux.** This module is the **practical map of the OS** an ML engineer touches — `/proc`, `nvidia-smi` workflows, `journalctl`, `cgroups`, `tmux`, `rsync`, `perf`, `eBPF` — without the system-administration bloat.
# >
# > Every command here is one you'd type in a real incident or training-prep flow.
#
# ### What you'll cover
# 1. The filesystem map an ML engineer needs (where things actually live)
# …


# %% [markdown] color=mint title="1 · The filesystem map for ML engineers"
# # 1 · The filesystem map for ML engineers
#
# ```
#    /
#    ├── etc/                 # config files
#    │   ├── systemd/          system service definitions
#    │   └── nvidia/           NVIDIA driver config
#    ├── usr/
# …


# %% [markdown] color=peach title="2 · Process management — the everyday tools"
# # 2 · Process management — the everyday tools
#
# | Command | What |
# |---|---|
# | `ps aux` | every process, full args, RSS, %CPU |
# | `ps -eo pid,ppid,pcpu,pmem,etime,cmd --sort=-pcpu \| head` | top CPU consumers, sortable |
# | `top -c` / `htop` | live view; `htop` is the friendlier UI |
# | `pidstat -u -p <pid> 1` | per-PID CPU at 1s intervals |
# …


# %% color=violet title="Example shell commands you'd type during a real…"
# @explain: Example shell commands you'd type during a real incident
# @explain: What's eating the CPU?
# @explain: Which python process owns port 8000?
# @explain: Why is this process stuck? (won't return CPU but won't exit)
# @explain: Memory + open-file pressure
# Example shell commands you'd type during a real incident
incident_shell = '''
# What's eating the CPU?
ps -eo pid,ppid,user,pcpu,pmem,etime,cmd --sort=-pcpu | head -20

# Which python process owns port 8000?
sudo lsof -nP -iTCP:8000 -sTCP:LISTEN

# Why is this process stuck? (won't return CPU but won't exit)
sudo strace -p 12345 -f -tt -T -s 256 -o /tmp/trace.txt &
sleep 5 ; kill %1
tail /tmp/trace.txt        # look for repeating syscall

# Memory + open-file pressure
sudo cat /proc/12345/status | grep -E "(VmRSS|VmPeak|Threads|FDSize)"
sudo ls -l /proc/12345/fd | wc -l        # currently open FDs

# Why is the box itself slow?
uptime ; free -h ; vmstat 1 5
'''
print(incident_shell)


# %% [markdown] color=amber title="3 · `nvidia-smi` workflows that matter"
# # 3 · `nvidia-smi` workflows that matter
#


# %% color=rose title="1"
# @explain: 1
# @explain: 2
# @explain: 3
# @explain: 4
# @explain: 5
nvidia_smi_recipes = '''
# 1. Watch GPUs live (every 1 sec)
nvidia-smi -l 1

# 2. Per-process GPU usage — who owns what memory
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv

# 3. Topology matrix — which GPUs see each other over NVLink (M77)
nvidia-smi topo -m

# 4. Persistence mode — needed before fabric-manager / NCCL is happy
sudo nvidia-smi -pm 1

# 5. Power & clock limits (e.g. cap to 350W during a benchmark sweep)
sudo nvidia-smi -i 0 -pl 350
sudo nvidia-smi -i 0 -lgc 1500,1700           # lock graphics clock to a range

# 6. ECC errors (silent killer — check daily)
nvidia-smi --query-gpu=ecc.errors.uncorrected.aggregate.total --format=csv

# 7. Xid messages — diagnostics in dmesg
sudo dmesg -T | grep -i "NVRM: Xid"

# 8. Useful aliases (put in ~/.bashrc)
alias gpu='nvidia-smi -l 1'
alias gpus='nvidia-smi --query-gpu=index,name,utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw --format=csv,noheader'
'''
print(nvidia_smi_recipes)


# %% [markdown] color=lime title="The four `nvidia-smi` outputs every on-call…"
# # The four `nvidia-smi` outputs every on-call…
#
# **The four `nvidia-smi` outputs every on-call engineer should be able to read in three seconds:**
# 1. **GPU utilization %** — if it's stuck at ~0% during training, your model is CPU-bound or the data pipeline is the bottleneck.
# 2. **Memory used/total** — if you're at 95 % during training and OOM'ing, it's time to reduce batch size or enable gradient checkpointing.
# 3. **Power draw vs. limit** — if it's well below TDP, you're not actually compute-bound.
# 4. **`Xid` messages in `dmesg`** — these are the canonical hardware error codes. **Xid 79 = "GPU has fallen off the bus"** (M78).


# %% [markdown] color=teal title="4 · systemd — every long-running service"
# # 4 · systemd — every long-running service
#


# %% color=sky title="/etc/systemd/system/vllm-server.service"
# @explain: /etc/systemd/system/vllm-server.service
# @explain: Hardening
systemd_unit = '''
# /etc/systemd/system/vllm-server.service
[Unit]
Description=vLLM inference server
Wants=network-online.target nvidia-persistenced.service
After=network-online.target nvidia-persistenced.service

[Service]
Type=simple
User=mlops
Group=mlops
WorkingDirectory=/opt/vllm
ExecStart=/usr/bin/python -m vllm.entrypoints.openai.api_server --model meta-llama/Llama-3.3-70B-Instruct --tensor-parallel-size 8
Restart=always
RestartSec=10
TimeoutStartSec=600        # big models take time to load
KillSignal=SIGTERM
TimeoutStopSec=60
LimitNOFILE=1048576        # open-file limit
LimitMEMLOCK=infinity       # required for CUDA + RDMA
Environment="CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7"
Environment="HF_HOME=/data/hf-cache"

# Hardening
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
'''
print(systemd_unit)


# %% [markdown] color=mint title="Commands you'll type 100 times"
# # Commands you'll type 100 times
#
# Commands you'll type 100 times:
#
# ```bash
# sudo systemctl daemon-reload
# sudo systemctl enable --now vllm-server.service
# sudo systemctl status vllm-server.service
# sudo systemctl restart vllm-server.service
# journalctl -u vllm-server.service -f --since "10 min ago"   # live log
# …


# %% [markdown] color=peach title="5 · `/proc` + `/sys` — the kernel's API"
# # 5 · `/proc` + `/sys` — the kernel's API
#


# %% color=violet title="Memory facts"
# @explain: Memory facts (used by top, free, etc.)
# @explain: CPU topology
# @explain: Per-process info — same shape across every PID
# @explain: CPU governor & turbo
# @explain: NUMA topology (matters for GPU-NIC alignment — M77)
proc_sys_recipes = '''
# Memory facts (used by top, free, etc.)
cat /proc/meminfo | head -5

# CPU topology
lscpu                                       # nicer view
cat /proc/cpuinfo | grep -m1 "model name"

# Per-process info — same shape across every PID
cat /proc/<pid>/status                      # VmRSS, threads, cgroups
cat /proc/<pid>/cmdline | tr '\0' ' '       # the full launch command
ls -l /proc/<pid>/fd | head                 # which FDs are open
cat /proc/<pid>/limits                      # ulimits actually in effect

# CPU governor & turbo
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# NUMA topology (matters for GPU-NIC alignment — M77)
numactl --hardware
cat /sys/devices/system/node/online

# PCIe topology (GPUs + NICs)
lspci | grep -i -E "(nvidia|mellanox|broadcom)"
lspci -vvv -s <bus_id> | grep LnkSta        # actual link speed/width

# Network interfaces & speed
ip -br addr
ethtool eth0 | grep -i speed
'''
print(proc_sys_recipes)


# %% [markdown] color=amber title="Why this matters.** `nvidia-smi` shows GPU state;…"
# # Why this matters.** `nvidia-smi` shows GPU state;…
#
# **Why this matters.** `nvidia-smi` shows GPU state; `/proc` and `/sys` show the **rest of the box**. When a training job is slow despite hot GPUs, the answer is in CPU governor (`powersave`), NUMA misalignment, or a flapping PCIe link — none of which `nvidia-smi` can tell you.


# %% [markdown] color=rose title="6 · cgroups + namespaces — the Docker primitives"
# # 6 · cgroups + namespaces — the Docker primitives
#
# Every container is just a process inside a **cgroup** (resource limits) and a **set of namespaces** (isolation). Knowing this debugs every Docker / k8s issue.
#
# ```
#    container (e.g. a Docker / k8s pod) == process(es)
#                                             +
#                                          cgroups          # what it can USE
# …


# %% color=lime title="Inspect cgroups for a container's PID"
# @explain: Inspect cgroups for a container's PID
# @explain: Apply a memory limit live (cgroups v2)
# @explain: Enter a container's namespaces (debug without exec'ing into the container)
# @explain: Check what a container actually sees
# @explain: Map a host PID to a container
cgroup_recipes = '''
# Inspect cgroups for a container's PID
PID=$(docker inspect -f "{{.State.Pid}}" my-vllm)
cat /proc/$PID/cgroup                     # what cgroups it belongs to

# Apply a memory limit live (cgroups v2)
sudo systemctl set-property --runtime my.slice MemoryMax=8G

# Enter a container's namespaces (debug without exec'ing into the container)
sudo nsenter -t $PID -a                  # full set
sudo nsenter -t $PID -n -- ss -tlnp     # listening sockets inside the container

# Check what a container actually sees
docker exec -it my-vllm sh -c "cat /proc/self/cgroup; ls /dev/nvidia*"

# Map a host PID to a container
docker ps -q | xargs -I {} docker inspect -f "{{.Name}} {{.State.Pid}}" {}
'''
print(cgroup_recipes)


# %% [markdown] color=teal title="> 🚨 **The famous `/dev/shm` trap.** PyTorch…"
# # > 🚨 **The famous `/dev/shm` trap.** PyTorch…
#
# > 🚨 **The famous `/dev/shm` trap.** PyTorch DataLoaders use shared memory for worker IPC. Docker defaults to **64 MB** of `/dev/shm`. Result: random `dataloader killed worker (pid X)` errors. Fix: `docker run --shm-size=8g ...` or `--ipc=host`. In k8s: `volumes: [{name: dshm, emptyDir: {medium: Memory, sizeLimit: 8Gi}}]`.


# %% [markdown] color=sky title="7 · Logs — `journalctl`, `dmesg`, structured logging"
# # 7 · Logs — `journalctl`, `dmesg`, structured logging
#


# %% color=mint title="System / service logs"
# @explain: System / service logs — the only command you really need
# @explain: Kernel ring buffer — Xid, OOM, link-down events
# @explain: OOM-killer events (training OOM, vLLM pods OOM, …)
# @explain: Logrotate config
# @explain: Quick check: who's logging the most?
logs_recipes = '''
# System / service logs — the only command you really need
journalctl -u my-service.service -f                       # tail live
journalctl -u my-service.service --since "1 hour ago"     # recent
journalctl -u my-service.service -p err --since today     # errors only
journalctl -k --since boot                                # kernel ring buffer
journalctl --disk-usage                                   # how big are journals?

# Kernel ring buffer — Xid, OOM, link-down events
sudo dmesg -T | tail -100
sudo dmesg -wH                                            # follow with human time

# OOM-killer events (training OOM, vLLM pods OOM, …)
sudo dmesg -T | grep -i "killed process"

# Logrotate config
ls /etc/logrotate.d/

# Quick check: who's logging the most?
sudo journalctl --disk-usage
sudo du -sh /var/log/* | sort -h | tail
'''
print(logs_recipes)


# %% [markdown] color=peach title="Application log discipline ML engineers should adopt"
# # Application log discipline ML engineers should adopt
#
# **Application log discipline ML engineers should adopt:**
# 1. Log JSON to stdout (not files); let `journald` / Docker / k8s do the rest.
# 2. Include `trace_id`, `tenant_id`, `model_id`, `request_id` on every line — pair with OTel (M51).
# 3. Use **structured logging** (`structlog`, `loguru`) so `jq` can slice the file.
# 4. Different log streams per pod — never log to shared NFS (write amplification kills throughput).


# %% [markdown] color=violet title="8 · Networking — the tools you'll need in 2 AM order"
# # 8 · Networking — the tools you'll need in 2 AM order
#
# ```bash
# # Who is listening on which port?
# ss -tlnp                                # all TCP listeners + owning PID
# ss -tunap state established | head      # active connections
#
# # DNS / connectivity
# …


# %% [markdown] color=amber title="9 · Disk + memory"
# # 9 · Disk + memory
#


# %% color=rose title="Disk usage / space remaining"
# @explain: Disk usage / space remaining
# @explain: Disk IO live
# @explain: Synthetic disk benchmark (M78 storage validation)
# @explain: Memory + swap
# @explain: Per-process memory breakdown
disk_mem_recipes = '''
# Disk usage / space remaining
df -hT                                  # mounted filesystems
du -sh /var/log/* | sort -h | tail      # what's eating the disk
df -i                                   # inodes (small-file storms exhaust these)

# Disk IO live
iostat -x 1                              # extended; %util, await, w/s, r/s
iotop -oP                                # which process is hitting disk hardest
sudo dstat -tdngy 1                      # mixed system view

# Synthetic disk benchmark (M78 storage validation)
sudo fio --name=randwrite --filename=/scratch/fio.test --rw=randwrite \
         --bs=4k --size=4G --iodepth=64 --numjobs=4 \
         --time_based --runtime=30 --group_reporting

# Memory + swap
free -h
vmstat 1 10                              # paging, context switches, runqueue
smem -tk                                 # PSS — proportional set size (multi-process picture)

# Per-process memory breakdown
sudo pmap -x <pid> | tail
cat /proc/<pid>/status | grep -E "(VmRSS|VmHWM|VmSwap|RssAnon|RssFile|VmData)"
'''
print(disk_mem_recipes)


# %% [markdown] color=lime title="Two ML-specific memory traps"
# # Two ML-specific memory traps
#
# **Two ML-specific memory traps:**
# - **`HF_HOME`** silently downloads multi-hundred-GB checkpoints to whatever drive you set it to. Move it to a fast big disk.
# - **Python multiprocessing** (DataLoaders) shows **N× the RSS** of the model. Each worker forks; without `--ipc=host` you'll fill `/dev/shm`.


# %% [markdown] color=teal title="10 · Bash for ML ops — the patterns that survive contact with prod"
# # 10 · Bash for ML ops — the patterns that survive contact with prod
#


# %% color=sky title="train-a-model.sh"
# @explain: train-a-model.sh — the production-grade shape
# @explain: Strict mode — fail fast on errors / undefined vars / pipe failures
# @explain: Trap errors with a helpful message
# @explain: Always-run cleanup (works even on Ctrl+C)
# @explain: Defaults via parameter expansion
bash_patterns = r'''
#!/usr/bin/env bash
# train-a-model.sh — the production-grade shape

# Strict mode — fail fast on errors / undefined vars / pipe failures
set -Eeuo pipefail

# Trap errors with a helpful message
trap 'rc=$?; echo "FAILED line $LINENO: $BASH_COMMAND  (rc=$rc)" >&2; exit $rc' ERR

# Always-run cleanup (works even on Ctrl+C)
cleanup() {
    rc=$?
    rm -rf "${TMPDIR:-/tmp}/build.$$"
    [[ $rc -ne 0 ]] && echo "cleaning up after failure ($rc)" >&2
}
trap cleanup EXIT

# Defaults via parameter expansion
MODEL="${MODEL:-meta-llama/Llama-3.3-70B-Instruct}"
EPOCHS="${EPOCHS:-3}"
SAVE_DIR="${SAVE_DIR:-/scratch/runs/$(date +%F)}"
DRY_RUN="${DRY_RUN:-0}"

# Logging helpers
log()  { printf "[%s] %s
" "$(date +%T)" "$*"; }
die()  { log "ERROR: $*" >&2; exit 1; }

# Pre-flight checks
command -v python >/dev/null || die "python not in PATH"
[[ -d /opt/cuda ]] || die "/opt/cuda missing"
nvidia-smi -L | grep -q UUID || die "no GPUs visible"

mkdir -p "$SAVE_DIR" || die "cannot create $SAVE_DIR"

log "training $MODEL for $EPOCHS epochs into $SAVE_DIR"

# Loop with safe IFS handling (newlines + tabs only)
for shard in $(ls /data/shards/*.parquet); do
    [[ "$DRY_RUN" == "1" ]] && { log "DRY: $shard"; continue; }
    python train.py --shard "$shard" --epochs "$EPOCHS" --out "$SAVE_DIR"         2>&1 | tee -a "$SAVE_DIR/train.log"
done

log "done."
'''
print(bash_patterns)


# %% [markdown] color=mint title="The seven habits of effective bash scripts"
# # The seven habits of effective bash scripts
#
# **The seven habits of effective bash scripts:**
#
# 1. **`set -Eeuo pipefail`** — fail fast, fail loud.
# 2. **`trap ERR` with line-number** — pinpoints the failure.
# 3. **`trap EXIT` for cleanup** — always-run, even on `Ctrl+C`.
# 4. **`"${VAR:-default}"`** — defaults with parameter expansion.
# 5. **Wrap commands in helpers** (`log`, `die`) — DRY + structured stderr.
# 6. **Pre-flight every dependency** — `command -v`, mount points, GPU presence.
# …


# %% [markdown] color=peach title="11 · `perf` + eBPF — the production performance toolkit"
# # 11 · `perf` + eBPF — the production performance toolkit
#


# %% color=violet title="Where is CPU time going for a running PID?"
# @explain: Where is CPU time going for a running PID?
# @explain: Generate a flamegraph (Brendan Gregg's tool)
# @explain: eBPF / bpftrace — far gentler perf hits, much richer signals
# @explain: bcc-tools — pre-baked one-liners; install once
# @explain: NVIDIA Nsight Systems for GPU profiles (ties to M41)
perf_ebpf = '''
# Where is CPU time going for a running PID?
sudo perf top -p <pid>                                 # live "hot functions"
sudo perf record -F 99 -p <pid> -g -- sleep 30          # 30s sample
sudo perf report --stdio                                # browse

# Generate a flamegraph (Brendan Gregg's tool)
git clone https://github.com/brendangregg/FlameGraph
sudo perf record -F 99 -p <pid> -g -- sleep 30
sudo perf script | FlameGraph/stackcollapse-perf.pl | FlameGraph/flamegraph.pl > flame.svg

# eBPF / bpftrace — far gentler perf hits, much richer signals
sudo bpftrace -e "tracepoint:syscalls:sys_enter_openat { @[comm] = count(); }"
sudo bpftrace -e "kprobe:do_unlinkat { printf(\"%s deletes %s\\n\", comm, str(arg1)); }"

# bcc-tools — pre-baked one-liners; install once
sudo apt install bpfcc-tools
sudo execsnoop-bpfcc                # every exec() in the system
sudo opensnoop-bpfcc                # every open() — see who is hitting the FS
sudo runqlat-bpfcc 10 1              # scheduler run-queue latency
sudo profile-bpfcc -p <pid> 30      # cheaper alternative to perf record

# NVIDIA Nsight Systems for GPU profiles (ties to M41)
sudo nsys profile -t cuda,nvtx -o profile.qdrep python train.py
'''
print(perf_ebpf)


# %% [markdown] color=amber title="Mental model for production performance work"
# # Mental model for production performance work
#
# **Mental model for production performance work:**
# - **`perf top`** — first 30 seconds; where's CPU going?
# - **Flamegraphs** — what's the call tree underneath those hot functions?
# - **bcc / bpftrace** — kernel-side; who's syscalling, who's waiting, who's blocking?
# - **Nsight Systems** — GPU side; CUDA kernels + memory transfers (M41).
#
# That four-tool ladder solves 95 % of "why is this slow" tickets.


# %% [markdown] color=rose title="✅ Recap"
# # ✅ Recap
#
# - The filesystem map: `/proc` for process info, `/sys` for hardware, `/dev/nvidia*` for GPU access, `/var/log` is what fills up first.
# - **`nvidia-smi -l 1`**, `topo -m`, the `Xid` grep, and `query-compute-apps` are the four GPU recipes.
# - **`systemd` units** with `Restart=always`, `LimitMEMLOCK=infinity`, and `TimeoutStartSec=600` are how every production model service runs.
# - **cgroups + namespaces** = containers. Know **`/dev/shm`** for PyTorch DataLoaders.
# - `journalctl -u <svc> -f` + `dmesg` get you 90 % of the way into any incident.
# - `ss`, `mtr`, `iperf3`, `tcpdump` are the networking 2-AM kit.
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


