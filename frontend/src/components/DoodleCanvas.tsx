import { useMemo, useEffect } from "react";
import ReactFlow, {
  Background,
  BackgroundVariant,
  Controls,
  MiniMap,
  Edge,
  Node,
  useNodesState,
  useEdgesState,
  ReactFlowProvider,
  useReactFlow,
  PanOnScrollMode,
} from "reactflow";
import { CodeCellNode } from "./CodeCellNode";
import { ExplanationNode } from "./ExplanationNode";
import { MarkdownNode } from "./MarkdownNode";
import { BrowserNode } from "./BrowserNode";
import { WhiteboardNode } from "./WhiteboardNode";
import { useStore } from "../store";
import type { Cell, ExplainResponse } from "../types";

const nodeTypes = {
  code: CodeCellNode,
  explain: ExplanationNode,
  markdown: MarkdownNode,
  browser: BrowserNode,
  whiteboard: WhiteboardNode,
};

const CELL_COL_X = 80;
const EXPLAIN_COL_X = 740;
const EXPLAIN_GAP_Y = 140;
// Phantom right-side buffer added to focus regions so that when the
// viewport centers the cell+callout cluster, the cluster lands LEFT of
// dead-center and the right-most callout doesn't get clipped on
// narrower screens. Tuning knob — bigger = more left shift.
const FOCUS_RIGHT_BUFFER = 260;
const MARKDOWN_BASE_H = 200;
const CODE_BASE_H = 460;
const CARD_W = 580;
const EXPLAIN_W = 320;

function estimateCellHeight(
  cell: Cell,
  calloutCount: number,
  measured?: number
): number {
  // Always make room for the right-side callout column too.
  const calloutsH = calloutCount > 0 ? 100 + calloutCount * EXPLAIN_GAP_Y : 0;
  if (measured && measured > 0) {
    // ResizeObserver gave us the actual rendered cell height (which
    // includes the outputs panel under the card). Use it directly.
    return Math.max(measured, calloutsH);
  }
  if (cell.kind === "markdown") {
    return Math.max(MARKDOWN_BASE_H, Math.ceil(cell.source.length / 50) * 26 + 80);
  }
  const lines = Math.max(6, cell.source.split("\n").length + 2);
  const codeH = CODE_BASE_H + Math.min(220, lines * 4);
  return Math.max(codeH, calloutsH);
}

function buildGraph(
  cells: Cell[],
  explainByCell: Record<string, ExplainResponse | undefined>,
  cellHeights: Record<string, number>,
  positionOverrides: Record<string, { x: number; y: number }> | null
): { nodes: Node[]; edges: Edge[] } {
  const nodes: Node[] = [];
  const edges: Edge[] = [];
  let y = 40;
  cells.forEach((cell, ci) => {
    const override = positionOverrides?.[cell.id];
    const baseY = override?.y ?? y;
    if (cell.kind === "markdown") {
      // Dispatch on cell.meta.cell_type so v2.2 cell variants
      // (browser / whiteboard) render with their specialized
      // components while plain markdown keeps the original path.
      const variant = cell.meta?.cell_type;
      const nodeType =
        variant === "browser" ? "browser"
        : variant === "whiteboard" ? "whiteboard"
        : "markdown";
      nodes.push({
        id: `cell-${cell.id}`,
        type: nodeType,
        position: { x: CELL_COL_X, y: baseY },
        data: {
          cellId: cell.id,
          source: cell.source,
          color: cell.meta?.color,
          kind: cell.meta?.kind,
          title: cell.meta?.title,
          // The text-box body shows `box_image` (the 📝 Edit field).
          // The right-side callout bubble keeps using `image`. Distinct
          // fields = no double-showing.
          image: cell.meta?.box_image,
        },
        draggable: true,
      });
      // Markdown cells can also carry callouts (v0.4+).
      const ex = explainByCell[cell.id];
      if (ex) {
        ex.explanations.forEach((e, ei) => {
          const id = `ex-${cell.id}-${ei}`;
          nodes.push({
            id,
            type: "explain",
            position: { x: EXPLAIN_COL_X, y: baseY + ei * EXPLAIN_GAP_Y },
            data: {
              cellId: cell.id,
              index: ei,
              title: e.title,
              body: e.body,
              kind: e.tags?.[0] ?? "expr",
              color: e.color,
              image: e.image,
            },
            draggable: true,
          });
          edges.push({
            id: `e-${id}`,
            source: `cell-${cell.id}`,
            target: id,
            type: "default",
            animated: true,
            style: { stroke: "#444", strokeWidth: 2 },
          });
        });
      }
    } else {
      nodes.push({
        id: `cell-${cell.id}`,
        type: "code",
        position: { x: CELL_COL_X, y: baseY },
        data: { cellId: cell.id },
        draggable: true,
      });
      const ex = explainByCell[cell.id];
      if (ex) {
        ex.explanations.forEach((e, ei) => {
          const id = `ex-${cell.id}-${ei}`;
          nodes.push({
            id,
            type: "explain",
            position: { x: EXPLAIN_COL_X, y: baseY + ei * EXPLAIN_GAP_Y },
            data: {
              cellId: cell.id,
              index: ei,
              title: e.title,
              body: e.body,
              kind: e.tags?.[0] ?? "expr",
              color: e.color,
              image: e.image,
            },
            draggable: true,
          });
          edges.push({
            id: `e-${id}`,
            source: `cell-${cell.id}`,
            target: id,
            type: "default",
            animated: true,
            style: { stroke: "#444", strokeWidth: 2 },
          });
        });
      }
    }
    if (ci > 0) {
      edges.push({
        id: `chain-${ci}`,
        source: `cell-${cells[ci - 1].id}`,
        target: `cell-${cell.id}`,
        type: "smoothstep",
        style: { stroke: "#9b9586", strokeWidth: 1.5, opacity: 0.55 },
      });
    }
    const calloutCount = explainByCell[cell.id]?.explanations.length ?? 0;
    const h = estimateCellHeight(cell, calloutCount, cellHeights[cell.id]) + 60;
    // When the layout is overridden (Auto-Space mode) keep y in sync
    // for any cell that ISN'T in the override map — but normally every
    // cell IS in the map and we just consume the override y above.
    y = override ? override.y + h : y + h;
  });
  return { nodes, edges };
}

function CanvasInner() {
  const cells = useStore((s) => s.notebook.cells);
  const cellState = useStore((s) => s.cellState);
  const focused = useStore((s) => s.focusedCellId);
  const presenting = useStore((s) => s.presenting);
  const focus = useStore((s) => s.focus);
  const theme = useStore((s) => s.theme);
  const mode = useStore((s) => s.interactionMode);
  const setOpenEditor = useStore((s) => s.setOpenEditor);
  const cellHeights = useStore((s) => s.cellHeight);
  const positionOverrides = useStore((s) => s.cellPositionOverrides);
  const fullscreen = useStore((s) => s.fullscreen);
  // Subscribe to the focused cell's measured height + output so the
  // present-mode fit-bounds effect re-runs when the user clicks Run
  // and the box grows downward to make room for stdout.
  const focusedHeight = useStore((s) => (focused ? s.cellHeight[focused] : undefined));
  const focusedHasOutputs = useStore(
    (s) => !!(focused && s.cellState[focused]?.outputs)
  );
  const dotColor = theme === "dark" ? "#262931" : "#cdbf94";

  const explainByCell = useMemo(() => {
    const m: Record<string, ExplainResponse | undefined> = {};
    for (const c of cells) m[c.id] = cellState[c.id]?.explain;
    return m;
  }, [cells, cellState]);

  const initial = useMemo(
    () => buildGraph(cells, explainByCell, cellHeights, positionOverrides),
    [cells, explainByCell, cellHeights, positionOverrides]
  );
  const [nodes, setNodes, onNodesChange] = useNodesState(initial.nodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initial.edges);

  useEffect(() => {
    setNodes(initial.nodes);
    setEdges(initial.edges);
  }, [initial, setNodes, setEdges]);

  const rf = useReactFlow();

  // Auto-fit the focused cell during presentation: include the cell + its
  // callouts in the bounds and let ReactFlow pick the zoom that fits.
  // Re-fires when the focused cell's measured height or outputs change
  // (i.e. the user clicked Run and stdout pushed the card taller).
  useEffect(() => {
    if (!presenting || !focused) return;
    const cell = cells.find((c) => c.id === focused);
    const node = nodes.find((n) => n.id === `cell-${focused}`);
    if (!cell || !node) return;
    const calloutCount = explainByCell[cell.id]?.explanations.length ?? 0;
    const h = estimateCellHeight(cell, calloutCount, cellHeights[cell.id]);
    const x = node.position.x - 40;
    const y = node.position.y - 40;
    // Cell variants (whiteboard / browser / media-only) render wider
    // than the default CARD_W. Use the cell's ACTUAL rendered width if
    // we have it tracked in cellSize; otherwise fall back to known
    // defaults per cell type. This keeps the focus region centered on
    // the actual node rather than its left half.
    const sizeMap = useStore.getState().cellSize;
    const variant = cell.meta?.cell_type;
    const isMediaOnlyMd =
      cell.kind === "markdown" &&
      !!cell.source &&
      /^!\[[^\]]*\]\([^)]+\)$/.test(cell.source.trim());
    const cardW =
      sizeMap[cell.id]?.width ??
      (variant === "browser" ? 1280
        : variant === "whiteboard" ? 1100
        : isMediaOnlyMd ? 720
        : CARD_W);

    // Two layouts:
    //   * If the slide HAS callouts → keep the right-side buffer so the
    //     bubbles aren't clipped on narrower screens.
    //   * If the slide has NO callouts → tight region around the card
    //     itself: it stays centered (no leftward shift) AND lands
    //     bigger on screen because fitBounds picks a higher zoom.
    const hasCallouts = calloutCount > 0;
    const width = hasCallouts
      ? cardW + 80 + FOCUS_RIGHT_BUFFER
      : cardW + 40;
    const height = h + 80;
    const padding = hasCallouts
      ? (fullscreen ? 0.06 : 0.12)
      : (fullscreen ? 0.04 : 0.08);
    // Tighter padding in fullscreen so the cell fills more of the screen.
    rf.fitBounds(
      { x, y, width, height },
      { padding, duration: 550 }
    );
  }, [
    focused,
    presenting,
    cells,
    nodes,
    fullscreen,
    rf,
    explainByCell,
    cellHeights,
    focusedHeight,
    focusedHasOutputs,
  ]);

  // On notebook open or cell-count change, pan to cell #1 at current zoom.
  // Keyed off the first cell's id so plain edits don't re-pan.
  const firstCellId = cells[0]?.id;
  useEffect(() => {
    if (!firstCellId) return;
    const first = nodes.find((n) => n.id === `cell-${firstCellId}`);
    if (first) {
      rf.setCenter(first.position.x + 280, first.position.y + 220, {
        zoom: rf.getZoom(),
        duration: 0,
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [firstCellId]);

  const resolveCellId = (node: Node): string | null => {
    if (node.id.startsWith("ex-")) return node.id.slice(3).replace(/-\d+$/, "");
    if (node.id.startsWith("cell-")) return node.id.slice(5);
    return null;
  };

  const setSelection = useStore((s) => s.setSelection);

  const onNodeClick = (_: any, node: Node) => {
    const cellId = resolveCellId(node);
    if (!cellId) return;
    focus(cellId);

    // Selection drives the toolbar action bar (Edit / Delete).
    if (node.id.startsWith("ex-")) {
      const idxStr = node.id.match(/-(\d+)$/)?.[1];
      const index = idxStr ? parseInt(idxStr, 10) : 0;
      setSelection({ type: "callout", cellId, index });
    } else {
      setSelection({ type: "cell", cellId });
    }

    if (presenting) return;

    const target = nodes.find((n) => n.id === `cell-${cellId}`);
    if (!target) return;
    rf.setCenter(target.position.x + 280, target.position.y + 220, {
      zoom: rf.getZoom(),
      duration: 400,
    });
  };

  // Click on empty canvas clears the selection so the action bar hides.
  const onPaneClick = () => setSelection(null);

  // Double-click opens the right editor — callout for code cells and
  // explanation bubbles, text editor for markdown cells. Works in
  // cursor / hand / move modes alike.
  const onNodeDoubleClick = (_: any, node: Node) => {
    const cellId = resolveCellId(node);
    if (!cellId) return;
    const cell = cells.find((c) => c.id === cellId);
    if (!cell) return;
    if (node.id.startsWith("ex-")) {
      setOpenEditor({ kind: "callout", cellId });
    } else if (cell.kind === "markdown") {
      setOpenEditor({ kind: "text", cellId });
    } else {
      setOpenEditor({ kind: "callout", cellId });
    }
  };

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onNodeClick={onNodeClick}
      onNodeDoubleClick={onNodeDoubleClick}
      onPaneClick={onPaneClick}
      nodeTypes={nodeTypes}
      defaultViewport={{ x: 0, y: 0, zoom: 0.7 }}
      minZoom={0.15}
      maxZoom={1.5}
      // Two-finger trackpad scroll on Mac (and mouse wheel anywhere) pans
      // the canvas. Cmd/Ctrl + scroll zooms. Pinch zooms (trackpad).
      // During presentation we KEEP panning (trackpad / hand-drag) so the
      // presenter can browse, but we LOCK zoom so a stray pinch can't
      // wreck a carefully-fit slide. Arrow keys still trigger auto-fit
      // to the next/prev cell.
      panOnScroll
      panOnScrollMode={PanOnScrollMode.Free}
      panOnScrollSpeed={0.9}
      zoomOnScroll={!presenting}
      zoomActivationKeyCode={["Meta", "Control"]}
      zoomOnPinch={!presenting}
      zoomOnDoubleClick={!presenting}
      preventScrolling
      noWheelClassName="nowheel"
      selectionOnDrag={false}
      panActivationKeyCode={null}
      deleteKeyCode={null}
      selectionKeyCode={null}
      multiSelectionKeyCode={null}
      proOptions={{ hideAttribution: true }}
      // Three explicit tools (V / H / M):
      //   cursor → click selects, double-click edits, no drag.
      //   hand   → drag pans the canvas (works in presentation too).
      //   move   → drag moves cells.
      // Presentation locks cell-drag (no accidental moves), but hand-tool
      // dragging stays available — explicit user ask.
      nodesDraggable={!presenting && mode === "move"}
      panOnDrag={mode === "hand"}
      nodesConnectable={false}
      elementsSelectable={!presenting}
      className={
        !presenting && mode === "hand"
          ? "cursor-grab active:cursor-grabbing"
          : !presenting && mode === "move"
          ? "cursor-move"
          : ""
      }
    >
      <Background variant={BackgroundVariant.Dots} gap={22} size={1.2} color={dotColor} />
      <Controls showInteractive={false} />
      <MiniMap pannable zoomable className="!bg-paper" maskColor="rgba(253,247,230,0.6)" />
    </ReactFlow>
  );
}

export function DoodleCanvas() {
  return (
    <ReactFlowProvider>
      <CanvasInner />
    </ReactFlowProvider>
  );
}
