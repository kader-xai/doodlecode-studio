import { useEffect, useRef, useState } from "react";
import { DoodleBorder } from "./DoodleBorder";
import { useFocusTrap } from "../lib/focusTrap";
import { useStore } from "../store";

/**
 * Iter 165: singleton modal for a cell's presenter speaker note. Local
 * draft (rule 10) committed on Save. Esc/Cmd+Enter wired with
 * stopImmediatePropagation so the App Esc cascade doesn't also fire.
 */
export function NoteEditor() {
  const cellId = useStore((s) => s.noteEditorCellId);
  const openNoteEditor = useStore((s) => s.openNoteEditor);
  const cell = useStore((s) => s.cells.find((c) => c.id === s.noteEditorCellId));
  const setNote = useStore((s) => s.setNote);

  const [draft, setDraft] = useState("");
  const panelRef = useRef<HTMLDivElement>(null);
  useFocusTrap(!!cellId && !!cell, panelRef);

  useEffect(() => {
    if (!cellId) return;
    setDraft(cell?.note ?? "");
  }, [cellId, cell]);

  useEffect(() => {
    if (!cellId) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.preventDefault();
        e.stopImmediatePropagation();
        openNoteEditor(null);
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
    setNote(cellId, draft);
    openNoteEditor(null);
  };
  const cancel = () => openNoteEditor(null);

  return (
    <div
      className="fixed inset-0 z-[100] bg-black/40 backdrop-blur-sm flex items-center justify-center p-6"
      onClick={cancel}
    >
      <div
        ref={panelRef}
        className="relative max-w-xl w-full"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-label="Speaker note"
      >
        <DoodleBorder
          stroke="var(--doodle-stroke, #2a2a2a)"
          fill="var(--doodle-help-fill, #fff8e1)"
          strokeWidth={3}
          radius={18}
        />
        <div className="relative p-5">
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-hand text-3xl">📝 Speaker note</h2>
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
            Shown only to you (bottom-left) during presentation — never on
            the slide. Saved with the notebook.
          </p>
          <textarea
            autoFocus
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            placeholder={"What to say on this slide…\nPause here. Mention the benchmark."}
            spellCheck
            rows={6}
            className="w-full font-hand text-lg leading-snug p-2 rounded border-2 border-ink/40 dark:border-white/30 bg-white dark:bg-[#1f2228] text-ink dark:text-white outline-none focus:border-[#c2255c]"
          />
          <p className="font-hand text-xs text-ink/50 dark:text-white/50 mt-2">
            Esc · Cancel · Cmd/Ctrl+Enter · Save
          </p>
        </div>
      </div>
    </div>
  );
}
