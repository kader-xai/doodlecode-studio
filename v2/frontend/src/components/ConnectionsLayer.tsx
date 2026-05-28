import { useViewport } from "reactflow";
import { useStore } from "../store";

/**
 * SVG overlay that draws dashed dot-flow connectors between cells
 * and their callouts. Mounted inside the ReactFlow pane so it sits
 * over the dot grid but under the nodes. We apply the same `transform`
 * as ReactFlow's viewport so panning + zooming carry the lines along.
 *
 * Why a custom layer instead of ReactFlow edges? ReactFlow silently
 * drops edges when the source/target node hasn't had its handle
 * bounds measured by ReactFlow's internal ResizeObserver. Our
 * synthetic callout pseudo-nodes never get measured (likely because
 * we manage `nodes` in local state outside ReactFlow's setNodes
 * pipeline) so every cell→callout edge was being filtered out by
 * `getNodeData(node).isValid`. Computing positions ourselves
 * sidesteps the whole measurement story.
 *
 * Geometry: each connector goes from the right edge of the cell
 * (cell.x + cellWidth, cell.y + cellHeight / 2) to the left edge of
 * the first callout (calloutX, calloutY + bubbleHeight / 2). For
 * cells with multiple callouts each bubble chains to the previous.
 */
const FALLBACK_W: Record<string, number> = {
  code: 580,
  markdown: 560,
  diagram: 560,
  browser: 720,
  whiteboard: 640,
};
const FALLBACK_H: Record<string, number> = {
  code: 260,
  markdown: 240,
  diagram: 360,
  browser: 480,
  whiteboard: 420,
  media: 320,
};
const CALLOUT_GAP = 40;
const BUBBLE_W = 280;
const BUBBLE_H_APPROX = 140; // matches CalloutBubble visual height
const STACK_DY = 200;

export function ConnectionsLayer() {
  const cells = useStore((s) => s.cells);
  const dark = useStore((s) => s.theme === "dark");
  // useViewport tracks pan + zoom so our SVG follows ReactFlow's
  // viewport on every frame.
  const { x: vx, y: vy, zoom } = useViewport();

  const segments: { x1: number; y1: number; x2: number; y2: number; key: string }[] = [];
  for (const c of cells) {
    const list = c.callouts ?? [];
    if (!list.length) continue;
    const cellW = c.w ?? FALLBACK_W[c.kind] ?? 560;
    const cellH = c.h ?? FALLBACK_H[c.kind] ?? 280;
    const cellRightX = c.x + cellW;
    const cellMidY = c.y + cellH / 2;
    const bubbleX = c.x + cellW + CALLOUT_GAP;

    for (let i = 0; i < list.length; i++) {
      const bubbleY = c.y + i * STACK_DY;
      const bubbleMidY = bubbleY + BUBBLE_H_APPROX / 2;
      if (i === 0) {
        // Cell → first callout: cell's right midpoint → bubble's left midpoint.
        segments.push({
          key: `${c.id}-c-${i}`,
          x1: cellRightX, y1: cellMidY,
          x2: bubbleX,    y2: bubbleMidY,
        });
      } else {
        // Bubble (i-1) → bubble (i): bottom of prev → top of current.
        const prevBubbleBottom = c.y + (i - 1) * STACK_DY + BUBBLE_H_APPROX;
        segments.push({
          key: `${c.id}-c-${i}`,
          x1: bubbleX + BUBBLE_W / 2, y1: prevBubbleBottom,
          x2: bubbleX + BUBBLE_W / 2, y2: bubbleY,
        });
      }
    }
  }

  if (!segments.length) return null;

  return (
    <svg
      aria-hidden
      style={{
        position: "absolute",
        inset: 0,
        // Sit under nodes (which are z:auto inside the viewport) but
        // above the background dots.
        zIndex: 1,
        pointerEvents: "none",
        width: "100%",
        height: "100%",
        overflow: "visible",
      }}
    >
      <g transform={`translate(${vx}, ${vy}) scale(${zoom})`}>
        {segments.map((s) => (
          <line
            key={s.key}
            x1={s.x1}
            y1={s.y1}
            x2={s.x2}
            y2={s.y2}
            stroke={dark ? "#aaa" : "#555"}
            strokeWidth={2.5}
            strokeLinecap="round"
            strokeDasharray="1 10"
            // CSS class powers the dashoffset keyframe in index.css.
            className="doodle-connector"
          />
        ))}
      </g>
    </svg>
  );
}
