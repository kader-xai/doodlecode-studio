# doodlecode format-version: 2
# Auto-converted from module_75_a2a_protocol_agent_communication.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 75 A2A Protocol Agent Communication"
# # Module 75 A2A Protocol Agent Communication
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 75 — A2A + Agent Communication"
# # Module 75 — A2A + Agent Communication
#
# > **MCP (M64)** standardised how a model talks to **tools**. **A2A (Agent-to-Agent)** — Google's open protocol announced in April 2025 — standardises how one **agent** talks to **another agent**. Imagine an HR agent at Company A asking a payroll agent at Company B to file a tax form, then handing the result to a legal-review agent at Company C — across organisations, with auth, capability discovery, and streaming progress. That's A2A's pitch.
# >
# > By late 2025 the protocol was donated to the **Linux Foundation** with backing from Microsoft, Salesforce, SAP, Atlassian, Cisco, MongoDB and ~50 others — making it the de-facto standard. This module is the practical map.
#
# ### What you'll cover
# 1. **A2A vs MCP** — different problem, different layer
# …


# %% [markdown] color=mint title="1 · A2A vs MCP — different problem, different layer"
# # 1 · A2A vs MCP — different problem, different layer
#
# | | **MCP (M64)** | **A2A (this module)** |
# |---|---|---|
# | Who talks to whom | **Model ↔ Tool** | **Agent ↔ Agent** |
# | Owned by | the host (Claude / Cursor / VS Code) | the agent itself (often another org) |
# | Primitives | tools · resources · prompts | tasks · messages · artifacts |
# | Trust boundary | inside one host process | **across organisations** |
# …


# %% [markdown] color=peach title="2 · The four primitives"
# # 2 · The four primitives
#
# | Primitive | What it is |
# |---|---|
# | **Agent Card** | JSON manifest at `/.well-known/agent.json` — name, description, skills, auth, endpoints |
# | **Task** | a unit of work; has a UUID `taskId` and a state machine |
# | **Message** | a turn in the conversation — list of typed `parts` (text / file / data) |
# | **Artifact** | a typed output produced by a task — files, JSON blobs, references |
# …


# %% [markdown] color=violet title="3 · The protocol surface"
# # 3 · The protocol surface
#
# A2A uses **JSON-RPC 2.0 over HTTPS** (the same family as MCP, deliberately — Google wanted them to feel familiar). For streaming results, it uses **Server-Sent Events (SSE)** on a sub-path of the same endpoint.
#
# Core methods:
#
# | Method | Purpose |
# |---|---|
# …


# %% [markdown] color=amber title="4 · Agent Cards — discovery"
# # 4 · Agent Cards — discovery
#


# %% color=rose title="/.well-known/agent.json"
# @explain: /.well-known/agent.json — what Agent B publishes about itself
# /.well-known/agent.json — what Agent B publishes about itself
agent_card = {
    "name": "Payroll Agent",
    "description": "Files tax forms, computes withholdings, exports W2s.",
    "url": "https://agent-b.example.com/a2a",
    "version": "1.4.0",
    "provider": {
        "organization": "Acme Payroll",
        "url": "https://acme.example.com",
    },
    "capabilities": {
        "streaming": True,
        "pushNotifications": True,
        "stateTransitionHistory": True,
    },
    "authentication": {
        "schemes": ["bearer", "mTLS"],
    },
    "defaultInputModes":  ["text/plain", "application/json"],
    "defaultOutputModes": ["text/plain", "application/json", "application/pdf"],
    "skills": [
        {
            "id": "file_w2",
            "name": "File W-2 form",
            "description": "Submits a W-2 to the IRS for a given employee record.",
            "inputModes":  ["application/json"],
            "outputModes": ["application/pdf"],
            "examples": ["Please file a W-2 for employee #123 for tax year 2025."],
        },
    ],
}
print(json.dumps(agent_card, indent=2)[:500] + " …")


# %% [markdown] color=lime title="Why a manifest.** An agent looking to delegate work…"
# # Why a manifest.** An agent looking to delegate work…
#
# **Why a manifest.** An agent looking to delegate work fetches `https://agent-b.example.com/.well-known/agent.json` once, caches it, and uses it to:
# - pick the right skill (`skills[].id`)
# - format the input correctly (`defaultInputModes`)
# - negotiate auth (`authentication.schemes`)
# - know whether it can stream (`capabilities.streaming`)
#
# `/.well-known/` is the standard place to put metadata for **any HTTPS service** (the [RFC 8615](https://datatracker.ietf.org/doc/html/rfc8615) convention also used by OAuth, OIDC, ACME, password-managers). A2A picked it on purpose.


# %% [markdown] color=teal title="5 · Task lifecycle"
# # 5 · Task lifecycle
#
# ```
#         ┌──────────┐    ┌──────────┐    ┌──────────────────┐    ┌────────────┐
#    →    │submitted │ →  │ working  │ →  │ input-required   │ →  │ completed  │
#         └──────────┘    └─────┬────┘    └────────┬─────────┘    └────────────┘
#                               │                  │
#                               ▼                  ▼
# …


# %% [markdown] color=sky title="6 · Messages — multimodal parts"
# # 6 · Messages — multimodal parts
#


# %% color=mint title="A Message is a list of typed parts"
# @explain: A Message is a list of typed parts — text / file / structured data
# A Message is a list of typed parts — text / file / structured data
example_message = {
    "role": "user",
    "parts": [
        { "type": "text",
          "text": "Please file a W-2 for the attached employee record." },
        { "type": "file",
          "file": {
            "name": "employee_123.json",
            "mimeType": "application/json",
            "bytes": "eyJlbXBsb3llZUlkIjogMTIzfQ=="   # base64
          }
        },
        { "type": "data",
          "data": { "taxYear": 2025, "preferredFilingMethod": "e-file" }
        },
    ],
}
print(json.dumps(example_message, indent=2)[:300] + " …")


# %% [markdown] color=peach title="Three part types** cover almost everything an agent…"
# # Three part types** cover almost everything an agent…
#
# **Three part types** cover almost everything an agent needs to send:
#
# - **`text`** — natural-language instructions or replies.
# - **`file`** — base64 payload **or** a `uri` reference to S3 / signed URL. Use `uri` for big files.
# - **`data`** — typed structured data (JSON Schema validatable). Use this for tool arguments, function results, or anything machine-readable.
#
# The same shape is used for **outgoing** messages (your turn) and **incoming** messages (the other agent's reply). Artifacts on completion are also lists of parts.


# %% [markdown] color=violet title="7 · Streaming with SSE"
# # 7 · Streaming with SSE
#
# A long task that takes ten minutes shouldn't block. A2A's answer: `tasks/sendSubscribe` opens an **SSE** stream that pushes events as the task progresses.
#
# ```http
# POST /a2a HTTP/1.1
# Content-Type: application/json
# Accept: text/event-stream
# …


# %% [markdown] color=amber title="8 · Auth + identity + trust"
# # 8 · Auth + identity + trust
#
# A2A inherits HTTPS's auth ecosystem. The Agent Card declares what schemes are supported in `authentication.schemes`.
#
# | Scheme | When |
# |---|---|
# | **Bearer token** | simple SaaS-to-SaaS, short-lived OAuth access tokens |
# | **mTLS** | cross-org, regulated industries; certs proven by the connecting client |
# …


# %% [markdown] color=rose title="9 · A tiny A2A server + client in Python"
# # 9 · A tiny A2A server + client in Python
#
# The official SDK is `a2a-sdk` (also published as `google-a2a` on PyPI in early 2025; renamed during Linux Foundation transfer). The shape:


# %% color=lime title="pip install a2a-sdk fastapi uvicorn"
# @explain: pip install a2a-sdk fastapi uvicorn
# @explain: SERVER side — wrap a function as a skill, expose at /a2a
# @explain: uvicorn server:app --port 9000
# pip install a2a-sdk fastapi uvicorn

# SERVER side — wrap a function as a skill, expose at /a2a
server_sketch = '''
from a2a_sdk.server import A2AServer, Skill, TaskContext
from fastapi import FastAPI

server = A2AServer(
    name="Math Agent",
    description="Adds, multiplies, factors numbers.",
    url="https://math.example.com/a2a",
)

@server.skill(
    id="add",
    name="Add two numbers",
    description="Returns a + b.",
    input_schema={"type":"object","required":["a","b"],
                  "properties":{"a":{"type":"number"},"b":{"type":"number"}}},
)
async def add(ctx: TaskContext):
    msg = ctx.message
    payload = next(p for p in msg.parts if p.type == "data").data
    a, b = payload["a"], payload["b"]
    await ctx.emit_status("working", "Computing...")
    result = a + b
    await ctx.emit_artifact({"type":"data","data":{"sum": result}})
    await ctx.emit_status("completed")

app = FastAPI()
server.mount(app, path="/a2a")
# uvicorn server:app --port 9000
'''
print(server_sketch)


# %% color=teal title="CLIENT side"
# @explain: CLIENT side — fetch the card, call the skill, stream the result
# @explain: 1) Discover
# @explain: 2) Submit + stream
# CLIENT side — fetch the card, call the skill, stream the result
client_sketch = '''
from a2a_sdk.client import A2AClient

async def main():
    # 1) Discover
    client = await A2AClient.from_well_known("https://math.example.com")
    print("agent:", client.card.name)
    print("skills:", [s.id for s in client.card.skills])

    # 2) Submit + stream
    async for evt in client.send_task_subscribe(
        skill_id="add",
        message={"parts":[{"type":"data","data":{"a": 2, "b": 3}}]},
    ):
        if evt.kind == "status":
            print("status →", evt.status.state)
        elif evt.kind == "artifact":
            print("artifact →", evt.artifact)
        elif evt.kind == "final":
            print("done   →", evt.final_artifacts)
            break
'''
print(client_sketch)


# %% [markdown] color=sky title="Note the shape of the skill handler.** It receives…"
# # Note the shape of the skill handler.** It receives…
#
# **Note the shape of the skill handler.** It receives a **`TaskContext`** — not just inputs and outputs. The context lets the skill:
# - read the incoming message (multi-part)
# - emit status updates (`ctx.emit_status(...)`)
# - emit interim artifacts
# - pause for input (`await ctx.request_input(prompt=...)`)
# - access the original requester's identity (`ctx.caller`)
#
# That's the surface area that lets long-running, multi-turn, cross-org agent workflows feel coherent.


# %% [markdown] color=mint title="10 · A2A vs MCP vs LangGraph hand-off — when to use what"
# # 10 · A2A vs MCP vs LangGraph hand-off — when to use what
#
# | Need | Pick | Why |
# |---|---|---|
# | Model ↔ tool inside one host | **MCP (M64)** | unified tool standard; host owns trust |
# | Agents inside one Python process | **LangGraph / crewAI (M33, M43)** | in-process function calls; no network |
# | Agents across processes in one company | **A2A** — *or* **gRPC (M45)** | A2A if you want capability discovery + lifecycle; gRPC if it's just RPC |
# | Agents across companies | **A2A** | discovery + auth + lifecycle baked in |
# …


# %% [markdown] color=peach title="11 · The 2025 ecosystem + future direction"
# # 11 · The 2025 ecosystem + future direction
#
# The agent-comm space crystallised in 2024-25. Three converging stacks:
#
# | Stack | Backed by | Status |
# |---|---|---|
# | **A2A** | Google (originator), then Linux Foundation, MS, Salesforce, SAP, Atlassian, Cisco, MongoDB, +50 | **De-facto standard in 2025** |
# | **MCP** | Anthropic | tools-side standard, now adopted by OpenAI too |
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


