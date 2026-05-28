import { useStore } from "../store";

/**
 * Bottom-center bar shown only during presentation.
 * Prev / slide-counter / Next / Exit. Keyboard handlers in App.tsx
 * cover the same actions; this bar is for click-only audiences and
 * for discoverability.
 */
export function PresenterBar() {
  const presenting = useStore((s) => s.presenting);
  const setPresenting = useStore((s) => s.setPresenting);
  const focusedCellId = useStore((s) => s.focusedCellId);
  const nextCell = useStore((s) => s.nextCell);
  const prevCell = useStore((s) => s.prevCell);
  const ordered = useStore((s) => s.cellsInOrder());
  const tool = useStore((s) => s.presenterTool);
  const setTool = useStore((s) => s.setPresenterTool);
  const clearInk = useStore((s) => s.clearPresenterInk);
  const fullscreen = useStore((s) => s.fullscreen);
  const cells = useStore((s) => s.cells);
  const runCell = useStore((s) => s.runCell);

  const focusedIsCode =
    !!focusedCellId && cells.find((c) => c.id === focusedCellId)?.kind === "code";

  const toggleFullscreen = () => {
    try {
      if (document.fullscreenElement) {
        const p = document.exitFullscreen?.();
        if (p && typeof p.catch === "function") p.catch(() => {});
      } else {
        const p = document.documentElement.requestFullscreen?.();
        if (p && typeof p.catch === "function") p.catch(() => {});
      }
    } catch { /* ignore */ }
  };

  if (!presenting) return null;
  const toolBtn = (active: boolean) =>
    `w-9 h-9 rounded-md border-2 font-hand text-lg transition ${
      active
        ? "bg-marker-yellow border-ink dark:bg-amber-700 dark:border-white text-ink dark:text-white shadow-sketch"
        : "bg-white/80 dark:bg-[#262a31] border-ink/40 dark:border-white/40 text-ink dark:text-white hover:translate-y-[1px]"
    }`;
  const idx = Math.max(0, ordered.findIndex((c) => c.id === focusedCellId));
  const total = ordered.length;

  return (
    <div
      className="fixed bottom-4 left-1/2 -translate-x-1/2 z-40 pointer-events-auto
                 flex items-center gap-2 px-3 py-2 rounded-2xl border-2 border-ink dark:border-white/60
                 bg-white/90 dark:bg-[#1f2228]/95 shadow-sketch font-hand text-lg"
    >
      <button
        onClick={prevCell}
        title="Previous (← / PageUp)"
        className="px-3 py-0.5 rounded-lg border-2 border-ink dark:border-white/70 bg-marker-sky dark:bg-[#1864ab] text-ink dark:text-white shadow-sketch hover:translate-y-[1px] transition disabled:opacity-40"
        disabled={idx <= 0}
      >
        ◀ Prev
      </button>
      <span className="px-2 select-none text-ink dark:text-white">
        Slide {total ? idx + 1 : 0} / {total}
      </span>
      <button
        onClick={nextCell}
        title="Next (→ / Space / PageDown)"
        className="px-3 py-0.5 rounded-lg border-2 border-ink dark:border-white/70 bg-marker-mint dark:bg-[#2b8a3e] text-ink dark:text-white shadow-sketch hover:translate-y-[1px] transition disabled:opacity-40"
        disabled={idx >= total - 1}
      >
        Next ▶
      </button>
      <span className="mx-1 h-5 w-px bg-ink/30 dark:bg-white/30" />

      {/* Ink tools — click to toggle. Active tool highlights yellow. */}
      <button
        className={toolBtn(tool === "pen")}
        onClick={() => setTool(tool === "pen" ? "none" : "pen")}
        title="Pen (P) — red ink, fades ~1.4s"
      >
        ✒️
      </button>
      <button
        className={toolBtn(tool === "highlighter")}
        onClick={() => setTool(tool === "highlighter" ? "none" : "highlighter")}
        title="Highlighter (H) — yellow ink, fades ~4s"
      >
        🖍
      </button>
      <button
        className={toolBtn(tool === "fixedPen")}
        onClick={() => setTool(tool === "fixedPen" ? "none" : "fixedPen")}
        title="Fixed pen (X) — red ink that stays until erased"
      >
        🖊
      </button>
      <button
        className={toolBtn(false)}
        onClick={clearInk}
        title="Erase all ink (E)"
      >
        🧽
      </button>

      <span className="mx-1 h-5 w-px bg-ink/30 dark:bg-white/30" />

      {/* Run focused code cell. Only meaningful when a code cell is
       *  the current slide — disabled otherwise. */}
      <button
        onClick={() => focusedCellId && runCell(focusedCellId)}
        disabled={!focusedIsCode}
        title={focusedIsCode ? "Run this code cell (R)" : "Focus a code cell first"}
        className="px-3 py-0.5 rounded-lg border-2 border-ink dark:border-white/70 bg-marker-mint dark:bg-[#2b8a3e] text-ink dark:text-white shadow-sketch hover:translate-y-[1px] transition disabled:opacity-40 disabled:cursor-not-allowed"
      >
        ▶ Run
      </button>
      <button
        onClick={toggleFullscreen}
        title="Toggle fullscreen (F)"
        className={`w-9 h-9 rounded-md border-2 font-hand text-lg transition ${
          fullscreen
            ? "bg-marker-yellow border-ink dark:bg-amber-700 dark:border-white text-ink dark:text-white shadow-sketch"
            : "bg-white/80 dark:bg-[#262a31] border-ink/40 dark:border-white/40 text-ink dark:text-white hover:translate-y-[1px]"
        }`}
      >
        ⛶
      </button>

      <span className="mx-1 h-5 w-px bg-ink/30 dark:bg-white/30" />
      <button
        onClick={() => setPresenting(false)}
        title="Exit presentation (Esc / F5 / Shift+P)"
        className="px-3 py-0.5 rounded-lg border-2 border-ink dark:border-white/70 bg-marker-pink dark:bg-[#a61e4d] text-ink dark:text-white shadow-sketch hover:translate-y-[1px] transition"
      >
        ✕ Exit
      </button>
    </div>
  );
}
