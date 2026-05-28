import { useEffect, useRef, useState } from "react";
import { useStore } from "../store";

/**
 * Presenter ink overlay — three tools:
 *
 *   pen        Thin red, fades in ~1.4 s. Quick "look here" gesture.
 *   highlighter Thick yellow ~35% alpha, fades in ~4 s.
 *   fixedPen   Same red as pen, but STAYS until erased.
 *
 * Pattern (the one that actually works):
 *
 * 1. SVG floats `position: fixed` over the whole viewport. When a
 *    draw tool is active we set `pointer-events: auto` and
 *    `zIndex: 9999` so it captures clicks above iframes, Monaco,
 *    modals, everything. When idle we set `pointer-events: none` and
 *    drop to z-25 so the PresenterBar stays clickable.
 * 2. The active stroke is held in a REF. We paint points to local
 *    state for re-render, but the source-of-truth is the ref so a
 *    React batch delay can't drop points mid-drag.
 * 3. `setPointerCapture(e.pointerId)` on `e.currentTarget` (the SVG)
 *    keeps subsequent move events delivered to us even when the
 *    cursor leaves the original target. v1's bug was using
 *    `e.target` here — that targets a child element which may not
 *    have a pointer-capture API surface.
 * 4. `touchAction: "none"` so trackpad gestures don't try to pan/zoom
 *    the page while we're drawing.
 * 5. A RAF loop ticks every frame to fade old strokes. fixedPen has
 *    fade=Infinity so it never expires.
 * 6. On `presenting=false` or "erase all" we wipe everything.
 */
type Point = { x: number; y: number };
type InkTool = "pen" | "highlighter" | "fixedPen";
type Stroke = { points: Point[]; tool: InkTool; bornAt: number };

const STYLES: Record<InkTool, { color: string; width: number; fade: number }> = {
  pen:         { color: "rgba(255, 70, 70, 0.95)",  width: 5,  fade: 1400 },
  highlighter: { color: "rgba(255, 220, 0, 0.45)",  width: 16, fade: 4000 },
  fixedPen:    { color: "rgba(255, 70, 70, 0.95)",  width: 5,  fade: Infinity },
};

export function PresenterOverlay() {
  const presenting = useStore((s) => s.presenting);
  const tool = useStore((s) => s.presenterTool);
  const clearCounter = useStore((s) => s.presenterClearCounter);

  const [strokes, setStrokes] = useState<Stroke[]>([]);
  const [current, setCurrent] = useState<{ points: Point[]; tool: InkTool } | null>(null);
  const currentRef = useRef<{ points: Point[]; tool: InkTool } | null>(null);
  const rafRef = useRef<number | null>(null);

  // Wipe on presentation exit.
  useEffect(() => {
    if (!presenting) {
      setStrokes([]);
      setCurrent(null);
      currentRef.current = null;
    }
  }, [presenting]);

  // Wipe on "erase all".
  useEffect(() => {
    if (clearCounter === 0) return;
    setStrokes([]);
    setCurrent(null);
    currentRef.current = null;
  }, [clearCounter]);

  // CSS hook for cursor + child-pointer-events while drawing.
  useEffect(() => {
    const root = document.documentElement;
    const drawing = presenting && (tool === "pen" || tool === "highlighter" || tool === "fixedPen");
    root.classList.toggle("ink-active", drawing);
    root.classList.toggle("ink-highlighter", drawing && tool === "highlighter");
    root.classList.toggle("ink-pen", drawing && (tool === "pen" || tool === "fixedPen"));
  }, [presenting, tool]);

  // Fade loop. Drops strokes whose age > fade; fixedPen stays.
  useEffect(() => {
    if (!presenting || (!strokes.length && !current)) return;
    let alive = true;
    const tick = () => {
      if (!alive) return;
      const now = Date.now();
      setStrokes((all) =>
        all.filter((s) => {
          const f = STYLES[s.tool].fade;
          if (!isFinite(f)) return true;
          return now - s.bornAt < f;
        }),
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

  const startDraw = (e: React.PointerEvent<SVGSVGElement>) => {
    if (!isDrawTool) return;
    e.preventDefault();
    try { e.currentTarget.setPointerCapture(e.pointerId); } catch { /* ignore */ }
    const stroke = { points: [{ x: e.clientX, y: e.clientY }], tool };
    currentRef.current = stroke;
    setCurrent(stroke);
  };
  const moveDraw = (e: React.PointerEvent<SVGSVGElement>) => {
    if (!currentRef.current) return;
    e.preventDefault();
    currentRef.current.points.push({ x: e.clientX, y: e.clientY });
    setCurrent({ ...currentRef.current, points: currentRef.current.points.slice() });
  };
  const endDraw = (e?: React.PointerEvent<SVGSVGElement>) => {
    if (e) { try { e.currentTarget.releasePointerCapture(e.pointerId); } catch { /* ignore */ } }
    const stroke = currentRef.current;
    currentRef.current = null;
    if (stroke && stroke.points.length > 1) {
      setStrokes((s) => [...s, { points: stroke.points, tool: stroke.tool, bornAt: Date.now() }]);
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
        // Capture pointer events ONLY while a draw tool is active so
        // the PresenterBar etc. stay clickable when not drawing.
        pointerEvents: isDrawTool ? "auto" : "none",
        // Float above iframes/Monaco/modals when actively drawing.
        zIndex: isDrawTool ? 9999 : 25,
        touchAction: "none",
      }}
      onPointerDown={startDraw}
      onPointerMove={moveDraw}
      onPointerUp={endDraw}
      onPointerCancel={endDraw}
      onLostPointerCapture={endDraw}
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
