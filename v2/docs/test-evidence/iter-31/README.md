# iter 31 — cell ↔ callout connectors

## Bug

Dashed connectors (and the flowing-dot animation we wired up via
`.doodle-edge-flow .react-flow__edge-path`) were never visible. The
`<g>` inside `.react-flow__edges` rendered empty even though we were
passing 12 valid `Edge` objects to ReactFlow.

## Root cause

Discovered by reading `node_modules/@reactflow/core/dist/esm/index.js`:

```js
const [sourceNodeRect, sourceHandleBounds, sourceIsValid] = getNodeData(nodeInternals.get(edge.source));
const [targetNodeRect, targetHandleBounds, targetIsValid] = getNodeData(nodeInternals.get(edge.target));
if (!sourceIsValid || !targetIsValid) {
    return null;
}
```

`getNodeData` returns `isValid: false` unless the node has measured
`width`, `height`, `positionAbsolute`, AND `[internalsSymbol].handleBounds`.
Our synthetic callout pseudo-nodes have `<Handle>` components, but
ReactFlow's internal ResizeObserver/handle-bounds measurement never
landed for them — likely because we drive `nodes` via local
`useState` rather than going through ReactFlow's `setNodes` pipeline.
Every cell→callout edge was silently dropped.

## Fix

`v2/frontend/src/components/ConnectionsLayer.tsx` — an SVG layer
mounted inside the ReactFlow viewport that draws the connectors
ourselves. Subscribes to `useViewport()` so pan + zoom carry the
lines. Geometry is computed from `cell.x/y/w/h` and the same
callout-stack offsets the canvas uses to position the bubbles.

The CSS animation moved from `.doodle-edge-flow` →
`.doodle-connector`. Keyframe is identical: `stroke-dashoffset` from
0 to `-22` over 1 s, infinite, on a `1 10` dasharray with
`linecap: round` so the line renders as marching dots.

## Verification (in-app)

| Check | Tool | Result |
| --- | --- | --- |
| `document.querySelectorAll(".doodle-connector").length` after demo load | preview_eval | **12** ✓ |
| `getComputedStyle(conn).animationName` | preview_eval | `doodle-dash-flow` ✓ |
| `strokeDasharray` | preview_eval | `1px, 10px` ✓ |
| Console errors | preview_console_logs | **none** ✓ |
| Geometry sanity (cell right midpoint → bubble left midpoint) | preview_eval | (800,200) → (840,150) for c0 ✓ |
| Reload + reload — connectors still there | preview_eval | yes ✓ |

## Rule learned (added to CLAUDE.md)

ReactFlow's `EdgeRenderer` drops edges whose source/target node
hasn't had its handle bounds measured. With controlled `nodes` state
that lives outside ReactFlow's `setNodes`, our synthetic pseudo-nodes
never get measured. For overlays of our own (callout chains, etc.)
the safe pattern is to render a custom SVG layer inside the ReactFlow
viewport — never to rely on ReactFlow edges.
