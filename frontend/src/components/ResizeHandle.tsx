import { useReactFlow } from "reactflow";
import { useStore } from "../store";

/**
 * Bottom-right corner drag handle (Figma / Notion idiom). The on-screen
 * mouse delta is divided by the canvas zoom level so the cell grows at
 * the same speed as your cursor — no more "drag 1 px, cell grows 10 px"
 * when the canvas is zoomed out. Shift-drag locks the height
 * (width-only). Double-click resets to auto-size.
 */
const MIN_W = 360;
const MAX_W = 720;
const MIN_H = 80;
const MAX_H = 900;

export function ResizeHandle({
  cellId,
  baseWidth,
  baseHeight,
}: {
  cellId: string;
  baseWidth: number;
  baseHeight: number;
}) {
  const setCellSize = useStore((s) => s.setCellSize);
  const rf = useReactFlow();

  const onDown = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    const startX = e.clientX;
    const startY = e.clientY;
    const startW = Math.max(MIN_W, baseWidth);
    const startH = Math.max(MIN_H, baseHeight);
    // Cache zoom at drag start — the same drag should produce the same
    // resize speed even if the user zooms mid-drag.
    const zoom = Math.max(0.2, rf.getZoom());
    const widthOnly = e.shiftKey;

    const onMove = (ev: MouseEvent) => {
      const dx = (ev.clientX - startX) / zoom;
      const dy = (ev.clientY - startY) / zoom;
      const w = Math.max(MIN_W, Math.min(MAX_W, Math.round(startW + dx)));
      const h = Math.max(MIN_H, Math.min(MAX_H, Math.round(startH + dy)));
      setCellSize(cellId, widthOnly ? { width: w } : { width: w, height: h });
    };
    const onUp = () => {
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mouseup", onUp);
    };
    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseup", onUp);
  };

  const onDouble = (e: React.MouseEvent) => {
    e.stopPropagation();
    setCellSize(cellId, { width: undefined, height: undefined });
  };

  return (
    <div
      onMouseDown={onDown}
      onDoubleClick={onDouble}
      className="nodrag absolute right-1 bottom-1 w-5 h-5 cursor-nwse-resize opacity-40 hover:opacity-100 transition"
      title="Drag to resize · Shift for width-only · double-click to reset"
      style={{
        backgroundImage:
          "linear-gradient(135deg, transparent 0%, transparent 40%, currentColor 40%, currentColor 50%, transparent 50%, transparent 70%, currentColor 70%, currentColor 80%, transparent 80%)",
      }}
    />
  );
}
