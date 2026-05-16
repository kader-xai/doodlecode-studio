import type { CellMeta, ExecuteResponse, ExplainResponse, Notebook } from "./types";

const BASE = "/api";

export async function executeCode(code: string, sessionId = "default"): Promise<ExecuteResponse> {
  const r = await fetch(`${BASE}/execute`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ code, session_id: sessionId }),
  });
  if (!r.ok) throw new Error(`execute ${r.status}`);
  return r.json();
}

export async function explainCode(
  code: string,
  mode = "beginner",
  meta?: CellMeta | null
): Promise<ExplainResponse> {
  const r = await fetch(`${BASE}/explain`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ code, mode, meta: meta ?? null }),
  });
  if (!r.ok) throw new Error(`explain ${r.status}`);
  return r.json();
}

export async function uploadNotebook(file: File): Promise<Notebook> {
  const fd = new FormData();
  fd.append("file", file);
  const r = await fetch(`${BASE}/upload`, { method: "POST", body: fd });
  if (!r.ok) throw new Error(`upload ${r.status}`);
  return r.json();
}

export async function resetKernel(sessionId = "default"): Promise<void> {
  await fetch(`${BASE}/reset?session_id=${encodeURIComponent(sessionId)}`, { method: "POST" });
}

export async function exportNotebook(nb: Notebook): Promise<string> {
  const r = await fetch(`${BASE}/export`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(nb),
  });
  if (!r.ok) throw new Error(`export ${r.status}`);
  return r.text();
}

export type InstallResult = {
  ok: boolean;
  packages: string[];
  stdout: string;
  stderr: string;
  returncode: number;
};

export async function installPackages(
  packages: string,
  upgrade = false
): Promise<InstallResult> {
  const r = await fetch(`${BASE}/install`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ packages, upgrade }),
  });
  if (!r.ok) {
    const detail = await r.text();
    throw new Error(`install ${r.status}: ${detail}`);
  }
  return r.json();
}

export async function autosaveNotebook(nb: Notebook): Promise<{ path: string }> {
  const r = await fetch(`${BASE}/autosave`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(nb),
  });
  if (!r.ok) throw new Error(`autosave ${r.status}`);
  return r.json();
}
