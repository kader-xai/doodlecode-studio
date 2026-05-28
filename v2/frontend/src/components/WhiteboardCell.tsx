import { useEffect, useMemo, useRef, useState } from "react";
import { Handle, NodeProps, Position } from "reactflow";
import { DoodleBorder } from "./DoodleBorder";
import { EditableTitle } from "./EditableTitle";
import { ResizeHandle } from "./ResizeHandle";
import { useStore } from "../store";

const DEFAULT_W = 640;
const DEFAULT_H = 420;

type Tool = "pen" | "highlighter" | "eraser";

const COLORS = ["#2a2a2a", "#c2255c", "#1864ab", "#2b8a3e", "#fcc419"];

interface Stroke {
  tool: "pen" | "highlighter";
  color: string;
  width: number;
  /** Flat array [x0, y0, x1, y1, ...] — half the JSON size of {x,y} objects. */
  pts: number[];
}

interface WhiteboardSource {
  bg: "light" | "dark" | "sandal";
  strokes: Stroke[];
}

function decode(src: string): WhiteboardSource {
  try {
    const parsed = JSON.parse(src);
    if (parsed && Array.isArray(parsed.strokes)) {
      return {
        bg: ["light", "dark", "sandal"].includes(parsed.bg) ? parsed.bg : "light",
        strokes: parsed.strokes,
      };
    }
  } catch { /* fall through */ }
  return { bg: "light", strokes: [] };
}

const BG_COLOR: Record<WhiteboardSource["bg"], string> = {
  light: "#ffffff",
  sandal: "#f5ecd6",
  dark: "#1a1d23",
};

/**
 * Whiteboard cell — drawing surface inside a doodle border.
 *
 * **Drawing pattern that actually works** (v1's hard-earned lesson):
 *   - Pointer-down on the canvas calls `setPointerCapture` so the
 *     drag survives cursor leaving the cell.
 *   - The active stroke lives in a REF and is painted directly to the
 *     canvas (`ctx.beginPath` / `lineTo`) — NO React re-render per
 *     pointer-move. Re-rendering at pointer-rate makes Monaco/iframes
 *     misbehave and drops points.
 *   - On pointer-up we commit the finished stroke to `cell.source`
 *     (one store update per stroke).
 *   - All strokes re-paint from store on every render (full redraw is
 *     cheap for hundreds of strokes; we only do it once per commit).
 *
 * Eraser is whole-stroke: clicking near a stroke removes it. Simpler
 * than pixel erasure and matches what users actually want when wiping
 * a doodle.
 */
export function WhiteboardCell({ data, selected }: NodeProps<{ cellId: string }>) {
  const cellId = data.cellId;
  const cell = useStore((s) => s.cells.find((c) => c.id === cellId));
  const setSource = useStore((s) => s.setSource);
  const setTitle = useStore((s) => s.setTitle);
  const setSelected = useStore((s) => s.setSelected);
  const toggleCollapse = useStore((s) => s.toggleCollapse);
  const renameTick = useStore((s) => s.renameTick[cellId] ?? 0);

  const [tool, setTool] = useState<Tool>("pen");
  const [color, setColor] = useState<string>(COLORS[0]);

  // F2 → title rename bridge.
  const [forceEditTitle, setForceEditTitle] = useState(false);
  useEffect(() => {
    if (renameTick > 0) {
      setForceEditTitle(true);
      const t = setTimeout(() => setForceEditTitle(false), 50);
      return () => clearTimeout(t);
    }
  }, [renameTick]);

  const decoded = useMemo<WhiteboardSource>(
    () => decode(cell?.source ?? ""),
    [cell?.source],
  );

  const canvasRef = useRef<HTMLCanvasElement>(null);
  const activeRef = useRef<Stroke | null>(null);
  // Pixel ratio for crisp lines on hi-dpi displays.
  const dprRef = useRef<number>(1);

  // (Re-)paint everything from the store. Cheap enough at <1000 strokes;
  // we only call this on commit / size change / theme change.
  const repaint = () => {
    const c = canvasRef.current;
    if (!c) return;
    const ctx = c.getContext("2d");
    if (!ctx) return;
    const w = c.width;
    const h = c.height;
    ctx.clearRect(0, 0, w, h);
    ctx.fillStyle = BG_COLOR[decoded.bg];
    ctx.fillRect(0, 0, w, h);

    for (const s of decoded.strokes) paintStroke(ctx, s, dprRef.current);
    const live = activeRef.current;
    if (live) paintStroke(ctx, live, dprRef.current);
  };

  // Resize the canvas backing store whenever the cell box changes.
  useEffect(() => {
    const c = canvasRef.current;
    if (!c) return;
    const wrapper = c.parentElement;
    if (!wrapper) return;
    const ro = new ResizeObserver(() => {
      const rect = wrapper.getBoundingClientRect();
      const dpr = window.devicePixelRatio || 1;
      dprRef.current = dpr;
      c.width = Math.round(rect.width * dpr);
      c.height = Math.round(rect.height * dpr);
      c.style.width = `${rect.width}px`;
      c.style.height = `${rect.height}px`;
      repaint();
    });
    ro.observe(wrapper);
    return () => ro.disconnect();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Repaint when the store data changes (load, undo, clear, color, theme).
  useEffect(() => {
    repaint();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [decoded]);

  // ── Drawing handlers ────────────────────────────────────────────

  const commit = (next: WhiteboardSource) => {
    setSource(cellId, JSON.stringify(next));
  };

  const onPointerDown = (e: React.PointerEvent<HTMLCanvasElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setSelected(cellId);
    (e.currentTarget as HTMLCanvasElement).setPointerCapture(e.pointerId);
    const dpr = dprRef.current;
    const x = e.nativeEvent.offsetX * dpr;
    const y = e.nativeEvent.offsetY * dpr;

    if (tool === "eraser") {
      const hit = hitStroke(decoded.strokes, x, y);
      if (hit >= 0) {
        const next = { ...decoded, strokes: decoded.strokes.filter((_, i) => i !== hit) };
        commit(next);
      }
      return;
    }

    activeRef.current = {
      tool,
      color: tool === "highlighter" ? hex2rgba(color, 0.35) : color,
      width: tool === "highlighter" ? 16 : 3,
      pts: [x, y],
    };
  };

  const onPointerMove = (e: React.PointerEvent<HTMLCanvasElement>) => {
    if (tool === "eraser") {
      if (e.pressure > 0 || e.buttons & 1) {
        const dpr = dprRef.current;
        const x = e.nativeEvent.offsetX * dpr;
        const y = e.nativeEvent.offsetY * dpr;
        const hit = hitStroke(decoded.strokes, x, y);
        if (hit >= 0) {
          const next = { ...decoded, strokes: decoded.strokes.filter((_, i) => i !== hit) };
          commit(next);
        }
      }
      return;
    }
    const live = activeRef.current;
    if (!live) return;
    e.preventDefault();
    const dpr = dprRef.current;
    const x = e.nativeEvent.offsetX * dpr;
    const y = e.nativeEvent.offsetY * dpr;
    live.pts.push(x, y);

    // Incremental paint — just the last segment.
    const c = canvasRef.current;
    if (!c) return;
    const ctx = c.getContext("2d");
    if (!ctx) return;
    const n = live.pts.length;
    if (n >= 4) {
      ctx.strokeStyle = live.color;
      ctx.lineWidth = live.width * dpr;
      ctx.lineCap = "round";
      ctx.lineJoin = "round";
      ctx.beginPath();
      ctx.moveTo(live.pts[n - 4], live.pts[n - 3]);
      ctx.lineTo(live.pts[n - 2], live.pts[n - 1]);
      ctx.stroke();
    }
  };

  const onPointerUp = (e: React.PointerEvent<HTMLCanvasElement>) => {
    (e.currentTarget as HTMLCanvasElement).releasePointerCapture(e.pointerId);
    const live = activeRef.current;
    activeRef.current = null;
    if (live && live.pts.length >= 4) {
      const next = { ...decoded, strokes: [...decoded.strokes, live] };
      commit(next);
    } else {
      repaint(); // wipe accidental dot
    }
  };

  const setBg = (bg: WhiteboardSource["bg"]) => commit({ ...decoded, bg });
  const clearAll = () => {
    if (!decoded.strokes.length) return;
    if (window.confirm("Clear the whiteboard?")) commit({ ...decoded, strokes: [] });
  };
  const undo = () => {
    if (!decoded.strokes.length) return;
    commit({ ...decoded, strokes: decoded.strokes.slice(0, -1) });
  };

  if (!cell) return null;

  const w = cell.w ?? DEFAULT_W;
  const h = cell.h ?? DEFAULT_H;
  const ringColor = selected ? "#c2255c" : "var(--doodle-stroke, #2a2a2a)";
  const ringWidth = selected ? 3.5 : 2.5;

  return (
    <div
      className="relative"
      // Iter 66: collapse drops outer height to ~44 px so only the
      // tool strip is visible — matches Diagram + Browser pattern.
      style={{ width: w, height: cell.collapsed ? 44 : h }}
      onClickCapture={() => setSelected(cellId)}
    >
      <Handle type="target" position={Position.Left} className="!bg-transparent !border-0" />

      <div className="absolute inset-0">
        <DoodleBorder stroke={ringColor} fill={BG_COLOR[decoded.bg]} strokeWidth={ringWidth} radius={14} />

        <div className="absolute inset-1 flex flex-col overflow-hidden rounded-lg">
          {/* Tool strip — draggable. `nodrag` lives only on the
           *  interactive children (ToolBtn, color swatches) so the
           *  empty space between them stays a drag handle. */}
          <div className="flex items-center gap-1.5 px-1.5 py-1 border-b-2 border-ink/30 dark:border-white/30 bg-white/80 dark:bg-[#1f2228]">
            {/* Iter 66: collapse chevron. */}
            <button
              type="button"
              onClick={(e) => { e.stopPropagation(); toggleCollapse(cellId); }}
              onPointerDown={(e) => e.stopPropagation()}
              onMouseDown={(e) => e.stopPropagation()}
              className="font-mono text-sm w-5 h-5 leading-none rounded border-2 border-ink/30 dark:border-white/30 bg-white/60 dark:bg-black/40 text-ink/70 dark:text-white/70 hover:bg-marker-yellow/50 dark:hover:bg-amber-700/30 transition nodrag shrink-0"
              title={cell.collapsed ? "Expand cell" : "Collapse cell"}
            >
              {cell.collapsed ? "▸" : "▾"}
            </button>
            <EditableTitle
              value={cell.title}
              onCommit={(t) => setTitle(cellId, t)}
              forceEdit={forceEditTitle}
              className="font-hand text-base truncate text-ink dark:text-white flex-1 min-w-0"
            />
            <ToolBtn label="✒️" title="Pen" active={tool === "pen"} onClick={() => setTool("pen")} />
            <ToolBtn label="🖍" title="Highlighter" active={tool === "highlighter"} onClick={() => setTool("highlighter")} />
            <ToolBtn label="🧽" title="Eraser (drag over strokes)" active={tool === "eraser"} onClick={() => setTool("eraser")} />
            <div className="mx-0.5 h-5 w-px bg-ink/30 dark:bg-white/30" />
            {COLORS.map((c) => (
              <button
                key={c}
                type="button"
                onClick={(e) => { e.stopPropagation(); setColor(c); setTool((t) => t === "eraser" ? "pen" : t); }}
                onPointerDown={(e) => e.stopPropagation()}
                onMouseDown={(e) => e.stopPropagation()}
                title={c}
                style={{ background: c }}
                className={`nodrag w-5 h-5 rounded-full border-2 ${color === c ? "border-[#c2255c] scale-110" : "border-ink/60 dark:border-white/40"} transition`}
              />
            ))}
            <div className="mx-0.5 h-5 w-px bg-ink/30 dark:bg-white/30" />
            <BgBtn label="□" title="White bg"  active={decoded.bg === "light"}  onClick={() => setBg("light")} />
            <BgBtn label="◧" title="Sandal bg" active={decoded.bg === "sandal"} onClick={() => setBg("sandal")} />
            <BgBtn label="■" title="Dark bg"   active={decoded.bg === "dark"}   onClick={() => setBg("dark")} />
            <div className="mx-0.5 h-5 w-px bg-ink/30 dark:bg-white/30" />
            <ToolBtn label="↶" title="Undo last stroke" onClick={undo} />
            <ToolBtn label="🗑" title="Clear all" onClick={clearAll} />
          </div>

          {/* Drawing surface — hidden when collapsed (iter 66). */}
          {!cell.collapsed && (
          <div className="relative flex-1 overflow-hidden nodrag nowheel">
            <canvas
              ref={canvasRef}
              onPointerDown={onPointerDown}
              onPointerMove={onPointerMove}
              onPointerUp={onPointerUp}
              onPointerCancel={onPointerUp}
              onLostPointerCapture={onPointerUp}
              style={{
                display: "block",
                width: "100%",
                height: "100%",
                touchAction: "none",
                cursor: tool === "eraser" ? "cell" : "crosshair",
              }}
            />
          </div>
          )}
        </div>

        <ResizeHandle cellId={cellId} baseWidth={w} baseHeight={h} />
      </div>

      <Handle type="source" position={Position.Right} className="!bg-transparent !border-0" />
    </div>
  );
}

function ToolBtn({
  label, title, active, onClick,
}: { label: string; title: string; active?: boolean; onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={(e) => { e.stopPropagation(); onClick(); }}
      onPointerDown={(e) => e.stopPropagation()}
      onMouseDown={(e) => e.stopPropagation()}
      title={title}
      className={`nodrag font-hand text-base w-7 h-7 rounded-md border-2 transition ${
        active
          ? "bg-marker-yellow border-ink dark:bg-amber-700 dark:border-white text-ink dark:text-white shadow-sketch"
          : "bg-white/80 dark:bg-[#262a31] border-ink/40 dark:border-white/30 text-ink dark:text-white hover:translate-y-[1px]"
      }`}
    >
      {label}
    </button>
  );
}
const BgBtn = ToolBtn;

function paintStroke(ctx: CanvasRenderingContext2D, s: Stroke, dpr: number) {
  if (s.pts.length < 4) return;
  ctx.strokeStyle = s.color;
  ctx.lineWidth = s.width * dpr;
  ctx.lineCap = "round";
  ctx.lineJoin = "round";
  ctx.beginPath();
  ctx.moveTo(s.pts[0], s.pts[1]);
  for (let i = 2; i < s.pts.length; i += 2) {
    ctx.lineTo(s.pts[i], s.pts[i + 1]);
  }
  ctx.stroke();
}

/** Index of the first stroke whose path passes within `tol` px of (x,y).
 *  Coords are in CANVAS (post-dpr) space. */
function hitStroke(strokes: Stroke[], x: number, y: number, tol = 8): number {
  const tol2 = tol * tol;
  for (let i = strokes.length - 1; i >= 0; i--) {
    const pts = strokes[i].pts;
    for (let j = 0; j < pts.length - 3; j += 2) {
      // Squared distance from (x,y) to segment ((pts[j],pts[j+1]) → (pts[j+2],pts[j+3])).
      const x1 = pts[j], y1 = pts[j + 1], x2 = pts[j + 2], y2 = pts[j + 3];
      const dx = x2 - x1, dy = y2 - y1;
      const len2 = dx * dx + dy * dy || 1;
      let t = ((x - x1) * dx + (y - y1) * dy) / len2;
      t = Math.max(0, Math.min(1, t));
      const px = x1 + t * dx, py = y1 + t * dy;
      const ddx = x - px, ddy = y - py;
      if (ddx * ddx + ddy * ddy < tol2) return i;
    }
  }
  return -1;
}

function hex2rgba(hex: string, a: number): string {
  const m = hex.match(/^#([0-9a-f]{6})$/i);
  if (!m) return hex;
  const n = parseInt(m[1], 16);
  return `rgba(${(n >> 16) & 0xff}, ${(n >> 8) & 0xff}, ${n & 0xff}, ${a})`;
}
