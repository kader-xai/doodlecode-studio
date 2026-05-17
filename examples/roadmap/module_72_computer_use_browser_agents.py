# doodlecode format-version: 2
# Auto-converted from module_72_computer_use_browser_agents.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 72 Computer Use Browser Agents"
# # Module 72 Computer Use Browser Agents
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 72 — Computer-use / Browser Agents"
# # Module 72 — Computer-use / Browser Agents
#
# > Every app has an API. **Except when it doesn't.** Internal admin panels, legacy SaaS, banking portals, government forms, that one Salesforce screen — they're all human-only UIs. **Computer-use agents** close the gap: a vision-language model (M65) watches a screen, reasons about what to click, and emits `click(x, y)` / `type("...")` / `scroll` actions. **Browser agents** are the same thing scoped to a web page (cheaper, sandboxable, faster).
# >
# > This module is the map of the space: **Claude computer-use**, **OpenAI Operator / Computer-use Agent**, **Playwright-AI / Browser Use / browser-use** for OSS, and the safety patterns that keep them from wiring your savings to a stranger.
#
# ### What you'll cover
# 1. Why computer-use exists — when APIs aren't an option
# …


# %% [markdown] color=mint title="1 · Why computer-use exists"
# # 1 · Why computer-use exists
#
# | Situation | Why not an API? |
# |---|---|
# | Internal admin portal | nobody wrote the API; no time / no budget |
# | Legacy SaaS | API is paid tier; you're on the free tier |
# | Government / bank portal | "we have an API" → 50-page PDF + manual onboarding |
# | Salesforce or Workday screen | API exists but auth is locked down by IT |
# …


# %% [markdown] color=peach title="2 · The mental model"
# # 2 · The mental model
#
# ```
#    ┌──────────────────────────────────────────────────────────┐
#    │  loop:                                                    │
#    │    screenshot     ←─ OS / Playwright / Chrome DevTools    │
#    │      │                                                    │
#    │      ▼                                                    │
# …


# %% [markdown] color=violet title="3 · The action space"
# # 3 · The action space
#
# Every computer-use API ships roughly the same primitives. Below is the Claude / OpenAI shape:
#
# | Tool | Args | Effect |
# |---|---|---|
# | `screenshot` | — | return the current screen (PNG bytes) |
# | `mouse_move` | `(x, y)` | cursor only |
# …


# %% [markdown] color=amber title="4 · The 2025-26 hosted providers"
# # 4 · The 2025-26 hosted providers
#


# %% color=rose title="Hosted computer-use APIs"
# @explain: Hosted computer-use APIs (latest as of 2025-26)
# @explain: 1) ANTHROPIC — Claude computer-use (built-in tool type)
# @explain: pyautogui / Playwright / VM-side capture
# @explain: Then loop: parse tool_use blocks (action), execute, screenshot again, send back, repeat
# Hosted computer-use APIs (latest as of 2025-26)

# 1) ANTHROPIC — Claude computer-use (built-in tool type)
anthropic_sketch = '''
import anthropic, base64
client = anthropic.Anthropic()

def take_screenshot() -> bytes:
    # pyautogui / Playwright / VM-side capture
    ...

screenshot_b64 = base64.b64encode(take_screenshot()).decode()

resp = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    tools=[
        {"type": "computer_20241022", "name": "computer",
         "display_width_px": 1280, "display_height_px": 800, "display_number": 1},
    ],
    messages=[
        {"role": "user", "content": [
            {"type": "text", "text": "Open Gmail and find the unread message from Alice."},
            {"type": "image",
             "source": {"type": "base64", "media_type": "image/png", "data": screenshot_b64}},
        ]},
    ],
)
# Then loop: parse tool_use blocks (action), execute, screenshot again, send back, repeat.
'''
print(anthropic_sketch)


# %% color=lime title="2) OPENAI"
# @explain: 2) OPENAI — Computer-use Agent (Operator) via the Responses API
# @explain: The model returns "computer_call" actions in the response object
# @explain: You execute them and call back with the new screenshot
# 2) OPENAI — Computer-use Agent (Operator) via the Responses API
openai_sketch = '''
from openai import OpenAI
client = OpenAI()

resp = client.responses.create(
    model="computer-use-preview",
    tools=[{"type": "computer-use_preview",
            "display_width": 1280, "display_height": 800, "environment": "browser"}],
    input=[{
        "role": "user",
        "content": [{"type": "input_text", "text": "Book the cheapest flight CDG → LHR for next Friday."}],
    }],
    truncation="auto",
)
# The model returns "computer_call" actions in the response object.
# You execute them and call back with the new screenshot.
'''
print(openai_sketch)


# %% [markdown] color=teal title="Two more options worth knowing"
# # Two more options worth knowing
#
# **Two more options worth knowing.**
# - **Gemini 2.5 Computer Use / Mariner** (Google) — same idea, in Vertex AI.
# - **Anthropic Claude Code + computer-use** — the agentic IDE pattern; the model can drive your browser to verify a code change.
#
# All three providers ship **reference loops** in their cookbooks. Don't write the screenshot/action loop yourself — copy theirs and customise.


# %% [markdown] color=sky title="5 · Open-source browser agents"
# # 5 · Open-source browser agents
#
# When you don't want to send screenshots to a vendor, or you want **deterministic browser primitives** instead of OS-level pixel control, the OSS stack:
#
# | Project | What it is | Notes |
# |---|---|---|
# | **browser-use** | Python wrapper: LLM drives a Playwright browser via DOM + accessibility tree | most popular OSS in 2025; pluggable models (OpenAI/Anthropic/local) |
# | **Skyvern** | end-to-end browser-agent platform; visual + DOM hybrid | self-hostable; commercial cloud too |
# …


# %% color=mint title="browser-use minimal example"
# @explain: browser-use minimal example
# @explain: pip install browser-use playwright && playwright install chromium
# browser-use minimal example
browser_use_sketch = '''
# pip install browser-use playwright && playwright install chromium
import asyncio
from browser_use import Agent, ChatOpenAI

agent = Agent(
    task="Find the price of the cheapest 256 GB iPhone 17 on the Apple India website.",
    llm=ChatOpenAI(model="gpt-4o"),
)

async def main():
    result = await agent.run()
    print(result.final_result())

asyncio.run(main())
'''
print(browser_use_sketch)


# %% [markdown] color=peach title="6 · Playwright + LLM — build it yourself"
# # 6 · Playwright + LLM — build it yourself
#


# %% color=violet title="Pseudocode for the cleanest self-built browser agent"
# @explain: Pseudocode for the cleanest self-built browser agent
# @explain: asyncio.run(run("buy the cheapest copy of Crime and Punishment",
# @explain: "https://www.amazon.com"))
# Pseudocode for the cleanest self-built browser agent
playwright_loop = '''
from playwright.async_api import async_playwright
import base64, asyncio
from openai import AsyncOpenAI                    # or anthropic, or any vLLM endpoint

client = AsyncOpenAI()

SYSTEM = (
    "You are a browser-use agent. At each step you are given a screenshot "
    "and a task. Reply ONLY with one of:\n"
    "- CLICK x y\n- TYPE \"text\"\n- SCROLL dy\n- KEY name\n"
    "- NAVIGATE url\n- DONE  (when the task is achieved)\n"
    "Output nothing else."
)

async def step(page, task, history):
    png = await page.screenshot()
    b64 = base64.b64encode(png).decode()
    msg = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM},
            *history,
            {"role": "user", "content": [
                {"type": "text", "text": f"Task: {task}\nReply with one action."},
                {"type": "image_url",
                 "image_url": {"url": f"data:image/png;base64,{b64}"}},
            ]},
        ],
    )
    return msg.choices[0].message.content.strip()

async def run(task: str, start_url: str, max_steps: int = 25):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(start_url)

        history = []
        for i in range(max_steps):
            action = await step(page, task, history)
            print(i, action)
            if action.startswith("DONE"): break
            history.append({"role": "assistant", "content": action})

            tok, *rest = action.split()
            if tok == "CLICK":
                x, y = map(int, rest);  await page.mouse.click(x, y)
            elif tok == "TYPE":
                await page.keyboard.type(action.split('"',1)[1].rstrip('"'))
            elif tok == "SCROLL":
                await page.mouse.wheel(0, int(rest[0]))
            elif tok == "KEY":
                await page.keyboard.press(rest[0])
            elif tok == "NAVIGATE":
                await page.goto(rest[0])
            await page.wait_for_timeout(700)

        await browser.close()

# asyncio.run(run("buy the cheapest copy of Crime and Punishment",
#                 "https://www.amazon.com"))
'''
print(playwright_loop)


# %% [markdown] color=amber title="Why building it yourself is sometimes the right call"
# # Why building it yourself is sometimes the right call
#
# **Why building it yourself is sometimes the right call.**
# - You control the **action vocabulary** — add `extract_text`, `read_aria_tree`, `wait_for_selector`.
# - You control the **stop condition** — your own scorer, your own retries.
# - You can **swap the model** — local Qwen2.5-VL when cheap, GPT-4o when cost is no object.
# - You see every screenshot + action — easier to **debug** than a hosted black box.
#
# **Why building it yourself is sometimes the wrong call.**
# - Hosted providers train the model specifically for accurate UI grounding. Their accuracy is hard to match.
# …


# %% [markdown] color=rose title="7 · Benchmarks"
# # 7 · Benchmarks
#
# How good *is* the state of the art? As of 2025-26:
#
# | Benchmark | What it measures | Frontier headline number |
# |---|---|---|
# | **OSWorld** | full Linux desktop tasks (file manager, email, spreadsheets, browsers) | ~30-45% success — still far from human |
# | **WebArena** | full-fidelity web apps (GitLab, Shopping, Reddit) | ~40-55% |
# …


# %% [markdown] color=lime title="8 · Sandboxing + safety — the only section that really matters"
# # 8 · Sandboxing + safety — the only section that really matters
#
# If you take nothing else from this module, take this: **a computer-use agent will eventually click something you didn't intend.** Plan for it.
#
# ### Three layers of defence
#
# **Layer 1 — VM isolation.**
# Run the agent's browser/desktop **inside a disposable VM or container**. No host access. Fresh image per task. The big providers ship reference images:
# …


# %% [markdown] color=teal title="9 · Failure modes you'll see in production"
# # 9 · Failure modes you'll see in production
#
# | Failure | Why | Mitigation |
# |---|---|---|
# | **Coordinate drift** | model clicks 8 px off; misses the button | use accessibility-tree fallback; verify with post-click screenshot |
# | **Infinite loop** | model "thinks" the page hasn't changed; clicks the same button forever | hash the screenshot; abort on N identical hashes |
# | **Login expiry** | session times out mid-task | persistent storage state per task; explicit `relogin` action |
# | **CAPTCHA wall** | bot detection trips; agent stuck | escalate to human; never train the agent to solve CAPTCHAs |
# …


# %% [markdown] color=sky title="10 · Decision tree — pick a stack"
# # 10 · Decision tree — pick a stack
#
# ```
# Do you need OS-level control (desktop apps, multi-window)?
#    │
#    ├─ Yes
#    │   ├─ hosted, willing to send screenshots to a vendor? → Claude / OpenAI / Gemini computer-use
#    │   └─ self-hosted only?                                 → Anthropic ref VM + local Qwen2.5-VL + UI-TARS
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


