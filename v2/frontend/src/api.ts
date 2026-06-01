import type { Cell, ExecuteResponse } from "./types";

export interface SaveResponse {
  text: string;
  format_version: number;
}

export interface OpenResponse {
  notebook: { name: string; cells: Cell[] };
  format_version: number;
}

/**
 * Tiny fetch wrapper. We deliberately don't pull in axios or react-query
 * — the API surface is small and these calls always live behind store
 * actions, so a couple of lines of `fetch` are clearer than the indirection.
 */
async function postJSON<T>(path: string, body: unknown): Promise<T> {
  const r = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!r.ok) {
    const text = await r.text().catch(() => "");
    throw new Error(`POST ${path} → HTTP ${r.status}: ${text || r.statusText}`);
  }
  return r.json() as Promise<T>;
}

export function executeCode(source: string, timeout_s = 15): Promise<ExecuteResponse> {
  return postJSON<ExecuteResponse>("/api/execute", { source, timeout_s });
}

export function saveNotebook(notebook: { name: string; cells: Cell[] }): Promise<SaveResponse> {
  return postJSON<SaveResponse>("/api/save", { notebook });
}

export function openNotebook(text: string): Promise<OpenResponse> {
  return postJSON<OpenResponse>("/api/open", { text });
}

export function exportMarkdown(notebook: { name: string; cells: Cell[] }): Promise<{ text: string }> {
  return postJSON<{ text: string }>("/api/export/markdown", { notebook });
}

export async function fetchDemo(): Promise<string> {
  const r = await fetch("/api/demo");
  if (!r.ok) throw new Error(`GET /api/demo → HTTP ${r.status}`);
  const j = (await r.json()) as { text: string };
  return j.text;
}

export async function resetKernel(): Promise<void> {
  const r = await fetch("/api/kernel/reset", { method: "POST" });
  if (!r.ok) throw new Error(`POST /api/kernel/reset → HTTP ${r.status}`);
}

/** Iter 44: SIGINT the running kernel — like Ctrl+C inside the
 *  user's exec(). Returns true iff a signal was actually delivered. */
export async function interruptKernel(): Promise<boolean> {
  const r = await fetch("/api/kernel/interrupt", { method: "POST" });
  if (!r.ok) throw new Error(`POST /api/kernel/interrupt → HTTP ${r.status}`);
  const j = (await r.json()) as { ok: boolean };
  return j.ok;
}

export interface InstallResponse {
  ok: boolean;
  elapsed_ms: number;
  output: string;
  packages: string[];
}
export function installPackages(packages: string): Promise<InstallResponse> {
  return postJSON<InstallResponse>("/api/install", { packages });
}
