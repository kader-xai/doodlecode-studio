import { Handle, Position, NodeProps } from "reactflow";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { ResizeHandle } from "./ResizeHandle";
import { useStore } from "../store";

const DEFAULT_W = 1100;
const DEFAULT_H = 640;

const PEN_COLORS = [
  "#2a2a2a", // ink
  "#e03131", // red
  "#1971c2", // blue
  "#2f9e44", // green
  "#f08c00", // amber
  "#ae3ec9", // violet
  "#ffffff", // white (works as eraser-tinted pen on dark bgs)
];

type Tool = "pen" | "line" | "circle" | "arrow" | "eraser";
type Pt = { x: number; y: number };
/** A single drawn shape on the board.
 *  `kind` defaults to "pen" for backward compatibility with older
 *  whiteboards that stored only freehand strokes. */
type Stroke = {
  kind?: Tool;
  color: string;
  width: number;
  points: Pt[];
};

type Sticker = { url: string; x: number; y: number; w: number; h: number };

function safeParse<T>(s: string | undefined | null, fallback: T): T {
  if (!s) return fallback;
  try { return JSON.parse(s) as T; } catch { return fallback; }
}

// Distance from point P to segment A-B (used by the eraser).
function distToSegment(px: number, py: number, ax: number, ay: number, bx: number, by: number): number {
  const dx = bx - ax;
  const dy = by - ay;
  const len2 = dx * dx + dy * dy;
  let t = len2 === 0 ? 0 : ((px - ax) * dx + (py - ay) * dy) / len2;
  t = Math.max(0, Math.min(1, t));
  const cx = ax + t * dx;
  const cy = ay + t * dy;
  return Math.hypot(px - cx, py - cy);
}

function strokeIsNearPoint(st: Stroke, p: Pt, threshold: number): boolean {
  if (st.points.length === 0) return false;
  if (st.points.length === 1) {
    return Math.hypot(st.points[0].x - p.x, st.points[0].y - p.y) <= threshold;
  }
  // For line / arrow / pen, check distance to each segment.
  if (st.kind === "circle") {
    const [a, b] = st.points;
    const cx = (a.x + b.x) / 2;
    const cy = (a.y + b.y) / 2;
    const rx = Math.abs(b.x - a.x) / 2;
    const ry = Math.abs(b.y - a.y) / 2;
    // Approximate by treating as average-radius circle.
    const r = (rx + ry) / 2;
    return Math.abs(Math.hypot(p.x - cx, p.y - cy) - r) <= threshold;
  }
  for (let i = 1; i < st.points.length; i++) {
    if (distToSegment(p.x, p.y, st.points[i - 1].x, st.points[i - 1].y, st.points[i].x, st.points[i].y) <= threshold) {
      return true;
    }
  }
  return false;
}

/**
 * Whiteboard cell — pen, line, circle, arrow, eraser + stickers.
 *
 * Header bar
 *   bg-toggle  | tool buttons | color palette | width slider |
 *                                            sticker | undo | clear
 *
 * Strokes + stickers persist into cell.meta.strokes / .stickers as
 * JSON strings (backward-compatible with v1.3.6 whiteboards — those
 * had no `kind`, so we treat them as "pen").
 */
export function WhiteboardNode({ data }: NodeProps<{ cellId: string }>) {
  const cellId = data.cellId;
  const cell = useStore((s) => s.notebook.cells.find((c) => c.id === cellId));
  const size = useStore((s) => s.cellSize[cellId]);
  const reportCellHeight = useStore((s) => s.reportCellHeight);
  const updateMeta = useStore((s) => s.updateCellMeta);

  const wrapRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const drawingRef = useRef<Stroke | null>(null);
  const stickerDragRef = useRef<{
    idx: number; dx: number; dy: number; mode: "move" | "resize";
  } | null>(null);

  const initialStrokes = useMemo<Stroke[]>(
    () => safeParse<Stroke[]>(cell?.meta?.strokes, []),
    [cell?.meta?.strokes]
  );
  const initialStickers = useMemo<Sticker[]>(
    () => safeParse<Sticker[]>(cell?.meta?.stickers, []),
    [cell?.meta?.stickers]
  );

  const [strokes, setStrokes] = useState<Stroke[]>(initialStrokes);
  const [stickers, setStickers] = useState<Sticker[]>(initialStickers);
  const [color, setColor] = useState<string>(PEN_COLORS[0]);
  const [penWidth, setPenWidth] = useState<number>(3);
  const [tool, setTool] = useState<Tool>("pen");

  const bg = cell?.meta?.whiteboard_bg ?? "white";
  const w = size?.width ?? DEFAULT_W;
  const h = size?.height ?? DEFAULT_H;

  useEffect(() => setStrokes(initialStrokes), [initialStrokes]);
  useEffect(() => setStickers(initialStickers), [initialStickers]);

  useEffect(() => {
    const el = wrapRef.current;
    if (!el) return;
    const ro = new ResizeObserver((entries) => {
      for (const e of entries) reportCellHeight(cellId, Math.ceil(e.contentRect.height));
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, [cellId, reportCellHeight]);

  // Resize backing canvas to displayed size.
  useEffect(() => {
    const c = canvasRef.current;
    if (!c) return;
    const surfaceH = h - 44;
    if (c.width !== w || c.height !== surfaceH) {
      c.width = w;
      c.height = surfaceH;
    }
  }, [w, h]);

  const drawShape = (ctx: CanvasRenderingContext2D, st: Stroke) => {
    if (!st.points.length) return;
    ctx.strokeStyle = st.color;
    ctx.lineWidth = st.width;
    const kind = st.kind ?? "pen";
    if (kind === "pen") {
      ctx.beginPath();
      ctx.moveTo(st.points[0].x, st.points[0].y);
      for (let i = 1; i < st.points.length; i++) ctx.lineTo(st.points[i].x, st.points[i].y);
      ctx.stroke();
      return;
    }
    if (st.points.length < 2) return;
    const a = st.points[0];
    const b = st.points[st.points.length - 1];
    if (kind === "line") {
      ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke();
      return;
    }
    if (kind === "circle") {
      const cx = (a.x + b.x) / 2;
      const cy = (a.y + b.y) / 2;
      const rx = Math.abs(b.x - a.x) / 2;
      const ry = Math.abs(b.y - a.y) / 2;
      ctx.beginPath();
      ctx.ellipse(cx, cy, Math.max(1, rx), Math.max(1, ry), 0, 0, Math.PI * 2);
      ctx.stroke();
      return;
    }
    if (kind === "arrow") {
      ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke();
      // Arrowhead.
      const ang = Math.atan2(b.y - a.y, b.x - a.x);
      const head = Math.max(10, st.width * 3);
      ctx.beginPath();
      ctx.moveTo(b.x, b.y);
      ctx.lineTo(b.x - head * Math.cos(ang - Math.PI / 7), b.y - head * Math.sin(ang - Math.PI / 7));
      ctx.lineTo(b.x - head * Math.cos(ang + Math.PI / 7), b.y - head * Math.sin(ang + Math.PI / 7));
      ctx.closePath();
      ctx.fillStyle = st.color;
      ctx.fill();
      return;
    }
  };

  useEffect(() => {
    const c = canvasRef.current;
    if (!c) return;
    const ctx = c.getContext("2d");
    if (!ctx) return;
    const cw = c.width;
    const ch = c.height;
    ctx.clearRect(0, 0, cw, ch);
    ctx.fillStyle = bg === "black" ? "#0f1115" : "#ffffff";
    ctx.fillRect(0, 0, cw, ch);
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    strokes.forEach((st) => drawShape(ctx, st));
    if (drawingRef.current) drawShape(ctx, drawingRef.current);
  }, [strokes, w, h, bg]);

  const commitStrokes = useCallback(
    (next: Stroke[]) => {
      setStrokes(next);
      updateMeta(cellId, {
        ...(cell?.meta ?? {}),
        cell_type: "whiteboard",
        strokes: JSON.stringify(next),
      });
    },
    [cellId, cell?.meta, updateMeta]
  );

  const commitStickers = useCallback(
    (next: Sticker[]) => {
      setStickers(next);
      updateMeta(cellId, {
        ...(cell?.meta ?? {}),
        cell_type: "whiteboard",
        stickers: JSON.stringify(next),
      });
    },
    [cellId, cell?.meta, updateMeta]
  );

  const toCanvasPoint = (e: React.PointerEvent<HTMLCanvasElement>): Pt => {
    const c = canvasRef.current!;
    const rect = c.getBoundingClientRect();
    return {
      x: ((e.clientX - rect.left) / rect.width) * c.width,
      y: ((e.clientY - rect.top) / rect.height) * c.height,
    };
  };

  const onPointerDown = (e: React.PointerEvent<HTMLCanvasElement>) => {
    if (stickerDragRef.current) return;
    e.stopPropagation();
    (e.target as Element).setPointerCapture?.(e.pointerId);
    const p = toCanvasPoint(e);
    if (tool === "eraser") {
      const thr = Math.max(8, penWidth * 2);
      const survived = strokes.filter((st) => !strokeIsNearPoint(st, p, thr));
      if (survived.length !== strokes.length) commitStrokes(survived);
      // Track a flag so drag-erasing keeps removing while the pointer moves.
      drawingRef.current = { kind: "eraser", color: "", width: penWidth, points: [p] };
      return;
    }
    drawingRef.current = {
      kind: tool,
      color,
      width: penWidth,
      points: [p],
    };
  };

  const onPointerMove = (e: React.PointerEvent<HTMLCanvasElement>) => {
    if (!drawingRef.current) return;
    const p = toCanvasPoint(e);
    if (drawingRef.current.kind === "eraser") {
      const thr = Math.max(8, penWidth * 2);
      const survived = strokes.filter((st) => !strokeIsNearPoint(st, p, thr));
      if (survived.length !== strokes.length) commitStrokes(survived);
      drawingRef.current.points.push(p);
      return;
    }
    if (drawingRef.current.kind === "pen") {
      drawingRef.current.points.push(p);
    } else {
      // line / circle / arrow — keep only the first + current point.
      drawingRef.current.points = [drawingRef.current.points[0], p];
    }
    setStrokes((s) => s.slice()); // trigger redraw
  };

  const finishStroke = () => {
    const s = drawingRef.current;
    drawingRef.current = null;
    if (!s) return;
    if (s.kind === "eraser") return; // already committed during move
    if (s.kind === "pen" && s.points.length < 2) return;
    if (s.kind !== "pen" && s.points.length < 2) return;
    commitStrokes([...strokes, s]);
  };

  const onClear = () => {
    if (!strokes.length && !stickers.length) return;
    if (!window.confirm("Clear the whiteboard (strokes + stickers)?")) return;
    commitStrokes([]);
    commitStickers([]);
  };

  const onUndo = () => {
    if (!strokes.length) return;
    commitStrokes(strokes.slice(0, -1));
  };

  const onAddSticker = () => {
    const url = window.prompt("Sticker image URL (any image — /demo/chart.png also works)");
    if (!url || !url.trim()) return;
    commitStickers([
      ...stickers,
      { url: url.trim(), x: 30, y: 30, w: 140, h: 140 },
    ]);
  };

  const onToggleBg = () => {
    updateMeta(cellId, {
      ...(cell?.meta ?? {}),
      cell_type: "whiteboard",
      whiteboard_bg: bg === "white" ? "black" : "white",
    });
  };

  // Sticker drag handling.
  useEffect(() => {
    const onMove = (e: MouseEvent) => {
      const drag = stickerDragRef.current;
      if (!drag) return;
      e.preventDefault();
      const next = stickers.slice();
      const s = { ...next[drag.idx] };
      if (drag.mode === "move") {
        s.x = e.clientX - drag.dx;
        s.y = e.clientY - drag.dy;
      } else {
        s.w = Math.max(40, e.clientX - drag.dx);
        s.h = Math.max(40, e.clientY - drag.dy);
      }
      next[drag.idx] = s;
      setStickers(next);
    };
    const onUp = () => {
      if (!stickerDragRef.current) return;
      stickerDragRef.current = null;
      commitStickers(stickers);
    };
    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseup", onUp);
    return () => {
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mouseup", onUp);
    };
  }, [stickers, commitStickers]);

  if (!cell) return null;

  const dark = bg === "black";
  const headerCls = dark
    ? "bg-[#0f1115] text-white border-white/40"
    : "bg-white text-ink border-ink/40";

  const TOOLS: { id: Tool; icon: string; label: string }[] = [
    { id: "pen",    icon: "✎",  label: "Pen"     },
    { id: "line",   icon: "／", label: "Line"    },
    { id: "circle", icon: "◯", label: "Circle"  },
    { id: "arrow",  icon: "→", label: "Arrow"   },
    { id: "eraser", icon: "✗",  label: "Eraser"  },
  ];

  const toolBtn = (active: boolean) =>
    `text-base font-hand w-9 h-8 rounded border-2 transition ${
      active
        ? "bg-marker-yellow border-ink text-ink shadow-sketch"
        : (dark
            ? "bg-[#0f1115] border-white/40 text-white/80"
            : "bg-white border-ink/40 text-ink/70")
    }`;

  const cursorClass =
    tool === "eraser" ? "cursor-cell"
    : tool === "pen" ? "cursor-crosshair"
    : "cursor-crosshair";

  return (
    <div ref={wrapRef} data-cell-id={cellId} style={{ width: w, position: "relative" }}>
      <Handle type="target" position={Position.Left} />
      <div className="doodle-card relative p-0 overflow-hidden" style={{ height: h, borderRadius: 18 }}>
        <div className={`flex items-center gap-2 px-2 py-1.5 border-b-2 nodrag flex-wrap ${headerCls}`}>
          <button
            type="button"
            className="text-base font-hand px-2 py-0.5 rounded border-2 border-current"
            onClick={onToggleBg}
            title="Toggle white / black background"
          >
            {bg === "white" ? "🌙 Black" : "☀ White"}
          </button>

          {/* Tools */}
          <div className="flex items-center gap-1">
            {TOOLS.map((t) => (
              <button
                key={t.id}
                type="button"
                className={toolBtn(tool === t.id)}
                onClick={() => setTool(t.id)}
                title={t.label}
                aria-label={t.label}
              >
                {t.icon}
              </button>
            ))}
          </div>

          {/* Colors (irrelevant for eraser, but harmless) */}
          <div className="flex items-center gap-1 ml-1">
            {PEN_COLORS.map((c) => (
              <button
                key={c}
                type="button"
                onClick={() => setColor(c)}
                className="w-6 h-6 rounded-full border-2 transition"
                style={{
                  background: c,
                  borderColor: color === c ? (dark ? "#fff" : "#000") : "transparent",
                  outline: color === c ? `2px solid ${dark ? "#fff" : "#000"}` : "none",
                  outlineOffset: 1,
                }}
                title={`Color ${c}`}
              />
            ))}
          </div>

          {/* Width */}
          <label className="ml-1 text-xs select-none flex items-center gap-1">
            width
            <input
              type="range"
              min={1}
              max={24}
              value={penWidth}
              onChange={(e) => setPenWidth(parseInt(e.target.value, 10))}
              className="w-20"
            />
            <span className="font-mono text-xs w-6 text-right">{penWidth}</span>
          </label>

          <div className="ml-auto flex items-center gap-1">
            <button
              type="button"
              className="text-sm font-hand px-2 py-0.5 rounded border-2 border-current"
              onClick={onAddSticker}
              title="Drop a draggable image sticker"
            >
              🖼 Sticker
            </button>
            <button
              type="button"
              className="text-sm font-hand px-2 py-0.5 rounded border-2 border-current"
              onClick={onUndo}
              title="Undo last shape"
            >
              ↶ Undo
            </button>
            <button
              type="button"
              className="text-sm font-hand px-2 py-0.5 rounded border-2 border-current"
              onClick={onClear}
              title="Clear all shapes and stickers"
            >
              ✕ Clear
            </button>
          </div>
        </div>

        <div
          className="relative"
          style={{ width: w, height: h - 44, background: dark ? "#0f1115" : "#ffffff" }}
        >
          <canvas
            ref={canvasRef}
            className={`absolute inset-0 nodrag ${cursorClass}`}
            style={{ width: "100%", height: "100%", touchAction: "none" }}
            onPointerDown={onPointerDown}
            onPointerMove={onPointerMove}
            onPointerUp={finishStroke}
            onPointerLeave={finishStroke}
          />
          {stickers.map((s, idx) => (
            <div
              key={idx}
              className="absolute nodrag"
              style={{ left: s.x, top: s.y, width: s.w, height: s.h, zIndex: 5 }}
            >
              <img
                src={s.url}
                alt=""
                draggable={false}
                style={{
                  width: "100%",
                  height: "100%",
                  objectFit: "contain",
                  border: "2px solid rgba(0,0,0,0.4)",
                  borderRadius: 6,
                  cursor: "grab",
                  background: "rgba(255,255,255,0.6)",
                }}
                onMouseDown={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  stickerDragRef.current = {
                    idx, dx: e.clientX - s.x, dy: e.clientY - s.y, mode: "move",
                  };
                }}
              />
              <div
                className="absolute"
                style={{
                  right: -6, bottom: -6, width: 14, height: 14,
                  background: "#fff", border: "2px solid #2a2a2a",
                  borderRadius: 3, cursor: "nwse-resize",
                }}
                onMouseDown={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  stickerDragRef.current = {
                    idx, dx: e.clientX - s.w, dy: e.clientY - s.h, mode: "resize",
                  };
                }}
              />
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  commitStickers(stickers.filter((_, i) => i !== idx));
                }}
                className="absolute -top-3 -right-3 w-6 h-6 rounded-full border-2 border-ink bg-white text-ink text-xs font-bold"
                title="Remove sticker"
              >
                ✕
              </button>
            </div>
          ))}
        </div>
      </div>
      <ResizeHandle cellId={cellId} baseWidth={w} baseHeight={h} />
      <Handle type="source" position={Position.Right} />
    </div>
  );
}
