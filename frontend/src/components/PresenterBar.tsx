import { useEffect, useCallback } from "react";
import { useStore } from "../store";

export function PresenterBar() {
  const presenting = useStore((s) => s.presenting);
  const cells = useStore((s) => s.notebook.cells);
  const focused = useStore((s) => s.focusedCellId);
  const focus = useStore((s) => s.focus);

  const idx = Math.max(0, cells.findIndex((c) => c.id === focused));

  const goTo = useCallback(
    (i: number) => {
      const next = Math.max(0, Math.min(cells.length - 1, i));
      const target = cells[next];
      if (target) focus(target.id);
    },
    [cells, focus]
  );

  // Keyboard nav while presenting. ArrowRight / ArrowLeft step cells.
  // Up/Down/Space-without-shift are swallowed so the canvas never scrolls.
  useEffect(() => {
    if (!presenting) return;
    const onKey = (e: KeyboardEvent) => {
      const tag = (e.target as HTMLElement | null)?.tagName?.toLowerCase();
      const inEditor = tag === "input" || tag === "textarea" || tag === "select";
      if (inEditor) return;

      // Hard block: up/down/page do nothing in presentation.
      if (
        e.key === "ArrowUp" ||
        e.key === "ArrowDown" ||
        e.key === "PageDown" ||
        e.key === "PageUp"
      ) {
        e.preventDefault();
        e.stopPropagation();
      }

      // Advance ONLY on right-arrow, space, or the Next button.
      if (e.key === "ArrowRight" || e.key === " ") {
        e.preventDefault();
        e.stopPropagation();
        goTo(idx + 1);
      } else if (e.key === "ArrowLeft") {
        e.preventDefault();
        e.stopPropagation();
        goTo(idx - 1);
      } else if (e.key === "Home") {
        e.preventDefault();
        goTo(0);
      } else if (e.key === "End") {
        e.preventDefault();
        goTo(cells.length - 1);
      } else if (e.key === "Escape") {
        useStore.getState().setPresenting(false);
      }
    };
    // Capture phase so we beat ReactFlow's own listeners.
    window.addEventListener("keydown", onKey, true);
    return () => window.removeEventListener("keydown", onKey, true);
  }, [presenting, idx, goTo, cells.length]);

  if (!presenting) return null;
  return (
    <div className="absolute bottom-4 left-1/2 -translate-x-1/2 z-30 flex items-center gap-2 bg-white/95 dark:bg-[#1f2228]/95 border-2 border-ink dark:border-white/70 rounded-2xl px-3 py-2 shadow-sketch">
      <button className="btn-sketch sky" onClick={() => goTo(idx - 1)} title="← / PageUp">
        ◀ Prev
      </button>
      <div className="font-hand text-2xl px-2 select-none">
        Slide {idx + 1} / {cells.length}
      </div>
      <button className="btn-sketch mint" onClick={() => goTo(idx + 1)} title="→ / Space / PageDown">
        Next ▶
      </button>
      <div className="font-hand text-base ml-2 text-ink/60 dark:text-white/60 select-none">
        ← → · Esc to exit
      </div>
    </div>
  );
}
