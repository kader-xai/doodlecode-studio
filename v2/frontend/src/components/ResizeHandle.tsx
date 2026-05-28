import { useRef } from "react";
import { useStore } from "../store";

/**
 * Bottom-right corner resize grip.
 *
 * Uses pointer-capture so the drag survives even when the cursor leaves
 * the handle. Reports the new width/height in CANVAS pixels (not
 * screen pixels) by dividing by ReactFlow's current zoom — otherwise
 * resizing on a zoomed-out canvas would over-scale.
 *
 * `nodrag nowheel` keeps ReactFlow from hijacking the gesture.
 */
export function ResizeHandle({
  cellId,
  baseWidth,
  baseHeight,
}: {
  cellId: string;
  baseWidth: number;
  baseHeight: number;
}) {
  const resizeCell = useStore((s) => s.resizeCell);
  const startRef = useRef<{
    x: number;
    y: number;
    w: number;
    h: number;
    zoom: number;
  } | null>(null);

  const currentZoom = (): number => {
    // ReactFlow stores zoom on `.react-flow__viewport` via transform:
    // matrix(zoom,0,0,zoom,tx,ty). Parse it cheaply.
    const el = document.querySelector(".react-flow__viewport") as HTMLElement | null;
    if (!el) return 1;
    const m = window.getComputedStyle(el).transform;
    // matrix(a,b,c,d,e,f) — `a` is the X-scale (== zoom).
    const match = m.match(/matrix\(([^,]+),/);
    return match ? parseFloat(match[1]) || 1 : 1;
  };

  const onPointerDown = (e: React.PointerEvent<HTMLDivElement>) => {
    e.stopPropagation();
    e.preventDefault();
    (e.target as HTMLElement).setPointerCapture(e.pointerId);
    startRef.current = {
      x: e.clientX,
      y: e.clientY,
      w: baseWidth,
      h: baseHeight,
      zoom: currentZoom(),
    };
  };
  const onPointerMove = (e: React.PointerEvent<HTMLDivElement>) => {
    const s = startRef.current;
    if (!s) return;
    e.preventDefault();
    const dx = (e.clientX - s.x) / s.zoom;
    const dy = (e.clientY - s.y) / s.zoom;
    resizeCell(cellId, s.w + dx, s.h + dy);
  };
  const onPointerUp = (e: React.PointerEvent<HTMLDivElement>) => {
    if (startRef.current) {
      (e.target as HTMLElement).releasePointerCapture(e.pointerId);
      startRef.current = null;
    }
  };

  return (
    <div
      className="absolute right-0 bottom-0 w-5 h-5 cursor-nwse-resize nodrag nowheel"
      onPointerDown={onPointerDown}
      onPointerMove={onPointerMove}
      onPointerUp={onPointerUp}
      onPointerCancel={onPointerUp}
      title="Drag to resize"
    >
      {/* Doodle-y corner grip — two diagonal lines so it reads as
       *  a real handle without dominating the visual. */}
      <svg viewBox="0 0 20 20" className="w-full h-full pointer-events-none">
        <path
          d="M 4 18 L 18 4"
          stroke="var(--doodle-stroke, #2a2a2a)"
          strokeWidth="2"
          strokeLinecap="round"
        />
        <path
          d="M 10 18 L 18 10"
          stroke="var(--doodle-stroke, #2a2a2a)"
          strokeWidth="2"
          strokeLinecap="round"
          opacity="0.7"
        />
      </svg>
    </div>
  );
}
