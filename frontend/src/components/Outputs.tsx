import { useState } from "react";
import type { ExecuteResponse } from "../types";
import { installPackages } from "../api";
import { useStore } from "../store";

const ANSI_RE = /\x1b\[[0-9;]*m/g;

const MOD_NOT_FOUND_RE = /No module named ['"]([^'"]+)['"]/;
const PEP_REMAP: Record<string, string> = {
  cv2: "opencv-python",
  PIL: "pillow",
  sklearn: "scikit-learn",
  yaml: "pyyaml",
  bs4: "beautifulsoup4",
};

function detectMissingModule(text: string): string | null {
  const m = text.match(MOD_NOT_FOUND_RE);
  if (!m) return null;
  const root = m[1].split(".")[0];
  return PEP_REMAP[root] ?? root;
}

function InstallChip({ pkg, onDone }: { pkg: string; onDone: () => void }) {
  const [state, setState] = useState<"idle" | "busy" | "ok" | "err">("idle");
  const setInstalling = useStore((s) => s.setInstalling);
  const run = async (e: React.MouseEvent) => {
    e.stopPropagation();
    setState("busy");
    setInstalling({ packages: pkg, log: "" });
    try {
      const r = await installPackages(pkg, false);
      setState(r.ok ? "ok" : "err");
      if (r.ok) onDone();
    } catch {
      setState("err");
    } finally {
      setInstalling(null);
    }
  };
  return (
    <button
      onClick={run}
      disabled={state === "busy"}
      className="mb-2 font-hand text-base px-2 py-0.5 rounded-lg border-2 border-ink dark:border-white/70 bg-[#d0bfff] dark:bg-[#553aa8] hover:translate-x-[1px] hover:translate-y-[1px] transition"
    >
      {state === "idle" && <>📦 Install <span className="font-mono">{pkg}</span></>}
      {state === "busy" && <>installing {pkg}…</>}
      {state === "ok" && <>✅ installed — re-run the cell</>}
      {state === "err" && <>❌ install failed (open 📦 Install for details)</>}
    </button>
  );
}

// Color hint per output kind. Used as a subtle left-edge stripe so viewers
// still get a visual cue (stdout vs error vs result) without verbose labels.
function stripeColor(o: { type: string; name?: string }, dark: boolean): string {
  if (o.type === "error") return dark ? "#9a3505" : "#ffa94d";
  if (o.type === "stream" && o.name === "stderr") return dark ? "#a3201f" : "#ffc9c9";
  if (o.type === "stream") return dark ? "#1864ab" : "#a5d8ff";
  if (o.type === "result") return dark ? "#1e6b34" : "#b2f2bb";
  if (o.type === "display") return dark ? "#553aa8" : "#d0bfff";
  return dark ? "#444" : "#ccc";
}

export function Outputs({ result }: { result?: ExecuteResponse }) {
  const dark = useStore((s) => s.theme === "dark");
  if (!result) return null;
  const empty = result.outputs.length === 0;

  return (
    <div className="mt-2 nodrag">
      {/* One label, one box. */}
      <div className="font-hand text-lg text-ink/80 dark:text-white/80 mb-1 flex items-center gap-2">
        ↳ output
        {result.status === "error" && (
          <span className="font-mono text-xs px-1.5 rounded bg-[#ff8787] text-white">error</span>
        )}
      </div>

      <div className="nowheel max-h-[28rem] overflow-auto rounded-xl border-2 border-ink/70 dark:border-white/40 bg-white dark:bg-[#11141a] p-2 space-y-1.5">
        {empty && (
          <div className="px-2 py-1 font-hand text-lg italic text-ink/50 dark:text-white/50">
            (no output)
          </div>
        )}
        {result.outputs.map((o, i) => {
          const stripe = stripeColor(o, dark);
          const baseCls =
            "rounded-md overflow-hidden border border-ink/20 dark:border-white/15 bg-stone-50 dark:bg-[#171a21]";

          if (o.type === "stream") {
            const text = (o.text ?? "").replace(ANSI_RE, "");
            return (
              <div key={i} className={baseCls} style={{ borderLeft: `5px solid ${stripe}` }}>
                <pre className="whitespace-pre-wrap font-mono text-[13px] leading-relaxed text-ink dark:text-stone-100 px-2 py-1 m-0">
                  {text}
                </pre>
              </div>
            );
          }

          if (o.type === "result" || o.type === "display") {
            const data = o.data ?? {};
            if (data["image/png"]) {
              return (
                <div key={i} className={baseCls} style={{ borderLeft: `5px solid ${stripe}` }}>
                  <img
                    alt="output"
                    src={`data:image/png;base64,${data["image/png"]}`}
                    className="max-w-full block"
                  />
                </div>
              );
            }
            if (data["text/html"]) {
              return (
                <div
                  key={i}
                  className={baseCls + " px-2 py-1"}
                  style={{ borderLeft: `5px solid ${stripe}` }}
                >
                  <div
                    className="prose prose-sm max-w-none dark:prose-invert"
                    dangerouslySetInnerHTML={{ __html: data["text/html"] }}
                  />
                </div>
              );
            }
            return (
              <div key={i} className={baseCls} style={{ borderLeft: `5px solid ${stripe}` }}>
                <pre className="whitespace-pre-wrap font-mono text-[13px] leading-relaxed text-ink dark:text-stone-100 px-2 py-1 m-0">
                  {(data["text/plain"] ?? "").replace(ANSI_RE, "")}
                </pre>
              </div>
            );
          }

          if (o.type === "error") {
            const tb = (o.traceback ?? []).join("\n").replace(ANSI_RE, "");
            const missing = detectMissingModule(`${o.evalue ?? ""} ${tb}`);
            return (
              <div
                key={i}
                className="rounded-md overflow-hidden border-2 border-[#d9480f] bg-[#fff4e6] dark:bg-[#321b08] px-2 py-1"
                style={{ borderLeft: `5px solid ${stripe}` }}
              >
                {missing && <InstallChip pkg={missing} onDone={() => {}} />}
                <pre className="whitespace-pre-wrap font-mono text-[13px] leading-relaxed m-0 text-[#a3360a] dark:text-[#ffd9b4]">
                  {`${o.ename ?? "Error"}: ${o.evalue ?? ""}\n${tb}`}
                </pre>
              </div>
            );
          }

          return null;
        })}
      </div>
    </div>
  );
}
