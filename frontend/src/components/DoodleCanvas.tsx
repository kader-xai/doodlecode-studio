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
import { useStore } from "../store";
import type { Cell, ExplainResponse } from "../types";

const nodeTypes = { code: CodeCellNode, explain: ExplanationNode, markdown: MarkdownNode };

const CELL_COL_X = 80;
const EXPLAIN_COL_X = 740;
const EXPLAIN_GAP_Y = 140;
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
  cellHeights: Record<string, number>
): { nodes: Node[]; edges: Edge[] } {
  const nodes: Node[] = [];
  const edges: Edge[] = [];
  let y = 40;
  cells.forEach((cell, ci) => {
    const baseY = y;
    if (cell.kind === "markdown") {
      nodes.push({
        id: `cell-${cell.id}`,
        type: "markdown",
        position: { x: CELL_COL_X, y: baseY },
        data: {
          cellId: cell.id,
          source: cell.source,
          color: cell.meta?.color,
          kind: cell.meta?.kind,
          title: cell.meta?.title,
        },
        draggable: true,
      });
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
    y += estimateCellHeight(cell, calloutCount, cellHeights[cell.id]) + 60;
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
  const cellHeights = useStore((s) => s.cellHeight);
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
    () => buildGraph(cells, explainByCell, cellHeights),
    [cells, explainByCell, cellHeights]
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
    const width =
      (cell.kind === "code" && calloutCount > 0
        ? EXPLAIN_COL_X - CELL_COL_X + EXPLAIN_W
        : CARD_W) + 80;
    const height = h + 80;
    rf.fitBounds({ x, y, width, height }, { padding: 0.12, duration: 550 });
  }, [
    focused,
    presenting,
    cells,
    nodes,
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

  const onNodeClick = (_: any, node: Node) => {
    let cellId: string | null = null;
    if (node.id.startsWith("ex-")) {
      const rest = node.id.slice(3);
      cellId = rest.replace(/-\d+$/, "");
    } else if (node.id.startsWith("cell-")) {
      cellId = node.id.slice(5);
    }
    if (!cellId) return;
    focus(cellId);
    if (presenting) return; // presentation effect handles the zoom

    const cell = cells.find((c) => c.id === cellId);
    const target = nodes.find((n) => n.id === `cell-${cellId}`);
    if (!cell || !target) return;
    // Outside presentation: pan only, preserve zoom — per CLAUDE.md rule 6.
    rf.setCenter(target.position.x + 280, target.position.y + 220, {
      zoom: rf.getZoom(),
      duration: 400,
    });
  };

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onNodeClick={onNodeClick}
      nodeTypes={nodeTypes}
      defaultViewport={{ x: 0, y: 0, zoom: 0.7 }}
      minZoom={0.15}
      maxZoom={1.5}
      // Two-finger trackpad scroll on Mac (and mouse wheel anywhere) pans
      // the canvas. Cmd/Ctrl + scroll zooms. Pinch zooms (trackpad).
      // Everything off during presentation so a stray gesture can't
      // drift the canvas mid-talk.
      panOnScroll={!presenting}
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
      // Figma / Excalidraw-style automatic behavior:
      //  - drag a cell  → moves the cell
      //  - drag empty   → pans the canvas
      // Both work simultaneously, no tool switching required.
      // During presentation cells stay locked; canvas drag stays free.
      nodesDraggable={!presenting}
      panOnDrag
      nodesConnectable={false}
      elementsSelectable={!presenting}
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
