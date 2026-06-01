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
  animation: 560,
};
const FALLBACK_H: Record<string, number> = {
  code: 260,
  markdown: 240,
  diagram: 360,
  browser: 480,
  whiteboard: 420,
  media: 320,
  animation: 240,
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

  type Seg = {
    x1: number;
    y1: number;
    x2: number;
    y2: number;
    key: string;
    /** Iter 45: links between cells render as solid sketchy lines
     *  in the doodle ink color so they're distinguishable from
     *  dashed callout chains. */
    kind: "callout" | "link";
  };
  const segments: Seg[] = [];

  // Iter 45: cell ↔ cell links. We dedupe a→b vs b→a so a symmetric
  // pair only draws once. Geometry connects the closest pair of
  // cell edges (right→left or bottom→top) so the line stays inside
  // the canvas instead of cutting diagonally through cells.
  const drawn = new Set<string>();
  const byId = new Map(cells.map((c) => [c.id, c] as const));
  for (const a of cells) {
    for (const tid of a.links ?? []) {
      const key = a.id < tid ? `${a.id}|${tid}` : `${tid}|${a.id}`;
      if (drawn.has(key)) continue;
      const b = byId.get(tid);
      if (!b) continue;
      drawn.add(key);
      const aW = a.w ?? FALLBACK_W[a.kind] ?? 560;
      const aH = a.h ?? FALLBACK_H[a.kind] ?? 280;
      const bW = b.w ?? FALLBACK_W[b.kind] ?? 560;
      const bH = b.h ?? FALLBACK_H[b.kind] ?? 280;
      // Pick edge midpoints from whichever face the centers are closest to.
      const aCx = a.x + aW / 2, aCy = a.y + aH / 2;
      const bCx = b.x + bW / 2, bCy = b.y + bH / 2;
      const dx = bCx - aCx;
      const dy = bCy - aCy;
      let x1: number, y1: number, x2: number, y2: number;
      if (Math.abs(dx) >= Math.abs(dy)) {
        // horizontal — connect right→left or left→right
        if (dx >= 0) {
          x1 = a.x + aW; y1 = aCy;
          x2 = b.x;       y2 = bCy;
        } else {
          x1 = a.x;       y1 = aCy;
          x2 = b.x + bW;  y2 = bCy;
        }
      } else {
        // vertical — connect bottom→top or top→bottom
        if (dy >= 0) {
          x1 = aCx; y1 = a.y + aH;
          x2 = bCx; y2 = b.y;
        } else {
          x1 = aCx; y1 = a.y;
          x2 = bCx; y2 = b.y + bH;
        }
      }
      segments.push({ x1, y1, x2, y2, key: `lk-${key}`, kind: "link" });
    }
  }

  for (const c of cells) {
    const list = c.callouts ?? [];
    if (!list.length) continue;
    const cellW = c.w ?? FALLBACK_W[c.kind] ?? 560;
    const cellH = c.h ?? FALLBACK_H[c.kind] ?? 280;
    const cellRightX = c.x + cellW;
    const bubbleX = c.x + cellW + CALLOUT_GAP;

    for (let i = 0; i < list.length; i++) {
      const bubbleY = c.y + i * STACK_DY;
      const bubbleMidY = bubbleY + BUBBLE_H_APPROX / 2;
      if (i === 0) {
        // Anchor the cell end at the bubble's height (clamped inside the
        // cell) so the connector runs roughly horizontal into the bubble
        // instead of slanting up from the cell's vertical middle.
        const y1 = Math.max(c.y + 12, Math.min(bubbleMidY, c.y + cellH - 12));
        segments.push({
          key: `${c.id}-c-${i}`,
          x1: cellRightX, y1,
          x2: bubbleX,    y2: bubbleMidY,
          kind: "callout",
        });
      } else {
        const prevBubbleBottom = c.y + (i - 1) * STACK_DY + BUBBLE_H_APPROX;
        segments.push({
          key: `${c.id}-c-${i}`,
          x1: bubbleX + BUBBLE_W / 2, y1: prevBubbleBottom,
          x2: bubbleX + BUBBLE_W / 2, y2: bubbleY,
          kind: "callout",
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
        {segments.map((s) =>
          s.kind === "link" ? (
            // Iter 45: cell↔cell link — solid sketchy line, doodle
            // ink color, no animation. Distinct from the dashed
            // dot-flow used for callouts.
            <line
              key={s.key}
              x1={s.x1}
              y1={s.y1}
              x2={s.x2}
              y2={s.y2}
              stroke={dark ? "#e9d8a6" : "#2a2a2a"}
              strokeWidth={2.5}
              strokeLinecap="round"
              opacity={0.85}
            />
          ) : (
            // Callout connector — a clearly-visible dotted line from the
            // cell's edge to its bubble. Denser dashes (was "1 10", which
            // read as nearly nothing) so it actually looks connected.
            <line
              key={s.key}
              x1={s.x1}
              y1={s.y1}
              x2={s.x2}
              y2={s.y2}
              stroke={dark ? "#d9c79f" : "#4a4a4a"}
              strokeWidth={2.5}
              strokeLinecap="round"
              strokeDasharray="2 5"
              opacity={0.9}
              className="doodle-connector"
            />
          ),
        )}
      </g>
    </svg>
  );
}
