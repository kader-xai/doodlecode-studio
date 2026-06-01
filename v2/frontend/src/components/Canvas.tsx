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

import { AnimationCell } from "./AnimationCell";
import { BrowserCell } from "./BrowserCell";
import { CalloutBubble } from "./CalloutBubble";
import { CodeCell } from "./CodeCell";
import { ConnectionsLayer } from "./ConnectionsLayer";
import { DiagramCell } from "./DiagramCell";
import { MarkdownCell } from "./MarkdownCell";
import { MediaCell } from "./MediaCell";
import { WhiteboardCell } from "./WhiteboardCell";
import { useStore } from "../store";
import { slideCenter } from "../lib/present";
import type { Cell } from "../types";

const nodeTypes: NodeTypes = {
  code: CodeCell,
  markdown: MarkdownCell,
  media: MediaCell,
  browser: BrowserCell,
  whiteboard: WhiteboardCell,
  diagram: DiagramCell,
  animation: AnimationCell,
  callout: CalloutBubble,
};

/** Cell widths used to right-position the callout bubble. */
const CELL_WIDTH_FALLBACK: Record<string, number> = {
  code: 580,
  markdown: 560,
  diagram: 560,
  animation: 560,
};
/** Approx cell heights, for vertically centering a slide when the cell
 *  has no explicit height yet. */
const CELL_HEIGHT_FALLBACK: Record<string, number> = {
  code: 360,
  markdown: 220,
  diagram: 360,
  media: 360,
  browser: 480,
  whiteboard: 420,
  animation: 240,
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
  // During presentation everything is locked in place: cells can't be
  // dragged and the canvas can't be panned, so the focused slide stays
  // centered (owner request). Resizing still works — the resize grip has
  // its own pointer handling. Outside presentation, the Figma-style
  // mode truth table applies.
  const panOnDrag = !presenting && mode === "hand";
  const nodesDraggable = !presenting && mode === "select";
  const canvasCursor = !presenting && mode === "hand" ? "grab" : "default";

  const instanceRef = useRef<ReactFlowInstance | null>(null);
  // Flips true once ReactFlow's `onInit` fires, so the first-load centering
  // effect re-runs when the instance is actually available (iter 236).
  const [rfReady, setRfReady] = useState(false);

  // Iter 62: pan to a cell when the palette picks it. The store
  // bumps `panToTick` on every pick; this effect centers on the new
  // selected cell at the current zoom level (animated).
  const panToTick = useStore((s) => s.panToTick);
  useEffect(() => {
    if (panToTick === 0) return; // skip the initial render
    const st = useStore.getState();
    const sid = st.selectedId;
    if (!sid) return;
    const c = st.cells.find((cc) => cc.id === sid);
    const inst = instanceRef.current;
    if (!c || !inst) return;
    const w = c.w ?? (c.kind === "code" ? 580 : 560);
    const h = c.h ?? 360;
    inst.setCenter(c.x + w / 2, c.y + h / 2, { zoom: inst.getZoom(), duration: 350 });
  }, [panToTick]);

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

  // Pan-to-focused-cell on presentation focus changes.
  //
  // The focused slide is centered DEAD-CENTER in the viewport (both
  // axes), at the user's current zoom. Horizontally we center on the
  // bounding box of the cell PLUS any callout bubbles to its right so a
  // cell+callout pair reads balanced; vertically on the cell midpoint.
  // (Per owner request: every slide sits in the middle of the screen.)
  //
  // Deps key on the focused cell's POSITION, not the whole `cells` array,
  // so re-centering fires on navigation and moves but NOT on every
  // resize tick — otherwise resizing a slide mid-talk spammed `setCenter`
  // with competing 350ms animations (jank).
  const focusedCell = presenting
    ? cells.find((c) => c.id === focusedCellId)
    : undefined;
  const focusedX = focusedCell?.x;
  const focusedY = focusedCell?.y;
  useEffect(() => {
    if (!presenting || !focusedCellId) return;
    const inst = instanceRef.current;
    if (!inst) return;
    const cell = cells.find((c) => c.id === focusedCellId);
    if (!cell) return;
    const w = cell.w ?? CELL_WIDTH_FALLBACK[cell.kind] ?? 560;
    const h = cell.h ?? CELL_HEIGHT_FALLBACK[cell.kind] ?? 360;
    const hasCallouts = (cell.callouts?.length ?? 0) > 0;
    const { cx, cy } = slideCenter(
      cell.x,
      cell.y,
      w,
      h,
      hasCallouts ? CALLOUT_GAP + BUBBLE_W : 0,
    );
    inst.setCenter(cx, cy, { zoom: inst.getZoom(), duration: 350 });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [presenting, focusedCellId, focusedX, focusedY]);

  // On first load, center the opening slide in the middle of the screen
  // at 100% zoom — never a zoomed-out "fit everything" view. Re-runs when
  // the ReactFlow instance becomes ready (`rfReady`), because `onInit`
  // often fires AFTER this effect's first pass — without that dependency
  // the instance is still null, the effect bails, and (since cells loaded
  // from localStorage never change again) the deck is left pinned at the
  // canvas origin / far-left. (iter 236)
  const didInitialCenter = useRef(false);
  const centerFirstCell = useCallback(() => {
    if (didInitialCenter.current) return;
    const inst = instanceRef.current;
    const cs = useStore.getState().cells;
    if (!inst || cs.length === 0) return;
    didInitialCenter.current = true;
    const ordered = useStore.getState().cellsInOrder();
    const c = ordered[0] ?? cs[0];
    const w = c.w ?? CELL_WIDTH_FALLBACK[c.kind] ?? 560;
    const h = c.h ?? CELL_HEIGHT_FALLBACK[c.kind] ?? 360;
    const { cx, cy } = slideCenter(c.x, c.y, w, h);
    // Defer one frame so the flow container has its real width/height —
    // setCenter divides by them, and they can read 0 at the init tick.
    requestAnimationFrame(() => inst.setCenter(cx, cy, { zoom: 1, duration: 0 }));
  }, []);
  useEffect(() => {
    centerFirstCell();
  }, [cells, rfReady, centerFirstCell]);

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
            // `undefined` defers to the global `nodesDraggable` prop
            // (mode-aware). While presenting we force `false` so a slide
            // can't be dragged out of place. A hardcoded `true` here used
            // to override the global, keeping slides draggable mid-talk.
            draggable: presenting ? false : undefined,
            // Iter 169: gentle entrance animation when this cell becomes
            // the focused slide during presentation. The class targets
            // the cell's inner content (not the ReactFlow node wrapper,
            // whose transform carries pan/zoom) so it never fights the
            // viewport transform. Re-triggers each time focus lands here
            // because the style change above already forces a rebuild.
            className:
              presenting && focusedCellId === c.id ? "slide-enter" : undefined,
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
  const loadNotebookFromText = useStore((s) => s.loadNotebookFromText);
  const setNotebookName = useStore((s) => s.setNotebookName);
  const onDrop = useCallback(
    (e: React.DragEvent) => {
      const f = e.dataTransfer.files?.[0];
      if (!f) return;
      e.preventDefault();
      // Iter 81: .py drop opens the file as a notebook. Confirm
      // before clobbering the current canvas (matches the File →
      // Open flow's affordance).
      if (f.name.endsWith(".py")) {
        // Iter 97: cap notebook size at 10 MB. Notebooks with that
        // many embedded callout images can technically reach a few
        // MB; 10 MB is a generous ceiling that still blocks the
        // truly broken inputs that'd stall FileReader.
        if (f.size > 10 * 1024 * 1024) {
          window.alert(`File too large (${(f.size / 1024 / 1024).toFixed(1)}MB > 10MB cap)`);
          return;
        }
        if (!window.confirm(`Open "${f.name}" as a notebook? Current canvas will be replaced.`)) {
          return;
        }
        const reader = new FileReader();
        reader.onload = () => {
          loadNotebookFromText(String(reader.result))
            .then(() => {
              const name = f.name.replace(/\.py$/, "");
              if (name) setNotebookName(name);
            })
            .catch((err) => window.alert(`Could not open: ${err}`));
        };
        reader.readAsText(f);
        return;
      }
      if (!f.type.startsWith("image/")) {
        window.alert(`Only image files and .py notebooks are supported (got ${f.type || f.name})`);
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
    [rf, addCell, loadNotebookFromText, setNotebookName],
  );

  return (
    <div className="w-full h-full" onDragOver={onDragOver} onDrop={onDrop}>
      <ReactFlow
        nodes={nodes}
        nodeTypes={nodeTypes}
        edges={[]}
        onInit={(inst) => { instanceRef.current = inst; setRfReady(true); }}
        onNodesChange={onNodesChange}
        onPaneClick={() => setSelected(null)}
        nodesConnectable={false}
        elementsSelectable
        nodesDraggable={nodesDraggable}
        panOnDrag={panOnDrag}
        // Iter 33: drag on empty pane in Select mode draws a lasso
        // that multi-selects every cell it crosses. Shift-click adds
        // cells to the selection. In Hand mode the drag pans instead.
        selectionOnDrag={!presenting && mode === "select"}
        multiSelectionKeyCode={["Shift", "Meta"]}
        panOnScroll={!presenting}
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

