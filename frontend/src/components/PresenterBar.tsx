import { useEffect, useCallback, useState } from "react";
import { useStore } from "../store";
import { splitSteps } from "./DiagramNode";

export function PresenterBar() {
  const presenting = useStore((s) => s.presenting);
  const cells = useStore((s) => s.notebook.cells);
  const focused = useStore((s) => s.focusedCellId);
  const focus = useStore((s) => s.focus);
  const tool = useStore((s) => s.presenterTool);
  const setTool = useStore((s) => s.setPresenterTool);
  const fullscreen = useStore((s) => s.fullscreen);

  // Auto-hide the bar when fullscreen + mouse has been idle for 2.5 s.
  // Any mouse-move re-shows it (and resets the idle timer).
  const [visible, setVisible] = useState(true);
  useEffect(() => {
    if (!fullscreen || !presenting) {
      setVisible(true);
      return;
    }
    let timer: number | undefined;
    const reveal = () => {
      setVisible(true);
      if (timer) window.clearTimeout(timer);
      timer = window.setTimeout(() => setVisible(false), 2500);
    };
    reveal();
    window.addEventListener("mousemove", reveal);
    window.addEventListener("touchstart", reveal);
    return () => {
      window.removeEventListener("mousemove", reveal);
      window.removeEventListener("touchstart", reveal);
      if (timer) window.clearTimeout(timer);
    };
  }, [fullscreen, presenting]);

  const toggleFullscreen = useCallback(() => {
    try {
      if (document.fullscreenElement) {
        const p = document.exitFullscreen?.();
        if (p && typeof p.catch === "function") p.catch(() => {});
      } else {
        const el = document.documentElement;
        const p = el.requestFullscreen?.();
        if (p && typeof p.catch === "function") p.catch(() => {});
      }
    } catch {
      // Some browsers throw synchronously when called outside a user
      // gesture or when the API is unavailable — swallow to avoid the
      // ErrorBoundary catching it.
    }
  }, []);

  const idx = Math.max(0, cells.findIndex((c) => c.id === focused));

  const goTo = useCallback(
    (i: number) => {
      const next = Math.max(0, Math.min(cells.length - 1, i));
      const target = cells[next];
      if (target) {
        focus(target.id);
        // Reset any diagram step counter when we land on a diagram
        // slide so the deck always starts at step 1 of N.
        if (target.meta?.cell_type === "diagram") {
          useStore.getState().resetDiagramStep(target.id);
        }
      }
    },
    [cells, focus]
  );

  useEffect(() => {
    if (!presenting) return;
    const onKey = (e: KeyboardEvent) => {
      const tag = (e.target as HTMLElement | null)?.tagName?.toLowerCase();
      const inEditor = tag === "input" || tag === "textarea" || tag === "select";
      if (inEditor) return;

      if (
        e.key === "ArrowUp" ||
        e.key === "ArrowDown" ||
        e.key === "PageDown" ||
        e.key === "PageUp"
      ) {
        e.preventDefault();
        e.stopPropagation();
      }

      if (e.key === "ArrowRight" || e.key === " ") {
        e.preventDefault();
        e.stopPropagation();
        // Diagram cells with multi-step sources: advance the step
        // first. Only when we've shown the last step does → move on
        // to the next slide.
        const current = cells[idx];
        if (current?.meta?.cell_type === "diagram") {
          const total = splitSteps(current.source || "").length;
          if (total > 1) {
            const advanced = useStore.getState().advanceDiagramStep(current.id, total);
            if (advanced) return;
          }
        }
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
      } else if (e.key === "p" || e.key === "P") {
        setTool(tool === "pen" ? "none" : "pen");
      } else if (e.key === "h" || e.key === "H") {
        setTool(tool === "highlighter" ? "none" : "highlighter");
      } else if (e.key === "x" || e.key === "X") {
        setTool(tool === "fixedPen" ? "none" : "fixedPen");
      } else if (e.key === "e" || e.key === "E") {
        useStore.getState().clearPresenterInk();
      } else if (e.key === "f" || e.key === "F") {
        toggleFullscreen();
      }
    };
    window.addEventListener("keydown", onKey, true);
    return () => window.removeEventListener("keydown", onKey, true);
  }, [presenting, idx, goTo, cells.length, setTool, tool]);

  if (!presenting) return null;

  const toolBtn = (active: boolean) =>
    `font-hand text-lg w-10 h-10 rounded-lg border-2 transition ${
      active
        ? "bg-marker-yellow border-ink dark:bg-amber-700 dark:border-white text-ink dark:text-white shadow-sketch"
        : "bg-white/70 dark:bg-[#1f2228] border-ink/40 dark:border-white/40 text-ink/70 dark:text-white/70"
    }`;

  return (
    <div
      className="absolute bottom-4 left-1/2 -translate-x-1/2 z-30 flex items-center gap-2 bg-white/95 dark:bg-[#1f2228]/95 border-2 border-ink dark:border-white/70 rounded-2xl px-3 py-2 shadow-sketch transition-opacity duration-300"
      style={{
        opacity: visible ? 1 : 0,
        pointerEvents: visible ? "auto" : "none",
      }}
      onMouseEnter={() => setVisible(true)}
    >
      <button className="btn-sketch sky" onClick={() => goTo(idx - 1)} title="← / PageUp">
        ◀ Prev
      </button>
      <div className="font-hand text-2xl px-2 select-none text-ink dark:text-white">
        Slide {idx + 1} / {cells.length}
      </div>
      <button
        className="btn-sketch mint"
        onClick={() => {
          const current = cells[idx];
          if (current?.meta?.cell_type === "diagram") {
            const total = splitSteps(current.source || "").length;
            if (total > 1) {
              const advanced = useStore.getState().advanceDiagramStep(current.id, total);
              if (advanced) return;
            }
          }
          goTo(idx + 1);
        }}
        title="→ / Space / PageDown"
      >
        Next ▶
      </button>

      {/* Presenter ink tools — fading pen + highlighter + fixed pen + erase-all */}
      <div className="ml-2 flex gap-1 border-l-2 border-ink/30 dark:border-white/30 pl-2">
        <button
          className={toolBtn(tool === "pen")}
          onClick={() => setTool(tool === "pen" ? "none" : "pen")}
          title="Pen — quick red strokes that fade in ~1.5s (P)"
        >
          ✒️
        </button>
        <button
          className={toolBtn(tool === "highlighter")}
          onClick={() => setTool(tool === "highlighter" ? "none" : "highlighter")}
          title="Highlighter — yellow strokes that fade in ~4s (H)"
        >
          🖍
        </button>
        <button
          className={toolBtn(tool === "fixedPen")}
          onClick={() => setTool(tool === "fixedPen" ? "none" : "fixedPen")}
          title="Fixed pen — red ink that stays until you erase (X)"
        >
          🖊
        </button>
        <button
          className={toolBtn(false)}
          onClick={() => useStore.getState().clearPresenterInk()}
          title="Erase all ink on the screen (E)"
        >
          🧽
        </button>
        <button
          className={toolBtn(fullscreen)}
          onClick={toggleFullscreen}
          title="Fullscreen — hide chrome, auto-fade this bar (F)"
        >
          ⛶
        </button>
      </div>

      <div className="font-hand text-base ml-2 text-ink/60 dark:text-white/60 select-none">
        ← → · P pen · H highlighter · X fixed · E erase · F fullscreen · Esc exit
      </div>
    </div>
  );
}
