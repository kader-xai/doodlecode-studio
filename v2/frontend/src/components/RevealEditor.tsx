import { useEffect, useState } from "react";
import { DoodleBorder } from "./DoodleBorder";
import { useStore } from "../store";

/**
 * Iter 155: singleton modal for authoring a code cell's reveal steps.
 *
 * The cell's `source` is the base (always shown first). Each step here
 * is an additional code fragment that the Reveal button types in BELOW
 * the current code during a talk — the program builds up
 * function-by-function. Run executes whatever is shown so far.
 *
 * Local-draft pattern (rule 10): edits live in `draft` and only commit
 * to the store on Save, so per-keystroke typing doesn't churn the
 * store / re-render the canvas.
 */
export function RevealEditor() {
  const cellId = useStore((s) => s.revealEditorCellId);
  const openRevealEditor = useStore((s) => s.openRevealEditor);
  const cell = useStore((s) => s.cells.find((c) => c.id === s.revealEditorCellId));
  const setReveals = useStore((s) => s.setReveals);

  const [draft, setDraft] = useState<string[]>([]);

  useEffect(() => {
    if (!cellId) return;
    setDraft(cell?.reveals && cell.reveals.length ? [...cell.reveals] : [""]);
  }, [cellId, cell]);

  useEffect(() => {
    if (!cellId) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.preventDefault();
        // Native window event — stop other window keydown listeners
        // (e.g. App's Esc cascade) from also firing.
        e.stopImmediatePropagation();
        openRevealEditor(null);
      } else if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
        e.preventDefault();
        save();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [cellId, draft]);

  if (!cellId || !cell) return null;

  const save = () => {
    setReveals(cellId, draft);
    openRevealEditor(null);
  };
  const cancel = () => openRevealEditor(null);

  const updateRow = (i: number, text: string) =>
    setDraft((d) => d.map((s, j) => (j === i ? text : s)));
  const removeRow = (i: number) => setDraft((d) => d.filter((_, j) => j !== i));
  const moveRow = (i: number, dir: -1 | 1) => {
    setDraft((d) => {
      const next = [...d];
      const j = i + dir;
      if (j < 0 || j >= next.length) return d;
      [next[i], next[j]] = [next[j], next[i]];
      return next;
    });
  };
  const addRow = () => setDraft((d) => [...d, ""]);

  return (
    <div
      className="fixed inset-0 z-[100] bg-black/40 backdrop-blur-sm flex items-center justify-center p-6"
      onClick={cancel}
    >
      <div
        className="relative max-w-2xl w-full max-h-[90vh] flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <DoodleBorder
          stroke="var(--doodle-stroke, #2a2a2a)"
          fill="var(--doodle-help-fill, #fff8e1)"
          strokeWidth={3}
          radius={18}
        />
        <div className="relative p-5 flex-1 overflow-hidden flex flex-col">
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-hand text-3xl">🎬 Reveal Steps</h2>
            <div className="flex gap-2">
              <button
                onClick={cancel}
                className="font-hand text-base px-3 py-0.5 rounded-lg border-2 border-ink dark:border-white/70 bg-white/80 dark:bg-[#1f2228] text-ink dark:text-white shadow-sketch hover:translate-y-[1px] transition"
              >
                Cancel
              </button>
              <button
                onClick={save}
                className="font-hand text-base px-3 py-0.5 rounded-lg border-2 border-ink dark:border-white/70 bg-marker-mint dark:bg-[#2b8a3e] text-ink dark:text-white shadow-sketch hover:translate-y-[1px] transition"
                title="Save (Cmd/Ctrl+Enter)"
              >
                ✓ Save
              </button>
            </div>
          </div>

          <p className="font-hand text-base text-ink/70 dark:text-white/70 mb-2">
            During a talk, each <b>Reveal</b> types the next step in
            below your code. Run executes whatever's shown.
          </p>

          {/* Base code preview — read-only reminder of what step 0 is. */}
          <div className="mb-3">
            <div className="font-hand text-sm text-ink/60 dark:text-white/60 mb-1">
              Base code (step 0 — shown first)
            </div>
            <pre className="font-mono text-xs leading-snug p-2 rounded border-2 border-ink/30 dark:border-white/20 bg-black/5 dark:bg-white/5 text-ink/80 dark:text-white/80 max-h-24 overflow-auto whitespace-pre-wrap">
              {cell.source || "(empty)"}
            </pre>
          </div>

          <div className="flex-1 overflow-auto pr-1 space-y-3">
            {draft.map((code, i) => (
              <div
                key={i}
                className="rounded-xl border-2 border-ink/30 dark:border-white/30 bg-white/60 dark:bg-black/30 p-2.5"
              >
                <div className="flex items-center justify-between mb-1.5">
                  <span className="font-hand text-base text-ink/80 dark:text-white/80">
                    Step {i + 1} / {draft.length}
                  </span>
                  <div className="flex gap-1 items-center">
                    <SmallBtn label="↑" title="Move up" onClick={() => moveRow(i, -1)} disabled={i === 0} />
                    <SmallBtn label="↓" title="Move down" onClick={() => moveRow(i, +1)} disabled={i === draft.length - 1} />
                    <SmallBtn label="🗑" title="Delete this step" onClick={() => removeRow(i)} />
                  </div>
                </div>
                <textarea
                  value={code}
                  onChange={(e) => updateRow(i, e.target.value)}
                  placeholder={"# code revealed at this step\ndef sigmoid(x):\n    return 1 / (1 + np.exp(-x))"}
                  spellCheck={false}
                  rows={5}
                  className="w-full font-mono text-sm leading-snug p-2 rounded border-2 border-ink/40 dark:border-white/30 bg-white dark:bg-[#1f2228] text-ink dark:text-white outline-none focus:border-[#c2255c] whitespace-pre"
                />
              </div>
            ))}
            <button
              onClick={addRow}
              className="font-hand text-lg px-3 py-1 rounded-lg border-2 border-dashed border-ink/40 dark:border-white/40 text-ink/70 dark:text-white/70 hover:bg-marker-yellow/40 dark:hover:bg-amber-700/30 transition w-full"
            >
              ＋ Add another step
            </button>
          </div>

          <p className="font-hand text-xs text-ink/50 dark:text-white/50 mt-2">
            Esc · Cancel · Cmd/Ctrl+Enter · Save
          </p>
        </div>
      </div>
    </div>
  );
}

function SmallBtn({
  label, title, onClick, disabled,
}: { label: string; title: string; onClick: () => void; disabled?: boolean }) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      title={title}
      className="font-hand text-sm w-7 h-7 rounded border-2 border-ink/50 dark:border-white/40 bg-white/90 dark:bg-[#262a31] text-ink dark:text-white hover:translate-y-[1px] transition disabled:opacity-30"
    >
      {label}
    </button>
  );
}
