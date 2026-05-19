import { useEffect, useRef, useState } from "react";
import { useStore } from "../store";

type Point = { x: number; y: number };
type InkTool = "pen" | "highlighter" | "fixedPen";
type Stroke = { points: Point[]; tool: InkTool; bornAt: number };

/**
 * Three presenter ink tools:
 *
 *   - **pen**       Thin red ink that fades in ~1.4s. Quick gesture
 *                   that vanishes by the time the audience's eye
 *                   follows. Good for "look here".
 *   - **highlighter** Thick translucent yellow that lingers ~4s.
 *                   Useful for slightly-longer emphasis.
 *   - **fixedPen**  Same red ink as pen, but the stroke STAYS until
 *                   you press the eraser button (🧽) or leave
 *                   presentation. Use for diagrams, longer
 *                   annotations, math written on top of the slide.
 *
 * Strokes auto-clear whenever the user leaves presentation mode OR
 * the presenter "erase all" button is pressed (which bumps
 * `presenterInkClearCounter` in the store).
 */
const STYLES: Record<InkTool, { color: string; width: number; fade: number }> = {
  pen:         { color: "rgba(255, 70, 70, 0.95)",  width: 5,  fade: 1400    },
  highlighter: { color: "rgba(255, 220, 0, 0.45)",  width: 16, fade: 4000    },
  fixedPen:    { color: "rgba(255, 70, 70, 0.95)",  width: 5,  fade: Infinity },
};

export function PresenterOverlay() {
  const presenting = useStore((s) => s.presenting);
  const tool = useStore((s) => s.presenterTool);
  const clearCounter = useStore((s) => s.presenterInkClearCounter);

  const [strokes, setStrokes] = useState<Stroke[]>([]);
  const [current, setCurrent] = useState<{ points: Point[]; tool: InkTool } | null>(null);
  const rafRef = useRef<number | null>(null);

  // Cursor classes for active tools.
  useEffect(() => {
    const root = document.documentElement;
    root.classList.toggle("highlighter-active", presenting && tool === "highlighter");
    root.classList.toggle("pen-active", presenting && (tool === "pen" || tool === "fixedPen"));
  }, [presenting, tool]);

  // Wipe when leaving presentation.
  useEffect(() => {
    if (!presenting) {
      setStrokes([]);
      setCurrent(null);
    }
  }, [presenting]);

  // Wipe on every "erase all" click.
  useEffect(() => {
    if (clearCounter === 0) return;
    setStrokes([]);
    setCurrent(null);
  }, [clearCounter]);

  // Fade loop — strokes with fade=Infinity are never dropped.
  useEffect(() => {
    if (!presenting || (!strokes.length && !current)) return;
    let alive = true;
    const tick = () => {
      if (!alive) return;
      const now = Date.now();
      setStrokes((all) =>
        all.filter((s) => {
          const fade = STYLES[s.tool].fade;
          if (!isFinite(fade)) return true;          // fixedPen: keep forever
          return now - s.bornAt < fade;
        })
      );
      rafRef.current = requestAnimationFrame(tick);
    };
    rafRef.current = requestAnimationFrame(tick);
    return () => {
      alive = false;
      if (rafRef.current != null) cancelAnimationFrame(rafRef.current);
    };
  }, [presenting, strokes.length, current]);

  const isDrawTool = tool === "pen" || tool === "highlighter" || tool === "fixedPen";

  const startDraw = (e: React.PointerEvent) => {
    if (!isDrawTool) return;
    e.preventDefault();
    setCurrent({ points: [{ x: e.clientX, y: e.clientY }], tool });
    (e.target as Element).setPointerCapture?.(e.pointerId);
  };
  const moveDraw = (e: React.PointerEvent) => {
    if (!isDrawTool || !current) return;
    setCurrent({ ...current, points: [...current.points, { x: e.clientX, y: e.clientY }] });
  };
  const endDraw = () => {
    if (!current) return;
    if (current.points.length > 1) {
      setStrokes((s) => [
        ...s,
        { points: current.points, tool: current.tool, bornAt: Date.now() },
      ]);
    }
    setCurrent(null);
  };

  if (!presenting) return null;

  const now = Date.now();
  return (
    <svg
      style={{
        position: "fixed",
        inset: 0,
        width: "100vw",
        height: "100vh",
        pointerEvents: isDrawTool ? "auto" : "none",
        zIndex: 25,
      }}
      onPointerDown={startDraw}
      onPointerMove={moveDraw}
      onPointerUp={endDraw}
      onPointerCancel={endDraw}
    >
      {strokes.map((s, i) => {
        const cfg = STYLES[s.tool];
        const opacity = isFinite(cfg.fade)
          ? Math.max(0, 1 - (now - s.bornAt) / cfg.fade)
          : 1;
        return (
          <polyline
            key={i}
            points={s.points.map((p) => `${p.x},${p.y}`).join(" ")}
            stroke={cfg.color}
            strokeWidth={cfg.width}
            strokeLinecap="round"
            strokeLinejoin="round"
            fill="none"
            opacity={opacity}
          />
        );
      })}
      {current && current.points.length > 1 && (
        <polyline
          points={current.points.map((p) => `${p.x},${p.y}`).join(" ")}
          stroke={STYLES[current.tool].color}
          strokeWidth={STYLES[current.tool].width}
          strokeLinecap="round"
          strokeLinejoin="round"
          fill="none"
        />
      )}
    </svg>
  );
}
