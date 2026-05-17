# doodlecode format-version: 2
# Auto-converted from module_64_mcp_model_context_protocol.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 64 Mcp Model Context Protocol"
# # Module 64 Mcp Model Context Protocol
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 64 — MCP"
# # Module 64 — MCP
#
# > Every AI app eventually wants the same five things: read files, query Postgres, hit the GitHub API, search Slack, control a browser. M32–M35's agents wired each one bespoke. **Model Context Protocol (MCP)** — Anthropic's open standard from late 2024 — replaces that with **one wire protocol** every assistant and every tool source can speak. Build your data source as an MCP **server** once; Claude Desktop, Claude Code, Cursor, Zed, VS Code Copilot, and many others can use it instantly.
# >
# > Think "USB-C for AI tools."
#
# ### What you'll cover
# 1. The problem MCP solves
# …


# %% [markdown] color=mint title="1 · The problem"
# # 1 · The problem
#
# Before MCP, every AI assistant connected to every tool *independently*:
#
# ```
#    Claude    ←→ {github-tools, fs-tools, slack-tools, gh-pr-tools, …}
#    ChatGPT   ←→ {github-tools, fs-tools, slack-tools, …}   ← all rewritten
#    Cursor    ←→ {github-tools, fs-tools, slack-tools, …}   ← rewritten again
# …


# %% [markdown] color=peach title="2 · The three primitives"
# # 2 · The three primitives
#
# MCP servers expose **three** kinds of things:
#
# | Primitive | Initiated by | Used for |
# |---|---|---|
# | **Tool** | The model | actions with side-effects — "create a GitHub issue," "execute SQL" |
# | **Resource** | The host (you, or the model with permission) | read-only data the model should *see* — "the contents of `/repo/README.md`" |
# …


# %% [markdown] color=violet title="3 · Architecture"
# # 3 · Architecture
#


# %% [markdown] color=amber title="```"
# # ```
#
# ```
# ┌────────────────────────────────┐       ┌────────────────────────────┐
# │           HOST                  │       │       MCP SERVER           │
# │  (Claude Desktop, VS Code,      │       │  Your code that exposes    │
# │   Cursor, Zed, your own app)    │       │  tools / resources /       │
# │                                 │       │  prompts                   │
# │   ┌──────────────────────┐      │       │                            │
# │   │      CLIENT          │ ◄─── │ JSON-RPC over stdio / HTTP+SSE ──► │
# …


# %% [markdown] color=rose title="4 · Setup"
# # 4 · Setup
#


# %% color=lime title="!pip -q install mcp 'mcp[cli]'"
# @explain: Run this cell to see the output.
!pip -q install mcp 'mcp[cli]'


# %% [markdown] color=teal title="The official Python SDK is **`mcp`**"
# # The official Python SDK is **`mcp`**
#
# The official Python SDK is **`mcp`**. It includes:
# - `mcp.server.fastmcp.FastMCP` — high-level decorator API for building servers.
# - `mcp.client.session` — client-side primitives if you want to *talk to* a server (we'll do that too).
# - `mcp` CLI — `mcp dev your_server.py` to debug locally with the Inspector UI.


# %% [markdown] color=sky title="5 · Build an MCP server in 30 lines"
# # 5 · Build an MCP server in 30 lines
#


# %% color=mint title="write a small server file we can launch later"
# @explain: write a small server file we can launch later
# write a small server file we can launch later
server_code = '''
"""weather_server.py — a toy MCP server."""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Weather")

@mcp.tool()
def get_forecast(city: str, units: str = "c") -> dict:
    """Get the (faked) weather forecast for a city.

    Args:
        city: city name, e.g. "Paris"
        units: "c" or "f"
    """
    fake = {"Paris": 21, "Tokyo": 27, "Seattle": 14, "Chennai": 33}
    temp = fake.get(city, 20)
    if units == "f":
        temp = round(temp * 9/5 + 32)
    return {"city": city, "temp": temp, "units": units, "condition": "sunny"}

@mcp.resource("note://latest")
def latest_note() -> str:
    """Read the most recently saved note."""
    return "Remember: ship MCP server for the support team by Friday."

@mcp.prompt()
def trip_plan(destination: str) -> str:
    """Generate a request to plan a one-day trip."""
    return (
        f"Plan a one-day itinerary for {destination}. "
        "Use the get_forecast tool first to check the weather, "
        "then suggest morning, afternoon and evening activities."
    )

if __name__ == "__main__":
    mcp.run()                  # default: stdio transport
'''
import pathlib
pathlib.Path("/content/weather_server.py").write_text(server_code)
print("server written")


# %% [markdown] color=peach title="Read what you wrote"
# # Read what you wrote
#
# **Read what you wrote.**
# - `@mcp.tool()` — exposes `get_forecast` as a model-callable tool. The **type hints** become the JSON schema; the **docstring** becomes the description the model sees.
# - `@mcp.resource("note://latest")` — exposes a read-only resource. The URI scheme is yours to design.
# - `@mcp.prompt()` — exposes a parameterised prompt the *user* can pick from a menu.
# - `mcp.run()` defaults to stdio. Change to `mcp.run(transport="streamable-http", port=8000)` for HTTP.
#
# **That's a real, working MCP server.** Add `command: python /content/weather_server.py` to a host's MCP config and Claude Desktop / Cursor / Zed will discover and call all three primitives.


# %% [markdown] color=violet title="6 · The wire format — what actually flows"
# # 6 · The wire format — what actually flows
#
# MCP is **JSON-RPC 2.0** under the hood. Here's a real session:
#
# ```jsonc
# // Host → server (first thing always)
# → { "jsonrpc": "2.0", "id": 1, "method": "initialize",
#     "params": { "protocolVersion": "2025-06-18",
# …


# %% [markdown] color=amber title="7 · Resources — pulling data into context"
# # 7 · Resources — pulling data into context
#
# A common mistake is shoving everything through tools. Tools should be for *side-effects*. For read-only data, use **resources**:


# %% color=rose title="Static resource"
# @explain: Static resource — fixed URI
# @explain: Templated resource — URI placeholders captured as args
# @explain: Binary resource — returns bytes
resource_examples = '''
# Static resource — fixed URI
@mcp.resource("config://app")
def app_config() -> str:
    return open("/etc/app/config.yaml").read()

# Templated resource — URI placeholders captured as args
@mcp.resource("file:///{path}")
def read_file(path: str) -> str:
    """Read a local file (sandboxed)."""
    safe_root = "/content/docs/"
    full = safe_root + path
    if not full.startswith(safe_root): raise ValueError("path escape!")
    return open(full).read()

# Binary resource — returns bytes
from mcp.server.fastmcp.resources import binary
@mcp.resource("image://logo")
def logo() -> bytes:
    return open("/content/logo.png", "rb").read()
'''
print(resource_examples)


# %% [markdown] color=lime title="Why resources beat tools for reading data"
# # Why resources beat tools for reading data
#
# **Why resources beat tools for reading data.**
# - The host can **stream** them into the model's context without an extra round trip.
# - The user can pick which resources to attach (in Claude Desktop: the paperclip menu).
# - Resources support **subscriptions** — the server can push an `updated` notification when the file changes.
# - The model never has to "decide" to fetch them — the host or user does.
#
# Rule: **side-effects → tool. Read-only data → resource.**


# %% [markdown] color=teal title="8 · Prompts — reusable workflows"
# # 8 · Prompts — reusable workflows
#


# %% color=sky title="prompt_examples = '''"
# @explain: Run this cell to see the output.
prompt_examples = '''
@mcp.prompt()
def code_review(language: str, code: str) -> str:
    """Review a code snippet."""
    return (
        f"You are a senior {language} engineer. Review the following code for "
        "correctness, security, readability, and idiomatic style. List issues, "
        "then propose minimal fixes.\n\n```{language}\n{code}\n```"
    )

@mcp.prompt()
def pr_release_notes(branch: str, tag: str) -> str:
    return (
        f"Compare git diff between {tag} and {branch} (you can use the git tools). "
        "Group changes into Features / Fixes / Breaking / Docs. "
        "Write release notes in markdown.\n"
    )
'''
print(prompt_examples)


# %% [markdown] color=mint title="Prompts show up in the host's UI as commands…"
# # Prompts show up in the host's UI as commands…
#
# Prompts show up in the host's UI as commands (`/code-review`, `/pr-release-notes`). Users pick one, fill in arguments, and a fully-formed prompt is inserted into the chat. Great for **codifying playbooks** so they live in code, not in someone's head.


# %% [markdown] color=peach title="9 · Wire it to a host"
# # 9 · Wire it to a host
#


# %% [markdown] color=violet title="Claude Desktop / Claude Code"
# # Claude Desktop / Claude Code
#
# Edit `~/.config/Claude/claude_desktop_config.json` (or use **`mcp install`**):
#
# ```jsonc
# {
#   "mcpServers": {
#     "weather": {
# …


# %% color=amber title="`mcp dev` launches your server with the Inspector"
# @explain: `mcp dev` launches your server with the Inspector — a web UI that lets you call tools,
# @explain: read resources, and watch the JSON-RPC traffic
# @explain: mcp dev /content/weather_server.py
# @explain: Or talk to it as a client from Python:
# `mcp dev` launches your server with the Inspector — a web UI that lets you call tools,
# read resources, and watch the JSON-RPC traffic.
#
#   mcp dev /content/weather_server.py
#
# Or talk to it as a client from Python:
client_code = '''
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    server = StdioServerParameters(command="python", args=["/content/weather_server.py"])
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as sess:
            await sess.initialize()
            print("tools:", [t.name for t in (await sess.list_tools()).tools])
            r = await sess.call_tool("get_forecast", {"city": "Tokyo", "units": "f"})
            print("result:", r.content)

asyncio.run(main())
'''
print(client_code)


# %% [markdown] color=rose title="10 · MCP vs OpenAI function-calling vs LangChain tools"
# # 10 · MCP vs OpenAI function-calling vs LangChain tools
#
# | | OpenAI function-calling | LangChain `@tool` | MCP |
# |---|---|---|---|
# | Defined in | client app | client app | **separate process** |
# | Reusable across hosts? | each provider's format | Python-only | **any MCP host** |
# | Discovers at runtime? | ✗ (compiled in) | ✗ | ✓ (`tools/list`) |
# | Auth lives with | the client | the client | the **server** (closer to the data) |
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


