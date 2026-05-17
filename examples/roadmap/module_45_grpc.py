# doodlecode format-version: 2
# Auto-converted from module_45_grpc.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 45 Grpc"
# # Module 45 Grpc
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 45 — gRPC for AI Backends"
# # Module 45 — gRPC for AI Backends
#
# > When a user hits your chat UI, the call rarely goes straight to the LLM. It hops through 3-7 services: **gateway → auth → rate-limit → embedder → retriever → reranker → LLM** → back. The protocol that connects those services in production isn't REST — it's **gRPC**. It's faster, strictly typed, supports bidirectional streaming, and ships an SDK in 11 languages from a single `.proto` file.
# >
# > TF Serving, Triton Inference Server, Vertex AI, Vespa, Qdrant — all expose a gRPC API alongside REST. This module makes you fluent.
#
# ### What you'll cover
# 1. Why gRPC — the four advantages over REST
# …


# %% [markdown] color=mint title="1 · Why gRPC over REST"
# # 1 · Why gRPC over REST
#
# | | gRPC | REST + JSON |
# |---|---|---|
# | Wire format | Protobuf (binary, schema'd) | JSON (text, schemaless) |
# | Size on the wire | ~5× smaller | baseline |
# | Speed | ~5–10× faster (HTTP/2 + binary) | baseline |
# | Schema | **enforced** — you can't send the wrong field | best-effort, your problem |
# …


# %% [markdown] color=peach title="2 · Protocol Buffers in 5 minutes"
# # 2 · Protocol Buffers in 5 minutes
#
# Protobuf is a **schema language** + a **compact binary encoding**. You write a `.proto` file describing your messages and services, then code-gen typed bindings for every language you care about.
#
# ```protobuf
# syntax = "proto3";
# package ai;
#
# …


# %% [markdown] color=violet title="3 · Setup"
# # 3 · Setup
#


# %% color=amber title="!pip -q install grpcio grpcio-tools protobuf"
# @explain: Run this cell to see the output.
!pip -q install grpcio grpcio-tools protobuf


# %% color=rose title="import os"
# @explain: Run this cell to see the output.
import os
os.makedirs("/content/proto", exist_ok=True)
os.makedirs("/content/gen",   exist_ok=True)


# %% [markdown] color=lime title="4 · Write the `.proto` file"
# # 4 · Write the `.proto` file
#


# %% color=teal title="proto = '''syntax = 'proto3'"
# @explain: Run this cell to see the output.
proto = '''syntax = "proto3";
package ai;

message EmbedRequest  { string text = 1; string model = 2; }
message EmbedResponse { repeated float vector = 1; int32 dim = 2; }

message ChatRequest   { string user_id = 1; string content = 2; }
message ChatToken     { string token = 1; bool done = 2; }

service Embedder {
  // unary RPC
  rpc Embed (EmbedRequest) returns (EmbedResponse);
}

service Chat {
  // server-streaming: client sends one prompt, server streams tokens back
  rpc Stream (ChatRequest) returns (stream ChatToken);
}
'''
open("/content/proto/ai.proto", "w").write(proto)
print("wrote /content/proto/ai.proto")


# %% [markdown] color=sky title="5 · Code-gen — one command builds the SDK"
# # 5 · Code-gen — one command builds the SDK
#


# %% color=mint title="!python -m grpc_tools.protoc \"
# @explain: Run this cell to see the output.
!python -m grpc_tools.protoc \
    --proto_path=/content/proto \
    --python_out=/content/gen \
    --grpc_python_out=/content/gen \
    /content/proto/ai.proto

!ls /content/gen


# %% [markdown] color=peach title="You now have"
# # You now have
#
# You now have:
# - `ai_pb2.py` — message classes (`EmbedRequest`, `EmbedResponse`, …)
# - `ai_pb2_grpc.py` — service stubs (`EmbedderStub`, `EmbedderServicer`, `ChatStub`, …)
#
# Same file generates **Go / Java / TS / Rust / etc.** clients. One schema, every language.


# %% [markdown] color=violet title="6 · Implement the server"
# # 6 · Implement the server
#


# %% color=amber title="Stand-in embedder: deterministic 16-d 'embedding'…"
# @explain: Stand-in embedder: deterministic 16-d "embedding" of the text
import sys; sys.path.insert(0, "/content/gen")
import ai_pb2, ai_pb2_grpc, grpc, time, hashlib
from concurrent import futures

# Stand-in embedder: deterministic 16-d "embedding" of the text
def fake_embed(text: str, dim: int = 16):
    h = hashlib.md5(text.encode()).digest()
    return [(b - 128)/128.0 for b in h[:dim]]

class EmbedderImpl(ai_pb2_grpc.EmbedderServicer):
    def Embed(self, req, ctx):
        v = fake_embed(req.text)
        return ai_pb2.EmbedResponse(vector=v, dim=len(v))

class ChatImpl(ai_pb2_grpc.ChatServicer):
    def Stream(self, req, ctx):
        for tok in ["The ","capital ","of ","France ","is ","Paris."]:
            yield ai_pb2.ChatToken(token=tok, done=False)
            time.sleep(0.05)
        yield ai_pb2.ChatToken(token="", done=True)

server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
ai_pb2_grpc.add_EmbedderServicer_to_server(EmbedderImpl(), server)
ai_pb2_grpc.add_ChatServicer_to_server(ChatImpl(), server)
server.add_insecure_port("[::]:50051")
server.start()
print("gRPC server up on :50051")


# %% [markdown] color=rose title="7 · Client — call it like a local function"
# # 7 · Client — call it like a local function
#


# %% color=lime title="unary"
# @explain: unary
channel = grpc.insecure_channel("localhost:50051")
emb = ai_pb2_grpc.EmbedderStub(channel)
chat = ai_pb2_grpc.ChatStub(channel)

# unary
resp = emb.Embed(ai_pb2.EmbedRequest(text="hello world", model="m1"), timeout=2.0)
print("dim:", resp.dim, " vector[:5]:", list(resp.vector[:5]))


# %% [markdown] color=teal title="8 · Server-streaming — token streams"
# # 8 · Server-streaming — token streams
#


# %% color=sky title="server streaming: iterate over the stub call → it…"
# @explain: server streaming: iterate over the stub call → it yields tokens
# server streaming: iterate over the stub call → it yields tokens
for tok in chat.Stream(ai_pb2.ChatRequest(user_id="u123", content="capital of France?")):
    if tok.done: print("\n[DONE]"); break
    print(tok.token, end="", flush=True)


# %% [markdown] color=mint title="Streaming flavours"
# # Streaming flavours
#
# **Streaming flavours.**
#
# | Pattern | proto syntax | Use case |
# |---|---|---|
# | Unary | `rpc M (R) returns (S)` | "embed this text" |
# | Server-streaming | `returns (stream S)` | LLM token streams (this demo) |
# | Client-streaming | `(stream R) returns (S)` | uploading a long doc, single summary back |
# | Bidirectional | `(stream R) returns (stream S)` | live chat, ASR, multi-turn agents |


# %% [markdown] color=peach title="9 · Production basics"
# # 9 · Production basics
#
# ```python
# # DEADLINES — every call should set one
# resp = emb.Embed(req, timeout=0.5)         # 500 ms; raises grpc.RpcError on timeout
#
# # ERRORS — set status + message from the server side
# context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
# …


# %% [markdown] color=violet title="10 · gRPC vs REST vs WebSocket vs MQ"
# # 10 · gRPC vs REST vs WebSocket vs MQ
#
# | Need | Use |
# |---|---|
# | Public API, browser-direct, easy curl | **REST + JSON** |
# | Service-to-service in your DC, low latency | **gRPC** |
# | Real-time browser ↔ server (chat) | **WebSocket** or **gRPC-Web** + bidi |
# | Async fan-out, durable, decoupled producers/consumers | **Kafka / NATS / Redis Streams** |
# …


# %% [markdown] color=amber title="✅ Recap"
# # ✅ Recap
#
# - gRPC = Protobuf schema + HTTP/2 + code-gen for 11 languages.
# - One `.proto` file → `ai_pb2.py` + `ai_pb2_grpc.py` via `grpc_tools.protoc`.
# - Four call shapes: unary, server-stream, client-stream, bidi.
# - Always set deadlines; use interceptors for auth, tracing, retries; mTLS for service-to-service.
# - Default architecture: **REST/SSE at the edge, gRPC inside.**
#
# Cleanup:


# %% color=rose title="server.stop(grace=1)"
# @explain: Run this cell to see the output.
server.stop(grace=1)


# %% [markdown] color=lime title="Next: **M46"
# # Next: **M46
#
# Next: **M46 — Kubernetes for ML** (running these services in production).


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


