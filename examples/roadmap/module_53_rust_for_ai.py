# doodlecode format-version: 2
# Auto-converted from module_53_rust_for_ai.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 53 Rust For Ai"
# # Module 53 Rust For Ai
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 53 — Rust Crash Course"
# # Module 53 — Rust Crash Course
#
# > Go (M52) is the cloud-native glue. **Rust** is what runs on the **hot path**: HuggingFace **`tokenizers`** is Rust. **`safetensors`** is Rust. **Polars** (the dataframe library that's eating Pandas) is Rust. **Qdrant** (M42) is Rust. **`candle`** (HF's pure-Rust ML framework), **`burn`**, **`mistral.rs`**, **`uv`** (the Astral pip replacement), **`ruff`**, **`tiktoken`**'s fast paths — all Rust. The pattern is consistent: when an ML tool needs to be *fast and safe*, the answer in 2026 is Rust.
# >
# > This module is a Rust crash course aimed at AI tooling. **No "learn Rust in 21 days"** — the 20% that lets you read those crates, contribute small fixes, and write a Rust extension for your Python code via **PyO3**.
#
# > 🟡 We'll install Rust (`rustup`) in Colab and run real programs.
#
# …


# %% [markdown] color=mint title="1 · Why Rust in ML 2026"
# # 1 · Why Rust in ML 2026
#
# | Property | Why ML tooling cares |
# |---|---|
# | **No GC, no runtime** | predictable latency in inference / hot loops |
# | **Memory safety** without a garbage collector | C++ speed, no segfaults / use-after-free |
# | **`unsafe` is opt-in** and audited | safe by default, escape hatch where needed |
# | **First-class FFI** | drop-in replacement for C extensions (PyO3, cxx) |
# …


# %% [markdown] color=peach title="2 · Setup"
# # 2 · Setup
#


# %% color=violet title="install rustup → toolchain"
# @explain: install rustup → toolchain
# install rustup → toolchain
!curl -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain stable --profile minimal > /dev/null 2>&1
import os
os.environ["PATH"] = "/root/.cargo/bin:" + os.environ["PATH"]
!rustc --version && cargo --version


# %% color=amber title="!cd /content && cargo new hello --quiet && cat…"
# @explain: Run this cell to see the output.
!cd /content && cargo new hello --quiet && cat /content/hello/src/main.rs


# %% color=rose title="!cd /content/hello && cargo run --quiet"
# @explain: Run this cell to see the output.
!cd /content/hello && cargo run --quiet


# %% [markdown] color=lime title="3 · Ownership + borrowing"
# # 3 · Ownership + borrowing
#
# This is the entire reason Rust is hard *and* the entire reason it's safe. Three rules:
#
# 1. **Every value has exactly one owner.**
# 2. **When the owner goes out of scope, the value is freed.** (No GC needed.)
# 3. You can hand out **borrows** — references — as long as they obey the **borrow checker**:
#    - any number of `&T` (shared, read-only) **OR**
# …


# %% color=teal title="ownership = '''fn main() {"
# @explain: Run this cell to see the output.
ownership = '''fn main() {
    let s = String::from("hello");          // s OWNS the heap-allocated bytes
    let len = take_len(&s);                 // borrow read-only — s still alive after
    println!("{:?} -> len {}", s, len);

    let mut v = vec![1, 2, 3];
    push_one(&mut v);                       // borrow mutably (exclusive)
    println!("v = {:?}", v);
}

fn take_len(s: &String) -> usize {          // &String == read-only borrow
    s.len()
}

fn push_one(v: &mut Vec<i32>) {             // &mut == mutable borrow
    v.push(99);
}
'''
import os
os.makedirs("/content/own/src", exist_ok=True)
open("/content/own/Cargo.toml","w").write(
    '[package]\nname = "own"\nversion = "0.1.0"\nedition = "2021"\n\n[dependencies]\n')
open("/content/own/src/main.rs","w").write(ownership)
!cd /content/own && cargo run --quiet 2>&1 | head -10


# %% [markdown] color=sky title="4 · Syntax fast-tour"
# # 4 · Syntax fast-tour
#


# %% color=mint title="[derive(Debug)]"
# @explain: [derive(Debug)]
tour = '''use std::collections::HashMap;

// STRUCT — like a Go struct or Python dataclass
#[derive(Debug)]
struct Model {
    name: String,
    params: u64,
    active: bool,
}

// METHODS — `impl` block
impl Model {
    fn tag(&self) -> String {
        format!("{}-{}", self.name.to_lowercase(), self.params)
    }
}

// ENUM — sum types (algebraic). Result and Option are stdlib enums.
enum Backend { OpenAI, Anthropic, VLLM }

// Result<T, E> for error handling — no exceptions
fn divide(a: i32, b: i32) -> Result<i32, String> {
    if b == 0 { Err("divide by zero".into()) } else { Ok(a / b) }
}

fn main() {
    let m = Model { name: "Qwen".into(), params: 500_000_000, active: true };
    println!("tag = {}", m.tag());

    let mut cfg: HashMap<&str, i32> = HashMap::new();
    cfg.insert("max_tokens", 256);
    cfg.insert("top_k", 50);
    for (k, v) in &cfg { println!("{} = {}", k, v); }

    // The ? operator unwraps Ok or returns the error early
    match divide(10, 0) {
        Ok(q)  => println!("q = {}", q),
        Err(e) => println!("oops: {}", e),
    }

    let b = Backend::VLLM;
    match b {
        Backend::OpenAI    => println!("calling openai"),
        Backend::Anthropic => println!("calling anthropic"),
        Backend::VLLM      => println!("calling vllm locally"),
    }
}
'''
os.makedirs("/content/tour/src", exist_ok=True)
open("/content/tour/Cargo.toml","w").write(
    '[package]\nname = "tour"\nversion = "0.1.0"\nedition = "2021"\n\n[dependencies]\n')
open("/content/tour/src/main.rs","w").write(tour)
!cd /content/tour && cargo run --quiet 2>&1 | tail -12


# %% [markdown] color=peach title="Highlights"
# # Highlights
#
# **Highlights.**
# - `Result<T, E>` and `Option<T>` are how Rust handles "this might fail" / "this might be missing." No exceptions, no `null`.
# - The `?` operator unwraps `Ok` and **returns the error early** — the equivalent of Go's `if err != nil { return err }` in one character.
# - `match` is **exhaustive** — the compiler errors if you don't cover every variant.
# - `derive(Debug)` auto-generates a printable representation.


# %% [markdown] color=violet title="5 · Iterators + closures — Rust's 'Pythonic' side"
# # 5 · Iterators + closures — Rust's "Pythonic" side
#


# %% color=amber title="iters = '''fn main() {"
# @explain: Run this cell to see the output.
iters = '''fn main() {
    let xs = vec![1,2,3,4,5,6,7,8];

    // map + filter + sum, all lazy, all on the stack
    let s: i32 = xs.iter()
                   .map(|x| x * x)
                   .filter(|x| x % 2 == 0)
                   .sum();
    println!("sum of even squares = {}", s);

    // collect into a Vec
    let doubled: Vec<i32> = xs.iter().map(|x| x * 2).collect();
    println!("{:?}", doubled);

    // for ... in works on anything that implements IntoIterator
    for (i, v) in xs.iter().enumerate() {
        if v % 3 == 0 { println!("idx {} -> {}", i, v); }
    }
}
'''
os.makedirs("/content/iters/src", exist_ok=True)
open("/content/iters/Cargo.toml","w").write(
    '[package]\nname = "iters"\nversion = "0.1.0"\nedition = "2021"\n\n[dependencies]\n')
open("/content/iters/src/main.rs","w").write(iters)
!cd /content/iters && cargo run --quiet 2>&1 | tail -8


# %% [markdown] color=rose title="Iterator chains compile to the same machine code as…"
# # Iterator chains compile to the same machine code as…
#
# Iterator chains compile to the same machine code as a hand-written `for` loop. **Zero-cost abstractions.** Combine with **`rayon`** (`use rayon::prelude::*; xs.par_iter().map(...)...`) and you have data-parallelism for free across all cores.


# %% [markdown] color=lime title="6 · Cargo — the package manager Python wishes it had"
# # 6 · Cargo — the package manager Python wishes it had
#
# ```toml
# # Cargo.toml
# [package]
# name = "llm-gateway"
# version = "0.1.0"
# edition = "2021"
# …


# %% [markdown] color=teal title="7 · `tokio` + `axum` — async HTTP server"
# # 7 · `tokio` + `axum` — async HTTP server
#
# ```rust
# // src/main.rs
# use axum::{routing::post, Json, Router};
# use serde::{Deserialize, Serialize};
# use std::net::SocketAddr;
#
# …


# %% [markdown] color=sky title="8 · PyO3 — call Rust from Python"
# # 8 · PyO3 — call Rust from Python
#
# The most common way to use Rust in an ML stack: write the hot loop in Rust, expose it as a Python module via **PyO3**.
#
# ```toml
# # Cargo.toml
# [lib]
# name = "fastnorm"
# …


# %% [markdown] color=mint title="9 · The ML-Rust ecosystem"
# # 9 · The ML-Rust ecosystem
#
# | Crate | What it is |
# |---|---|
# | **`tokenizers`** (HF) | byte-pair encoding / WordPiece / SentencePiece — what every LLM uses |
# | **`safetensors`** | safe alternative to PyTorch `.bin` (no pickle = no RCE) |
# | **`candle`** (HF) | pure-Rust ML framework — load Llama/Mistral/Whisper without Python |
# | **`burn`** | another pure-Rust framework, dynamic graphs, multi-backend |
# …


# %% [markdown] color=peach title="10 · Rust vs Go vs C++"
# # 10 · Rust vs Go vs C++
#
# | Use case | Pick |
# |---|---|
# | K8s controller, HTTP gateway, sidecar | **Go** (M52) |
# | Hot path inside a service: tokenisation, vector math, parsing | **Rust** |
# | You need to embed in or interop with **legacy C++** | **C++** (or Rust + cxx crate) |
# | GPU kernels | **CUDA C++** or **Triton**; Rust binding via `cudarc` |
# …


# %% [markdown] color=violet title="✅ Recap"
# # ✅ Recap
#
# - Rust = C++ speed + memory safety + a brilliant package manager.
# - The **ownership + borrowing** discipline is the price of admission. Internalise the **shared XOR mutable** rule.
# - `Result<T, E>` + `?` replace exceptions; `match` is exhaustive.
# - **`tokio` + `axum`** for backends; **PyO3 + maturin** to ship a Rust crate as a Python wheel.
# - The ML-Rust ecosystem is real: `tokenizers`, `safetensors`, `polars`, `candle`, `burn`, `qdrant`.
# - Pick Rust where you'd otherwise reach for **C++ or a Python C-extension**. Stay in Go (M52) for the rest.
#
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


