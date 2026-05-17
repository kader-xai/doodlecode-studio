# doodlecode format-version: 2
# Auto-converted from module_54_typescript_for_ai_frontends.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 54 Typescript For Ai Frontends"
# # Module 54 Typescript For Ai Frontends
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 54 — TypeScript for AI Frontends"
# # Module 54 — TypeScript for AI Frontends
#
# > The whole course built the **backend**. M44–M53 stood up vLLM, gRPC, Kubernetes, observability, the polyglot stack. But **users only see the frontend** — the chat box, the streaming tokens, the citations, the tool-call cards. And the language of frontends in 2026 is **TypeScript**.
# >
# > This module is the missing piece. TypeScript fundamentals, then the **Vercel AI SDK** + **React** combo most production AI apps use, then **streaming**, **tool calls**, **structured outputs**, and **deployment** — wired against the OpenAI-compatible `/v1` endpoint your backend already exposes.
#
# ### What you'll cover
# 1. Why TypeScript — and why every AI startup ships it
# …


# %% [markdown] color=mint title="1 · Why TypeScript"
# # 1 · Why TypeScript
#
# | Reason | Why it matters for AI apps |
# |---|---|
# | **Static types** on top of JS | typo in `messages[0].rol` is a compile error, not a runtime crash |
# | **One language end-to-end** | the same Zod schema validates a tool call on browser, edge, and Node |
# | **Massive ecosystem** | every model SDK ships TS first (OpenAI, Anthropic, Mistral, Cohere, Vertex) |
# | **Edge runtimes** | TS bundles run on Cloudflare / Vercel / Bun edge — sub-50 ms cold start near the user |
# …


# %% [markdown] color=peach title="2 · TypeScript in 5 minutes"
# # 2 · TypeScript in 5 minutes
#


# %% color=violet title="ts_tour = '''// types: like Python type hints"
# @explain: Run this cell to see the output.
ts_tour = '''// types: like Python type hints, but enforced
const model: string = "gpt-4o-mini";
const temperature: number = 0.7;
const stream: boolean = true;

// INTERFACE — describe the shape of an object
interface ChatMessage {
  role: "system" | "user" | "assistant" | "tool";   // union of literals
  content: string;
  name?: string;          // optional
}

const msgs: ChatMessage[] = [
  { role: "user", content: "What is RAG?" },
];

// GENERICS — types parameterised by other types
function head<T>(xs: T[]): T | undefined {
  return xs[0];
}
const first = head(msgs);   // inferred as ChatMessage | undefined

// NARROWING — TS understands `if`/`typeof`/`in` checks
function describe(x: string | number) {
  if (typeof x === "string") return x.toUpperCase();   // here TS knows x is string
  return x.toFixed(2);                                  // here it's number
}

// TYPE ALIAS — sometimes nicer than interface
type Tool = { name: string; description: string; schema: unknown };

console.log(first, describe("hi"), describe(3.14159));
'''
print(ts_tour)


# %% [markdown] color=amber title="Things that bite Python devs"
# # Things that bite Python devs
#
# **Things that bite Python devs.**
# - TS types are **erased** at runtime — no `isinstance(x, ChatMessage)`. For runtime checks use **Zod**.
# - `interface` ≈ `type` for object shapes; pick whichever your team prefers.
# - `unknown` (safer) vs `any` (the escape hatch — avoid).
# - `?:` makes a field optional; `!:` asserts "trust me, it's there".
# - `as const` freezes literals, often necessary to keep unions narrow.


# %% [markdown] color=rose title="3 · The AI SDK landscape"
# # 3 · The AI SDK landscape
#
# | SDK | Best for | Backend support |
# |---|---|---|
# | **Vercel AI SDK** (`ai`) | full-stack apps with streaming + React/Svelte/Vue hooks | OpenAI, Anthropic, Google, Mistral, Cohere, **OpenAI-compatible (vLLM, Ollama, llama-server)** |
# | **OpenAI SDK** (`openai`) | direct OpenAI calls or any compat backend | OpenAI (and via `baseURL` override: vLLM, Ollama, …) |
# | **Anthropic SDK** (`@anthropic-ai/sdk`) | Claude tool-use, computer-use | Anthropic |
# | **LangChain.js** | port of LangChain (M32) | many — same abstractions as Python |
# …


# %% [markdown] color=lime title="4 · Minimal Node script — call your vLLM backend"
# # 4 · Minimal Node script — call your vLLM backend
#


# %% color=teal title="tsnode = '''// chat.ts"
# @explain: Run this cell to see the output.
tsnode = '''// chat.ts — run with `npx tsx chat.ts`
import { generateText } from "ai";
import { createOpenAI } from "@ai-sdk/openai";

const provider = createOpenAI({
  baseURL: process.env.OPENAI_BASE_URL ?? "http://localhost:8000/v1",
  apiKey:  process.env.OPENAI_API_KEY  ?? "x",          // any non-empty string
});

const { text, usage } = await generateText({
  model: provider("Qwen/Qwen2.5-0.5B-Instruct"),
  system: "You are a terse assistant.",
  prompt: "What is PagedAttention?",
});

console.log(text);
console.log("tokens:", usage);
'''
print(tsnode)


# %% [markdown] color=sky title="That's the whole script.** `generateText` works…"
# # That's the whole script.** `generateText` works…
#
# **That's the whole script.** `generateText` works against **OpenAI, Anthropic, vLLM (M44), Ollama (M38), llama-server (M38)** with no code change — just swap the provider. The same shape works in Node, Bun, Vercel Edge, Cloudflare Workers.


# %% [markdown] color=mint title="5 · Streaming — Server-Sent Events done right"
# # 5 · Streaming — Server-Sent Events done right
#
# LLMs feel slow if you wait for the whole response. **Stream tokens** the moment they're produced.


# %% color=peach title="ts_stream = '''// In a Next.js / React Router /…"
# @explain: Run this cell to see the output.
ts_stream = '''// In a Next.js / React Router / Remix route handler:
import { streamText } from "ai";

export async function POST(req: Request) {
  const { messages } = await req.json();
  const result = await streamText({
    model: provider("Qwen/Qwen2.5-0.5B-Instruct"),
    system: "Answer in one paragraph.",
    messages,
  });
  return result.toDataStreamResponse();   // SSE-compatible Response
}
'''
print(ts_stream)


# %% [markdown] color=violet title="On the wire that's a stream of tiny JSON-encoded events"
# # On the wire that's a stream of tiny JSON-encoded events
#
# On the wire that's a stream of tiny JSON-encoded events:
# ```
# data: { "type": "text-delta", "textDelta": "Paged" }
# data: { "type": "text-delta", "textDelta": "Attention" }
# data: { "type": "text-delta", "textDelta": " is …" }
# data: { "type": "finish", "usage": { … } }
# ```
#
# …


# %% [markdown] color=amber title="6 · React + `useChat` — a chat UI in 30 lines"
# # 6 · React + `useChat` — a chat UI in 30 lines
#


# %% color=rose title="ts_react = '''// app/page.tsx"
# @explain: Run this cell to see the output.
ts_react = '''// app/page.tsx — Next.js App Router
"use client";
import { useChat } from "ai/react";

export default function Page() {
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat();

  return (
    <main className="mx-auto max-w-2xl p-6">
      <ul className="space-y-2">
        {messages.map(m => (
          <li key={m.id} className={m.role === "user" ? "text-right" : ""}>
            <span className="rounded-2xl px-3 py-2 inline-block bg-gray-100">
              <strong>{m.role}:</strong> {m.content}
            </span>
          </li>
        ))}
      </ul>

      <form onSubmit={handleSubmit} className="flex gap-2 mt-4">
        <input
          value={input}
          onChange={handleInputChange}
          placeholder="Ask anything…"
          className="flex-1 border rounded px-3 py-2"
        />
        <button disabled={isLoading} className="px-4 py-2 rounded bg-black text-white">
          {isLoading ? "…" : "Send"}
        </button>
      </form>
    </main>
  );
}
'''
print(ts_react)


# %% [markdown] color=lime title="That's a **streaming chat UI**"
# # That's a **streaming chat UI**
#
# That's a **streaming chat UI**. `useChat()`:
# - POSTs to `/api/chat` (the route from §5) automatically.
# - Keeps `messages` in React state, **including the streaming partial assistant message**.
# - Exposes `isLoading`, `stop()`, `reload()`, `append()` for tool integrations.
# - Works with multi-modal attachments out of the box.
#
# In **Svelte**, `useChat` is `useChat()` from `ai/svelte`. In **Vue**, `ai/vue`. Same API.


# %% [markdown] color=teal title="7 · Tool calling + Zod schemas"
# # 7 · Tool calling + Zod schemas
#


# %% color=sky title="ts_tools = '''// app/api/chat/route.ts"
# @explain: Run this cell to see the output.
ts_tools = '''// app/api/chat/route.ts
import { streamText, tool } from "ai";
import { z } from "zod";

const tools = {
  weather: tool({
    description: "Get current weather for a city",
    parameters: z.object({
      city: z.string().describe("City name, e.g. Paris"),
      units: z.enum(["c","f"]).default("c"),
    }),
    execute: async ({ city, units }) => {
      // … real fetch to a weather API …
      return { city, units, tempC: 21, condition: "sunny" };
    },
  }),
  ragSearch: tool({
    description: "Search the company knowledge base",
    parameters: z.object({ query: z.string(), k: z.number().int().default(5) }),
    execute: async ({ query, k }) => {
      // … call your retriever (M30) over HTTP/gRPC (M45) …
      return { hits: [/* ... */] };
    },
  }),
};

export async function POST(req: Request) {
  const { messages } = await req.json();
  const result = await streamText({
    model: provider("gpt-4o-mini"),
    messages, tools, maxSteps: 5,        // multi-step tool use
  });
  return result.toDataStreamResponse();
}
'''
print(ts_tools)


# %% [markdown] color=mint title="Zod is the killer.** One schema is"
# # Zod is the killer.** One schema is
#
# **Zod is the killer.** One schema is:
# - the **runtime validator** for the model's tool call,
# - the **TS type** of the `execute` arguments,
# - the **JSON schema** sent to the LLM,
# - the **prompt description** (`.describe(...)`).
#
# This eliminates the entire "the model invented a field" failure class — bad calls are rejected before your `execute` runs.


# %% [markdown] color=peach title="8 · Structured outputs — `streamObject`"
# # 8 · Structured outputs — `streamObject`
#
# Often you don't want chat — you want **a typed JSON object**. The SDK streams it as it's produced so the UI can show partial state.


# %% color=violet title="ts_obj = '''import { streamObject } from 'ai'"
# @explain: Run this cell to see the output.
ts_obj = '''import { streamObject } from "ai";
import { z } from "zod";

const Schema = z.object({
  title: z.string(),
  bullets: z.array(z.string()).min(3).max(5),
  confidence: z.number().min(0).max(1),
});

const { partialObjectStream } = await streamObject({
  model: provider("gpt-4o-mini"),
  schema: Schema,
  prompt: "Summarise the latest paper on PagedAttention.",
});

for await (const partial of partialObjectStream) {
  console.log(partial);   // shows the object filling in field by field
}
'''
print(ts_obj)


# %% [markdown] color=amber title="Internally this uses the model's…"
# # Internally this uses the model's…
#
# Internally this uses the model's grammar-constrained JSON mode (M38). Combined with `useObject()` on the React side, you can render forms / cards that fill themselves in live as the model streams.


# %% [markdown] color=rose title="9 · Edge runtimes"
# # 9 · Edge runtimes
#
# | Runtime | What's special |
# |---|---|
# | **Vercel Edge** | global region, V8 isolates, ~5 ms cold start, full Vercel AI SDK support |
# | **Cloudflare Workers** | similar; bundles to ~1 MB; **AI Gateway** + **Workers AI** native |
# | **Bun** | server-side, faster than Node, native `Bun.serve` HTTP, drop-in Node compat |
# | **Deno / Deno Deploy** | TS-first runtime; clean stdlib; Deno KV |
# …


# %% [markdown] color=lime title="10 · Production checklist"
# # 10 · Production checklist
#
# | Concern | Implementation |
# |---|---|
# | **Auth** | Auth.js / Clerk / Lucia for sessions; check user before every LLM call |
# | **Rate limiting** | Upstash Redis (sliding window — same recipe as M37) keyed by user id |
# | **Abuse / prompt injection** | strip user-controlled HTML, cap message length, watchlist patterns |
# | **Telemetry** | OTel SDK for browsers + edge → Collector (M51) → Langfuse / Datadog |
# …


# %% [markdown] color=teal title="🎓 The whole arc — what you've built across 54 modules"
# # 🎓 The whole arc — what you've built across 54 modules
#
# ```
# M1-M5     Python · Pandas · NumPy · Plotting · SQL fundamentals
# M6-M15    Stats · classical ML · evaluation · feature engineering · MLOps basics
# M16-M24   PyTorch · transformers from scratch · diffusion · time-series · math + DeepSeek-V3 internals
# M25-M27   Pydantic · LangChain · Chroma RAG starter
# M28-M31   FastAPI · serving · vector DBs · advanced RAG
# …


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


