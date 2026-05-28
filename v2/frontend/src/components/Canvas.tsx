import { useCallback, useEffect, useRef, useState } from "react";
import ReactFlow, {
  Background,
  BackgroundVariant,
  Controls,
  Node,
  NodeChange,
  NodeTypes,
  ReactFlowInstance,
  ReactFlowProvider,
  applyNodeChanges,
  useReactFlow,
} from "reactflow";
import "reactflow/dist/style.css";

import { BrowserCell } from "./BrowserCell";
import { CalloutBubble } from "./CalloutBubble";
import { CodeCell } from "./CodeCell";
import { ConnectionsLayer } from "./ConnectionsLayer";
import { DiagramCell } from "./DiagramCell";
import { MarkdownCell } from "./MarkdownCell";
import { MediaCell } from "./MediaCell";
import { WhiteboardCell } from "./WhiteboardCell";
import { useStore } from "../store";
import type { Cell } from "../types";

const nodeTypes: NodeTypes = {
  code: CodeCell,
  markdown: MarkdownCell,
  media: MediaCell,
  browser: BrowserCell,
  whiteboard: WhiteboardCell,
  diagram: DiagramCell,
  callout: CalloutBubble,
};

/** Cell widths used to right-position the callout bubble. */
const CELL_WIDTH_FALLBACK: Record<string, number> = {
  code: 580,
  markdown: 560,
  diagram: 560,
};
const CALLOUT_GAP = 40;
/** Approximate rendered width of a callout bubble — must match the
 *  `BUBBLE_W` constant in CalloutBubble.tsx. Used to grow the
 *  presentation-centering bounding box when callouts exist. */
const BUBBLE_W = 280;

/**
 * Infinite canvas. ReactFlow drives drag/selection UX; the store is
 * the source of truth.
 *
 * Drag pattern (the one that works with controlled-mode ReactFlow):
 *   - Local `nodes` state mirrors the store on every cell-shape change
 *     (add/delete/store-side move). ReactFlow reads from this.
 *   - During drag, `onNodesChange` runs `applyNodeChanges` to update
 *     local `nodes` LIVE — that's what lets the user see the card move
 *     under the cursor.
 *   - When drag ends (`change.dragging === false`), we commit the new
 *     position into the store (which then triggers autosave).
 *
 * This is the same controlled-but-locally-buffered pattern ReactFlow
 * docs recommend; doing the store write on every micro-move would
 * cause re-renders during drag and visually drop frames.
 */
export function Canvas() {
  // ReactFlowProvider gives useReactFlow + the internal store access
  // to children. Without it, controlled-mode edge sync can get stuck
  // (we saw `<g class="react-flow__edges">` rendered but empty).
  return (
    <ReactFlowProvider>
      <CanvasInner />
    </ReactFlowProvider>
  );
}

function CanvasInner() {
  const cells = useStore((s) => s.cells);
  const selectedId = useStore((s) => s.selectedId);
  const selectedIds = useStore((s) => s.selectedIds);
  const moveCell = useStore((s) => s.moveCell);
  const setSelected = useStore((s) => s.setSelected);
  const setSelectedIds = useStore((s) => s.setSelectedIds);
  const addCell = useStore((s) => s.addCell);
  const dark = useStore((s) => s.theme === "dark");
  const presenting = useStore((s) => s.presenting);
  const focusedCellId = useStore((s) => s.focusedCellId);
  const mode = useStore((s) => s.interactionMode);
  // useReactFlow gives us screenToFlowPosition — needed to translate
  // a pointer's screen coords into canvas (pre-transform) coords for
  // the dropped Media cell's position.
  const rf = useReactFlow();

  // Two-mode truth table (Figma-style):
  //   select (default) : drag cells to move; click empty pane deselects.
  //   hand             : drag empty pane to pan; cells locked.
  // Wheel pans in both modes (panOnScroll); Cmd/Ctrl+wheel zooms.
  const panOnDrag = mode === "hand";
  const nodesDraggable = mode === "select";
  const canvasCursor = mode === "hand" ? "grab" : "default";

  const instanceRef = useRef<ReactFlowInstance | null>(null);

  // Iter 52: Cmd/Ctrl+0 resets zoom to 1; Cmd/Ctrl+1 fits the whole
  // canvas. Skipped while the user is typing into a text input.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (!(e.metaKey || e.ctrlKey) || e.shiftKey || e.altKey) return;
      const tgt = e.target as Element | null;
      if (tgt?.closest("input, textarea, [contenteditable=true], .monaco-editor")) return;
      const inst = instanceRef.current;
      if (!inst) return;
      if (e.key === "0") {
        e.preventDefault();
        inst.zoomTo(1, { duration: 200 });
      } else if (e.key === "1") {
        e.preventDefault();
        inst.fitView({ padding: 0.2, duration: 250 });
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  // Pan-to-focused-cell on presentation focus changes. We center on
  // the **bounding box** of the cell PLUS any callout bubbles to its
  // right, so the slide is balanced left/right whether or not it has
  // a callout column. (The previous +120px right bias pushed
  // callout-less cells off-center to the left.)
  useEffect(() => {
    if (!presenting || !focusedCellId) return;
    const inst = instanceRef.current;
    if (!inst) return;
    const cell = cells.find((c) => c.id === focusedCellId);
    if (!cell) return;
    const w = cell.w ?? CELL_WIDTH_FALLBACK[cell.kind] ?? 560;
    const h = cell.h ?? 360;
    const hasCallouts = (cell.callouts?.length ?? 0) > 0;
    // Include the callout column in the bounding box when present
    // so both the cell and the bubble are visually balanced.
    const totalW = w + (hasCallouts ? CALLOUT_GAP + BUBBLE_W : 0);
    const cx = cell.x + totalW / 2;
    const cy = cell.y + h / 2;
    const z = inst.getZoom();
    inst.setCenter(cx, cy, { zoom: z, duration: 350 });
  }, [presenting, focusedCellId, cells]);

  // Per-cellId stable `data` object. ReactFlow passes `data` straight
  // to the user node component, and changes to its identity cause the
  // node to re-render. We keep ONE `{cellId}` object per cell so the
  // node's prop identity never flickers while the user types — which
  // is what was blurring the markdown textarea.
  const dataCacheRef = useRef<Map<string, { cellId: string }>>(new Map());
  const dataFor = (id: string) => {
    let d = dataCacheRef.current.get(id);
    if (!d) {
      d = { cellId: id };
      dataCacheRef.current.set(id, d);
    }
    return d;
  };
  // Separate cache for callout-bubble data objects (each carries an
  // `index` because a cell can host multiple bubbles).
  const calloutDataRef = useRef<Map<string, { cellId: string; index: number }>>(new Map());
  const calloutDataFor = (cellId: string, index: number) => {
    const k = `${cellId}::${index}`;
    let d = calloutDataRef.current.get(k);
    if (!d || d.index !== index || d.cellId !== cellId) {
      d = { cellId, index };
      calloutDataRef.current.set(k, d);
    }
    return d;
  };

  // Stable per-node style object too.
  const STYLE = useRef({ outline: "none" }).current;

  /** Stack of bubbles for one cell, each at the next y-offset. */
  const calloutNodesFor = (c: Cell, parentX: number, parentY: number): Node[] => {
    const list = c.callouts ?? [];
    if (!list.length) return [];
    const cellW = c.w ?? CELL_WIDTH_FALLBACK[c.kind] ?? 560;
    const x = parentX + cellW + CALLOUT_GAP;
    const STACK_DY = 200; // approximate; each bubble is ~180-200px tall
    return list.map((_, idx) => ({
      id: `${c.id}--callout-${idx}`,
      type: "callout",
      position: { x, y: parentY + idx * STACK_DY },
      data: calloutDataFor(c.id, idx),
      selected: false,
      style: STYLE,
      draggable: false,
    }));
  };

  /** Build the full node list, including derived callout bubbles. */
  const buildNodes = (): Node[] => {
    const selSet = new Set(selectedIds.length ? selectedIds : selectedId ? [selectedId] : []);
    const out: Node[] = [];
    for (const c of cells) {
      out.push({
        id: c.id,
        type: c.kind,
        position: { x: c.x, y: c.y },
        data: dataFor(c.id),
        selected: selSet.has(c.id),
        style: STYLE,
        draggable: true,
      });
      out.push(...calloutNodesFor(c, c.x, c.y));
    }
    return out;
  };

  const [nodes, setNodes] = useState<Node[]>(() => buildNodes());

  useEffect(() => {
    const selSet = new Set(
      selectedIds.length ? selectedIds : selectedId ? [selectedId] : [],
    );
    setNodes((prev) => {
      const byId = new Map(prev.map((n) => [n.id, n]));
      const out: Node[] = [];
      for (const c of cells) {
        const existing = byId.get(c.id);
        const samePos =
          existing && existing.position.x === c.x && existing.position.y === c.y;
        const sameSel = existing && existing.selected === selSet.has(c.id);
        const sameType = existing && existing.type === c.kind;
        // During presentation, give non-focused cells reduced
        // opacity so the audience's eye lands on the active slide.
        const cellStyle: React.CSSProperties =
          presenting && focusedCellId && c.id !== focusedCellId
            ? { ...STYLE, opacity: 0.35, transition: "opacity 350ms ease" }
            : presenting
            ? { ...STYLE, transition: "opacity 350ms ease" }
            : STYLE;
        if (
          existing &&
          samePos &&
          sameSel &&
          sameType &&
          existing.style === cellStyle
        ) {
          out.push(existing);
        } else {
          out.push({
            id: c.id,
            type: c.kind,
            position: samePos ? existing!.position : { x: c.x, y: c.y },
            data: dataFor(c.id),
            selected: selSet.has(c.id),
            style: cellStyle,
            draggable: true,
          });
        }
        // Append callout bubbles after each cell. Position is always
        // derived from the parent so users don't drag them manually.
        const parentPos = samePos ? existing!.position : { x: c.x, y: c.y };
        out.push(...calloutNodesFor(c, parentPos.x, parentPos.y));
      }
      return out;
    });
    // Prune the data cache for deleted cells so it doesn't leak.
    const live = new Set(cells.map((c) => c.id));
    for (const k of dataCacheRef.current.keys()) {
      if (!live.has(k)) dataCacheRef.current.delete(k);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [cells, selectedId, selectedIds, STYLE, presenting, focusedCellId]);

  // We used to derive ReactFlow edges from cell.callouts here, but
  // ReactFlow silently dropped every one of them because its
  // EdgeRenderer filters edges whose source/target nodes don't have
  // measured handle bounds — a measurement that never landed for our
  // synthetic callout pseudo-nodes. The dashed connectors are now
  // drawn by `<ConnectionsLayer />` below, which sidesteps the whole
  // ReactFlow edge pipeline.

  const onNodesChange = useCallback(
    (changes: NodeChange[]) => {
      // Live update local state so the cell visually follows the cursor
      // AND we have the authoritative post-drag position to commit.
      setNodes((curr) => {
        const next = applyNodeChanges(changes, curr);

        // Commit drag-end positions by reading from the freshly-applied
        // state. We can't just use `ch.position` because ReactFlow's
        // final `dragging:false` change sometimes arrives WITHOUT a
        // position field — only the prior dragging:true events carried
        // it. Reading `next` is the always-correct source.
        for (const ch of changes) {
          if (ch.type === "position" && ch.dragging === false) {
            // Skip synthetic callout pseudo-nodes — their position is
            // derived from the parent cell each render.
            if (ch.id.includes("--callout-")) continue;
            const node = next.find((n) => n.id === ch.id);
            if (node) moveCell(node.id, node.position.x, node.position.y);
          }
          if (ch.type === "select") {
            // Ignore synthetic callout pseudo-nodes — they're never selectable.
            if (ch.id.includes("--callout-")) continue;
            if (ch.selected) setSelected(ch.id);
            else if (useStore.getState().selectedId === ch.id) setSelected(null);
          }
        }
        // Iter 33: sync the full selection set after every change so
        // marquee + shift-click multi-selection drive group-delete and
        // visual highlight. `selectedId` is still the last-clicked
        // primary (toolbar / callout target).
        const selectedIds = next
          .filter((n) => n.selected && !n.id.includes("--callout-"))
          .map((n) => n.id);
        const prev = useStore.getState().selectedIds;
        const same =
          prev.length === selectedIds.length &&
          prev.every((id, i) => id === selectedIds[i]);
        if (!same) setSelectedIds(selectedIds);
        return next;
      });
    },
    [moveCell, setSelected, setSelectedIds],
  );

  // Iter 32: drag image files from desktop → instant Media cell.
  // We attach handlers to the wrapping div (not ReactFlow directly)
  // because ReactFlow's pane swallows drop events on its own children.
  const onDragOver = useCallback((e: React.DragEvent) => {
    if (Array.from(e.dataTransfer.items).some((it) => it.kind === "file")) {
      e.preventDefault();
      e.dataTransfer.dropEffect = "copy";
    }
  }, []);
  const onDrop = useCallback(
    (e: React.DragEvent) => {
      const f = e.dataTransfer.files?.[0];
      if (!f) return;
      e.preventDefault();
      if (!f.type.startsWith("image/")) {
        window.alert(`Only image files are supported (got ${f.type || "unknown"})`);
        return;
      }
      if (f.size > 5 * 1024 * 1024) {
        window.alert(`Image too large (${(f.size / 1024 / 1024).toFixed(1)}MB > 5MB cap)`);
        return;
      }
      const pos = rf.screenToFlowPosition({ x: e.clientX, y: e.clientY });
      const reader = new FileReader();
      reader.onload = () => {
        addCell({
          kind: "media",
          source: String(reader.result),
          x: pos.x - 240,
          y: pos.y - 160,
          w: 480,
          h: 320,
        });
      };
      reader.readAsDataURL(f);
    },
    [rf, addCell],
  );

  return (
    <div className="w-full h-full" onDragOver={onDragOver} onDrop={onDrop}>
      <ReactFlow
        nodes={nodes}
        nodeTypes={nodeTypes}
        edges={[]}
        onInit={(inst) => { instanceRef.current = inst; }}
        onNodesChange={onNodesChange}
        onPaneClick={() => setSelected(null)}
        nodesConnectable={false}
        elementsSelectable
        nodesDraggable={nodesDraggable}
        panOnDrag={panOnDrag}
        // Iter 33: drag on empty pane in Select mode draws a lasso
        // that multi-selects every cell it crosses. Shift-click adds
        // cells to the selection. In Hand mode the drag pans instead.
        selectionOnDrag={mode === "select"}
        multiSelectionKeyCode={["Shift", "Meta"]}
        panOnScroll
        zoomOnPinch
        zoomOnScroll={false}
        minZoom={0.3}
        maxZoom={2}
        defaultViewport={{ x: 0, y: 0, zoom: 1 }}
        proOptions={{ hideAttribution: true }}
        style={{ cursor: canvasCursor }}
      >
        <Background
          variant={BackgroundVariant.Dots}
          gap={24}
          size={1.5}
          color={dark ? "#3a3f47" : "#d4c89a"}
        />
        {/* Our own animated dashed connectors between cells and
         *  callouts. Mounted inside ReactFlow so it picks up the
         *  viewport (pan + zoom) via useViewport. */}
        <ConnectionsLayer />
        {!presenting && (
          <Controls
            showInteractive={false}
            className="!bg-white/80 dark:!bg-[#262a31]/80 !border-2 !border-ink/40 dark:!border-white/30 !rounded-xl"
          />
        )}
      </ReactFlow>
    </div>
  );
}

