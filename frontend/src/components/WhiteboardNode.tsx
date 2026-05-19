import { Handle, Position, NodeProps } from "reactflow";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { ResizeHandle } from "./ResizeHandle";
import { useStore } from "../store";

const DEFAULT_W = 960;
const DEFAULT_H = 600;

const PEN_COLORS = [
  "#2a2a2a", // ink
  "#e03131", // red
  "#1971c2", // blue
  "#2f9e44", // green
  "#f08c00", // amber
  "#ae3ec9", // violet
  "#ffffff", // eraser-ish (white on white, black on black)
];

type Stroke = {
  color: string;
  width: number;
  points: { x: number; y: number }[];
};

type Sticker = { url: string; x: number; y: number; w: number; h: number };

function safeParse<T>(s: string | undefined | null, fallback: T): T {
  if (!s) return fallback;
  try { return JSON.parse(s) as T; } catch { return fallback; }
}

/**
 * Whiteboard cell. Pure-canvas pen tool + draggable image stickers.
 *
 * - Background toggle: white / black (header button).
 * - Pen palette: 7 colors + width slider.
 * - Eraser: pen swatch matching the current background.
 * - Stickers: paste an image URL into the prompt → it appears top-left
 *   and is draggable inside the board.
 * - Persistence: every edit autosaves via store; strokes and stickers
 *   live in cell.meta.strokes / .stickers as JSON.
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
    idx: number;
    dx: number;
    dy: number;
    mode: "move" | "resize";
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

  const bg = cell?.meta?.whiteboard_bg ?? "white";
  const w = size?.width ?? DEFAULT_W;
  const h = size?.height ?? DEFAULT_H;

  // Re-sync state when external edits change meta (rare — autosave loop).
  useEffect(() => setStrokes(initialStrokes), [initialStrokes]);
  useEffect(() => setStickers(initialStickers), [initialStickers]);

  // Report height for canvas layout.
  useEffect(() => {
    const el = wrapRef.current;
    if (!el) return;
    const ro = new ResizeObserver((entries) => {
      for (const e of entries) reportCellHeight(cellId, Math.ceil(e.contentRect.height));
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, [cellId, reportCellHeight]);

  // Redraw whenever strokes / size / bg change.
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
    const drawStroke = (st: Stroke) => {
      if (!st.points.length) return;
      ctx.strokeStyle = st.color;
      ctx.lineWidth = st.width;
      ctx.beginPath();
      ctx.moveTo(st.points[0].x, st.points[0].y);
      for (let i = 1; i < st.points.length; i++) ctx.lineTo(st.points[i].x, st.points[i].y);
      ctx.stroke();
    };
    strokes.forEach(drawStroke);
    if (drawingRef.current) drawStroke(drawingRef.current);
  }, [strokes, w, h, bg]);

  // Resize the backing canvas to match displayed size (avoid blur).
  useEffect(() => {
    const c = canvasRef.current;
    if (!c) return;
    const surfaceH = h - 44; // minus header
    if (c.width !== w || c.height !== surfaceH) {
      c.width = w;
      c.height = surfaceH;
    }
  }, [w, h]);

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

  const toCanvasPoint = (e: React.PointerEvent<HTMLCanvasElement>) => {
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
    drawingRef.current = {
      color,
      width: penWidth,
      points: [toCanvasPoint(e)],
    };
  };

  const onPointerMove = (e: React.PointerEvent<HTMLCanvasElement>) => {
    if (!drawingRef.current) return;
    drawingRef.current.points.push(toCanvasPoint(e));
    // Trigger a re-render via state shuffle (cheaper than rAF for now).
    setStrokes((s) => s.slice());
  };

  const finishStroke = () => {
    const s = drawingRef.current;
    drawingRef.current = null;
    if (!s || s.points.length < 2) return;
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

  // Sticker drag handling (mouse).
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

  return (
    <div ref={wrapRef} data-cell-id={cellId} style={{ width: w, position: "relative" }}>
      <Handle type="target" position={Position.Left} />
      <div
        className="doodle-card relative p-0 overflow-hidden"
        style={{ height: h, borderRadius: 18 }}
      >
        {/* Header — bg toggle + pen palette + width + tools */}
        <div
          className={`flex items-center gap-2 px-2 py-1.5 border-b-2 nodrag ${headerCls}`}
        >
          <button
            className="text-base font-hand px-2 py-0.5 rounded border-2 border-current"
            onClick={onToggleBg}
            title="Toggle white / black background"
          >
            {bg === "white" ? "🌙 Black" : "☀ White"}
          </button>
          <div className="flex items-center gap-1 ml-1">
            {PEN_COLORS.map((c) => (
              <button
                key={c}
                onClick={() => setColor(c)}
                className="w-6 h-6 rounded-full border-2 transition"
                style={{
                  background: c,
                  borderColor: color === c
                    ? (dark ? "#fff" : "#000")
                    : "transparent",
                  outline: color === c ? `2px solid ${dark ? "#fff" : "#000"}` : "none",
                  outlineOffset: 1,
                }}
                title={`Pen ${c}`}
              />
            ))}
          </div>
          <label className="ml-2 text-xs select-none flex items-center gap-1">
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
              className="text-sm font-hand px-2 py-0.5 rounded border-2 border-current"
              onClick={onAddSticker}
              title="Drop a draggable image sticker"
            >
              🖼 Sticker
            </button>
            <button
              className="text-sm font-hand px-2 py-0.5 rounded border-2 border-current"
              onClick={onUndo}
              title="Undo last stroke"
            >
              ↶ Undo
            </button>
            <button
              className="text-sm font-hand px-2 py-0.5 rounded border-2 border-current"
              onClick={onClear}
              title="Clear all strokes and stickers"
            >
              ✕ Clear
            </button>
          </div>
        </div>

        {/* Canvas + stickers overlay */}
        <div
          className="relative"
          style={{ width: w, height: h - 44, background: dark ? "#0f1115" : "#ffffff" }}
        >
          <canvas
            ref={canvasRef}
            className="absolute inset-0 nodrag"
            style={{ width: "100%", height: "100%", touchAction: "none", cursor: "crosshair" }}
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
                    idx,
                    dx: e.clientX - s.x,
                    dy: e.clientY - s.y,
                    mode: "move",
                  };
                }}
              />
              {/* Resize handle (bottom-right corner of sticker) */}
              <div
                className="absolute"
                style={{
                  right: -6,
                  bottom: -6,
                  width: 14,
                  height: 14,
                  background: "#fff",
                  border: "2px solid #2a2a2a",
                  borderRadius: 3,
                  cursor: "nwse-resize",
                }}
                onMouseDown={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  stickerDragRef.current = {
                    idx,
                    dx: e.clientX - s.w,
                    dy: e.clientY - s.h,
                    mode: "resize",
                  };
                }}
              />
              {/* Delete sticker */}
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  const next = stickers.filter((_, i) => i !== idx);
                  commitStickers(next);
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
