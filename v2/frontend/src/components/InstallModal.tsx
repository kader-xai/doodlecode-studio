import { useEffect, useRef, useState } from "react";
import { useFocusTrap } from "../lib/focusTrap";
import { installPackages } from "../api";
import { useStore } from "../store";
import { DoodleBorder } from "./DoodleBorder";

/**
 * Modal for running `pip install …` against the kernel's Python.
 *
 *   • Textarea accepts space- or newline-separated package specs
 *     (e.g. "numpy pandas matplotlib==3.8" or one per line).
 *   • Install button POSTs to /api/install. We show a spinner during,
 *     pip's combined stdout+stderr in a pre block when done.
 *   • On success the backend auto-resets the kernel so freshly-
 *     installed modules are importable from the next cell.
 *   • Esc / ✕ / click-outside closes — including mid-install, which
 *     just dismisses the UI (the install keeps running on the server).
 */
export function InstallModal() {
  const open = useStore((s) => s.installOpen);
  const setOpen = useStore((s) => s.setInstallOpen);

  const [pkgs, setPkgs] = useState("");
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<
    { ok: boolean; output: string; elapsed_ms: number } | null
  >(null);

  // Reset modal state on each open.
  useEffect(() => {
    if (open) {
      setPkgs("");
      setBusy(false);
      setResult(null);
    }
  }, [open]);

  // Esc closes.
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") { e.preventDefault(); setOpen(false); }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, setOpen]);

  const panelRef = useRef<HTMLDivElement>(null);
  useFocusTrap(open, panelRef);

  if (!open) return null;

  const run = async () => {
    if (!pkgs.trim()) return;
    setBusy(true);
    setResult(null);
    try {
      const r = await installPackages(pkgs);
      setResult({ ok: r.ok, output: r.output, elapsed_ms: r.elapsed_ms });
    } catch (err) {
      setResult({ ok: false, output: String(err), elapsed_ms: 0 });
    } finally {
      setBusy(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-[100] bg-black/40 backdrop-blur-sm flex items-center justify-center p-6"
      onClick={() => setOpen(false)}
    >
      <div
        ref={panelRef}
        className="relative max-w-2xl w-full max-h-[90vh] flex flex-col"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-label="Install Python packages"
      >
        <DoodleBorder
          stroke="var(--doodle-stroke, #2a2a2a)"
          fill="var(--doodle-help-fill, #fff8e1)"
          strokeWidth={3}
          radius={18}
        />
        <div className="relative p-5 flex-1 overflow-hidden flex flex-col">
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-hand text-3xl">📦 Install Python packages</h2>
            <button
              onClick={() => setOpen(false)}
              className="font-hand text-xl px-2 rounded-md border-2 border-ink dark:border-white/70 hover:translate-y-[1px] transition"
              title="Close (Esc)"
            >
              ✕
            </button>
          </div>

          <p className="font-hand text-base text-ink/70 dark:text-white/70 mb-2">
            One or many — space or newline separated. Version specs allowed
            (e.g. <code className="font-mono">numpy pandas matplotlib==3.8</code>).
          </p>

          <textarea
            value={pkgs}
            onChange={(e) => setPkgs(e.target.value)}
            onKeyDown={(e) => e.stopPropagation()}
            placeholder="numpy pandas matplotlib"
            spellCheck={false}
            rows={3}
            className="w-full font-mono text-sm leading-snug p-2 rounded-lg border-2 border-ink/40 dark:border-white/30 bg-white dark:bg-[#1f2228] text-ink dark:text-white outline-none focus:border-[#c2255c]"
            disabled={busy}
            autoFocus
          />

          <div className="mt-3 flex items-center gap-2">
            <button
              onClick={run}
              disabled={busy || !pkgs.trim()}
              className="font-hand text-lg px-4 py-1 rounded-lg border-2 border-ink dark:border-white/70 bg-marker-mint dark:bg-[#2b8a3e] text-ink dark:text-white shadow-sketch hover:translate-y-[1px] transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {busy ? "… installing" : "Install"}
            </button>
            {busy && (
              <span className="font-hand text-base text-ink/70 dark:text-white/70">
                pip is running — the kernel will reset automatically when done.
              </span>
            )}
            {result && (
              <span
                className={`font-hand text-base ${
                  result.ok
                    ? "text-[#2b8a3e] dark:text-[#b2f2bb]"
                    : "text-[#c2255c] dark:text-[#fcc2d7]"
                }`}
              >
                {result.ok ? "✓ installed" : "✗ failed"} · {result.elapsed_ms} ms
              </span>
            )}
          </div>

          {result && (
            <pre className="mt-3 flex-1 overflow-auto font-mono text-xs leading-relaxed p-2 rounded-lg border-2 border-ink/30 dark:border-white/30 bg-white dark:bg-[#1a1d23] text-ink dark:text-white whitespace-pre-wrap break-words">
              {result.output || "(no output)"}
            </pre>
          )}
        </div>
      </div>
    </div>
  );
}
