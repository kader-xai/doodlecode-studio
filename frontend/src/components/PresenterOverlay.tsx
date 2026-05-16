import { useEffect, useRef, useState } from "react";
import { useStore } from "../store";

type Point = { x: number; y: number };
type Stroke = { points: Point[]; tool: "pen" | "highlighter"; bornAt: number };

/**
 * Two presenter ink tools, both Excalidraw-style:
 *
 *   - **pen**          Thin red ink that fades in ~1.4s. Draw a quick
 *                      circle around something and it vanishes by the
 *                      time the audience's eye follows.
 *   - **highlighter**  Thick translucent yellow ink that stays ~4s.
 *                      Good for stable annotations on a slide.
 *
 * While either tool is active the SVG captures pointer events so the
 * drag is registered. Otherwise the SVG is pointer-events:none so the
 * canvas keeps responding normally. z-index sits between the canvas
 * and the UI chrome so the presenter bar / modals stay clickable.
 */
const STYLES = {
  pen: { color: "rgba(255, 70, 70, 0.95)", width: 5, fade: 1400 },
  highlighter: { color: "rgba(255, 220, 0, 0.45)", width: 16, fade: 4000 },
} as const;

export function PresenterOverlay() {
  const presenting = useStore((s) => s.presenting);
  const tool = useStore((s) => s.presenterTool);

  const [strokes, setStrokes] = useState<Stroke[]>([]);
  const [current, setCurrent] = useState<{ points: Point[]; tool: "pen" | "highlighter" } | null>(
    null
  );
  const rafRef = useRef<number | null>(null);

  // CSS hook so the cursor reflects the active tool.
  useEffect(() => {
    const root = document.documentElement;
    root.classList.toggle("highlighter-active", presenting && tool === "highlighter");
    root.classList.toggle("pen-active", presenting && tool === "pen");
  }, [presenting, tool]);

  // Wipe ink when leaving presentation.
  useEffect(() => {
    if (!presenting) {
      setStrokes([]);
      setCurrent(null);
    }
  }, [presenting]);

  // Animation loop — fades strokes by age and drops them when fully
  // transparent. Idle when nothing's on screen.
  useEffect(() => {
    if (!presenting || (!strokes.length && !current)) return;
    let alive = true;
    const tick = () => {
      if (!alive) return;
      const now = Date.now();
      setStrokes((all) =>
        all.filter((s) => now - s.bornAt < STYLES[s.tool].fade)
      );
      rafRef.current = requestAnimationFrame(tick);
    };
    rafRef.current = requestAnimationFrame(tick);
    return () => {
      alive = false;
      if (rafRef.current != null) cancelAnimationFrame(rafRef.current);
    };
  }, [presenting, strokes.length, current]);

  const isDrawTool = tool === "pen" || tool === "highlighter";

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
        const age = now - s.bornAt;
        const opacity = Math.max(0, 1 - age / cfg.fade);
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
