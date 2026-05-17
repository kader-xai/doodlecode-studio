# doodlecode format-version: 2
# Auto-converted from module_52_go_for_ai_backends.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 52 Go For Ai Backends"
# # Module 52 Go For Ai Backends
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 52 — Go for AI Backends"
# # Module 52 — Go for AI Backends
#
# > The whole platform you've built in M44–M51 is written in Go. **Kubernetes, Docker, containerd, Prometheus, Grafana, the OTel Collector, Argo CD, Helm, Terraform, vLLM's gateway services, Ollama, Cloudflare Workers AI, Anthropic's tool servers** — all Go. Python is for the model + research; **Go is the glue layer**: gateways, sidecars, controllers, exporters, CLIs.
# >
# > This module is a Go crash course aimed at AI backends. Not "learn Go in 10 hours" — the **20%** that lets you read the source of the tools you use and ship a working LLM gateway.
#
# > 🟡 We'll install Go in Colab and run real programs. No Python here.
#
# …


# %% [markdown] color=mint title="1 · Why Go in cloud-native AI"
# # 1 · Why Go in cloud-native AI
#
# | Trait | Why it matters for ML infra |
# |---|---|
# | **Static binary, no runtime** | one `.bin` per service → tiny Docker image, fast cold start |
# | **Goroutines** | thousands of concurrent connections per process for ~free |
# | **Standard library** | HTTP server, JSON, gRPC, TLS, profiling — all in stdlib |
# | **gofmt + simple syntax** | every codebase looks the same; PRs are quick to review |
# …


# %% [markdown] color=peach title="2 · Setup — Go inside Colab"
# # 2 · Setup — Go inside Colab
#


# %% color=violet title="!apt-get -y -qq install golang-1.22 > /dev/null"
# @explain: Run this cell to see the output.
!apt-get -y -qq install golang-1.22 > /dev/null
import os
os.environ["PATH"] = "/usr/lib/go-1.22/bin:" + os.environ["PATH"]
!go version


# %% color=amber title="hello = '''package main"
# @explain: Run this cell to see the output.
hello = '''package main

import "fmt"

func main() {
    fmt.Println("hello from Go")
}
'''
import os
os.makedirs("/content/hello", exist_ok=True)
open("/content/hello/main.go","w").write(hello)
!cd /content/hello && go run main.go


# %% [markdown] color=rose title="3 · Syntax fast-tour"
# # 3 · Syntax fast-tour
#


# %% color=lime title="tour = '''package main"
# @explain: Run this cell to see the output.
tour = '''package main

import (
    "fmt"
    "errors"
    "strings"
)

// 1) STRUCTS — like a dataclass
type Model struct {
    Name    string
    Params  int64
    Active  bool
}

// 2) METHODS — receivers attach functions to types
func (m *Model) Tag() string {
    return strings.ToLower(m.Name) + "-" + fmt.Sprint(m.Params)
}

// 3) ERROR HANDLING — errors are VALUES, not exceptions
func divide(a, b int) (int, error) {
    if b == 0 {
        return 0, errors.New("divide by zero")
    }
    return a / b, nil
}

func main() {
    m := Model{Name: "Qwen", Params: 500_000_000, Active: true}
    fmt.Println(m.Tag())                    // qwen-500000000

    // 4) SLICES — dynamic arrays
    nums := []int{1, 2, 3}
    nums = append(nums, 4)
    fmt.Println(nums, "len:", len(nums))    // [1 2 3 4] len: 4

    // 5) MAPS — like a dict
    cfg := map[string]int{"max_tokens": 256, "top_k": 50}
    cfg["temp"] = 1                         // (we lied — int only, but you get it)
    for k, v := range cfg { fmt.Println(k, "=", v) }

    // 6) ERROR PATTERN
    if q, err := divide(10, 0); err != nil {
        fmt.Println("oops:", err)
    } else {
        fmt.Println("q:", q)
    }
}
'''
os.makedirs("/content/tour", exist_ok=True)
open("/content/tour/main.go","w").write(tour)
!cd /content/tour && go run main.go


# %% [markdown] color=teal title="4 · Goroutines + channels — Go's superpower"
# # 4 · Goroutines + channels — Go's superpower
#


# %% color=sky title="concurrent = '''package main"
# @explain: Run this cell to see the output.
concurrent = '''package main

import (
    "fmt"
    "sync"
    "time"
)

// pretend RPC to an embedding service
func embed(id int, ch chan<- string) {
    time.Sleep(time.Duration(50+id*10) * time.Millisecond)
    ch <- fmt.Sprintf("doc-%d-embedded", id)
}

func main() {
    n := 10
    ch := make(chan string, n)              // BUFFERED channel
    var wg sync.WaitGroup
    for i := 1; i <= n; i++ {
        wg.Add(1)
        go func(id int) {                   // GOROUTINE — `go` keyword
            defer wg.Done()
            embed(id, ch)
        }(i)
    }
    wg.Wait()
    close(ch)
    for v := range ch { fmt.Println(v) }
}
'''
os.makedirs("/content/concurrent", exist_ok=True)
open("/content/concurrent/main.go","w").write(concurrent)
!cd /content/concurrent && go run main.go


# %% [markdown] color=mint title="The two primitives"
# # The two primitives
#
# **The two primitives.**
# - `go fn()` spawns a **goroutine** — a green thread that costs ~2 KB of stack. You can run a million of them.
# - `chan T` is a typed pipe. **`<-`** sends/receives. **`close`** signals "done". Buffered channels = bounded queue; unbounded sends → blocking until a receiver shows up.
#
# **The mantra.** *"Don't communicate by sharing memory; share memory by communicating."* — i.e. pass values over channels instead of locking shared state.


# %% [markdown] color=peach title="5 · `net/http` — the world's simplest HTTP server"
# # 5 · `net/http` — the world's simplest HTTP server
#


# %% color=violet title="server = '''package main"
# @explain: Run this cell to see the output.
server = '''package main

import (
    "encoding/json"
    "log"
    "net/http"
)

type EchoIn  struct{ Text string `json:"text"` }
type EchoOut struct{ Said string `json:"said"` }

func main() {
    mux := http.NewServeMux()

    mux.HandleFunc("GET /healthz", func(w http.ResponseWriter, r *http.Request) {
        w.Write([]byte("ok"))
    })

    mux.HandleFunc("POST /echo", func(w http.ResponseWriter, r *http.Request) {
        var in EchoIn
        if err := json.NewDecoder(r.Body).Decode(&in); err != nil {
            http.Error(w, err.Error(), 400); return
        }
        json.NewEncoder(w).Encode(EchoOut{Said: in.Text})
    })

    log.Println("listening on :8080")
    log.Fatal(http.ListenAndServe(":8080", mux))
}
'''
os.makedirs("/content/server", exist_ok=True)
open("/content/server/main.go","w").write(server)
print("server source written. (We won't run it long-running in Colab, but you can: `go run main.go`)")


# %% [markdown] color=amber title="Twelve lines of stdlib gives you an HTTP server.**…"
# # Twelve lines of stdlib gives you an HTTP server.**…
#
# **Twelve lines of stdlib gives you an HTTP server.** No frameworks, no `pip install`. This is why every cloud-native project starts in Go — the path from idea to running service is shorter than anywhere else.


# %% [markdown] color=rose title="6 · JSON"
# # 6 · JSON
#


# %% [markdown] color=lime title="Go's `encoding/json` package marshals/unmarshals…"
# # Go's `encoding/json` package marshals/unmarshals…
#
# Go's `encoding/json` package marshals/unmarshals between structs and JSON. Tag the struct fields:
#
# ```go
# type ChatReq struct {
#     Model    string  `json:"model"`
#     Messages []Msg   `json:"messages"`
#     Temperature float64 `json:"temperature,omitempty"`   // omit if zero
# }
# …


# %% [markdown] color=teal title="7 · Context — deadlines, cancellation, request scoping"
# # 7 · Context — deadlines, cancellation, request scoping
#


# %% color=sky title="ctxdemo = '''package main"
# @explain: Run this cell to see the output.
ctxdemo = '''package main

import (
    "context"
    "fmt"
    "time"
)

// pretend remote call that respects ctx
func slowCall(ctx context.Context) (string, error) {
    select {
    case <-time.After(2 * time.Second):
        return "done", nil
    case <-ctx.Done():
        return "", ctx.Err()
    }
}

func main() {
    ctx, cancel := context.WithTimeout(context.Background(), 500*time.Millisecond)
    defer cancel()

    out, err := slowCall(ctx)
    fmt.Println(out, err)        // → "" deadline exceeded
}
'''
os.makedirs("/content/ctx", exist_ok=True)
open("/content/ctx/main.go","w").write(ctxdemo)
!cd /content/ctx && go run main.go


# %% [markdown] color=mint title="Every function in a request path takes `ctx…"
# # Every function in a request path takes `ctx…
#
# **Every function in a request path takes `ctx context.Context` as its first arg.** It carries:
# - a **deadline** that propagates downstream;
# - a **cancellation signal** so a request that the user closed stops the whole chain;
# - per-request **values** (trace IDs, user IDs).
#
# This is the **single most important Go idiom for backend services.** Always thread `ctx` through; never use `context.Background()` inside a handler.


# %% [markdown] color=peach title="8 · A real LLM gateway — fan-out across backends"
# # 8 · A real LLM gateway — fan-out across backends
#


# %% color=violet title="gateway = '''package main"
# @explain: Run this cell to see the output.
gateway = '''package main

import (
    "context"
    "encoding/json"
    "fmt"
    "io"
    "log"
    "net/http"
    "time"
)

type completionReq struct {
    Model    string `json:"model"`
    Prompt   string `json:"prompt"`
}
type completionResp struct {
    Backend  string `json:"backend"`
    Output   string `json:"output"`
    Latency  string `json:"latency_ms"`
}

// Pretend backend call (would be a real OpenAI-compatible POST in prod)
func callBackend(ctx context.Context, name, url string, req completionReq) completionResp {
    start := time.Now()
    // simulate work + jitter:
    select {
    case <-time.After(time.Duration(50+len(name)*30) * time.Millisecond):
    case <-ctx.Done():
        return completionResp{Backend: name, Output: "<canceled>"}
    }
    return completionResp{
        Backend: name,
        Output:  fmt.Sprintf("[%s] answered: %s", name, req.Prompt),
        Latency: fmt.Sprintf("%d", time.Since(start).Milliseconds()),
    }
}

// Race two backends; whichever returns first wins.
func fanOut(ctx context.Context, req completionReq) completionResp {
    ch := make(chan completionResp, 2)
    backends := map[string]string{
        "vllm-A": "http://vllm-a:8000",
        "vllm-B": "http://vllm-b:8000",
    }
    for name, url := range backends {
        go func(n, u string) { ch <- callBackend(ctx, n, u, req) }(name, url)
    }
    return <-ch        // first one wins
}

func main() {
    mux := http.NewServeMux()
    mux.HandleFunc("POST /v1/completions", func(w http.ResponseWriter, r *http.Request) {
        ctx, cancel := context.WithTimeout(r.Context(), 2*time.Second)
        defer cancel()
        var req completionReq
        if err := json.NewDecoder(io.LimitReader(r.Body, 1<<20)).Decode(&req); err != nil {
            http.Error(w, err.Error(), 400); return
        }
        resp := fanOut(ctx, req)
        json.NewEncoder(w).Encode(resp)
    })

    log.Println("gateway on :8080")
    log.Fatal(http.ListenAndServe(":8080", mux))
}
'''
os.makedirs("/content/gateway", exist_ok=True)
open("/content/gateway/main.go","w").write(gateway)
!cd /content/gateway && go vet . && echo "OK"
print("\nThis is a working pattern: fan-out racing two LLM backends, first response wins,")
print("per-request 2s timeout via context. You can curl POST localhost:8080/v1/completions in real life.")


# %% [markdown] color=amber title="Why this is hard to do well in Python.** GIL +…"
# # Why this is hard to do well in Python.** GIL +…
#
# **Why this is hard to do well in Python.** GIL + asyncio's contagion mean your gateway either spawns a thread per connection (slow) or you go full async (everything in your stack must be async). Go just gives you goroutines + channels and gets out of the way.


# %% [markdown] color=rose title="9 · Tooling"
# # 9 · Tooling
#
# ```bash
# go mod init github.com/me/llm-gateway     # initialise a module
# go mod tidy                                # add/remove dependencies based on imports
#
# go fmt ./...                               # canonical formatting (CI-enforced)
# go vet ./...                               # static checks
# …


# %% [markdown] color=lime title="10 · Picking Go vs Python vs Rust"
# # 10 · Picking Go vs Python vs Rust
#
# | Use case | Pick |
# |---|---|
# | Train a model, fine-tune, eval, research | **Python** (M16-M24, M39) |
# | LLM gateway, sidecar, controller, k8s operator | **Go** |
# | Hot inference path, CUDA kernel, FFI to C++ | **Rust** (M53) or C++ |
# | CLIs distributed to users | Go (one static binary) or Rust |
# …


# %% [markdown] color=teal title="✅ Recap"
# # ✅ Recap
#
# - Go = static binary + goroutines + simple stdlib → **the** glue language for cloud-native AI.
# - Errors are values; **`if err != nil { return err }`** is a feature, not a wart.
# - Goroutines + channels make fan-out / fan-in trivial; pair with `sync.WaitGroup` or `errgroup`.
# - `net/http` + `encoding/json` ship a real HTTP service in 30 lines.
# - **Always thread `ctx`** through your call chain.
# - Default tooling: `go fmt`, `go vet`, `go test -race`, `pprof`.
#
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


