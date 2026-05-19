import { Handle, Position, NodeProps } from "reactflow";
import Editor from "@monaco-editor/react";
import { useEffect, useRef } from "react";
import { Outputs } from "./Outputs";
import { EditableTitle } from "./EditableTitle";
import { ResizeHandle } from "./ResizeHandle";
import { useStore } from "../store";
import { executeCode, explainCode } from "../api";
import { colorFor } from "../lib/rough";

const DEFAULT_W = 580;

export function CodeCellNode({ data }: NodeProps<{ cellId: string }>) {
  const cellId = data.cellId;
  const cell = useStore((s) => s.notebook.cells.find((c) => c.id === cellId));
  const state = useStore((s) => s.cellState[cellId]);
  const size = useStore((s) => s.cellSize[cellId]);
  const updateSource = useStore((s) => s.updateCellSource);
  const updateMeta = useStore((s) => s.updateCellMeta);
  const setExec = useStore((s) => s.setExecResult);
  const setExplain = useStore((s) => s.setExplain);
  const reportCellHeight = useStore((s) => s.reportCellHeight);
  const theme = useStore((s) => s.theme);
  const dark = theme === "dark";

  const wrapRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!cell) return;
    explainCode(cell.source, "beginner", cell.meta ?? undefined)
      .then((r) => setExplain(cellId, r))
      .catch(() => {});
  }, [cell?.meta, cellId, setExplain, cell?.source, cell]);

  useEffect(() => {
    const el = wrapRef.current;
    if (!el) return;
    const ro = new ResizeObserver((entries) => {
      for (const e of entries) {
        reportCellHeight(cellId, Math.ceil(e.contentRect.height));
      }
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, [cellId, reportCellHeight]);

  if (!cell) return null;

  const cardW = size?.width ?? DEFAULT_W;
  const userH = size?.height;
  const lineCount = Math.max(6, cell.source.split("\n").length + 2);
  // If the user resized to a specific height, let the editor grow into it.
  const editorHeight = userH
    ? Math.max(120, userH - 110)
    : Math.min(420, Math.max(120, lineCount * 19));
  const innerH = (userH ?? editorHeight + 90);

  const accent = colorFor({ color: cell.meta?.color, kind: cell.meta?.kind, dark });
  const title = cell.meta?.title;

  const run = async () => {
    setExec(cellId, undefined, true);
    try {
      const r = await executeCode(cell.source);
      setExec(cellId, r, false);
    } catch (e: any) {
      setExec(
        cellId,
        { status: "error", outputs: [{ type: "error", ename: "ClientError", evalue: String(e), traceback: [] }] },
        false
      );
    }
  };

  return (
    <div ref={wrapRef} data-cell-id={cellId} style={{ width: cardW, position: "relative" }}>
      <Handle type="target" position={Position.Left} />

      <div className="doodle-card relative" style={{ minHeight: innerH, height: innerH }}>
        <div
          className="rounded-t-lg -mx-3 -mt-3 px-3 py-1.5 mb-2 border-b-2 border-ink/80 flex items-center justify-between relative"
          style={{ background: accent }}
        >
          <div className="flex items-baseline gap-2 min-w-0 flex-1">
            <EditableTitle
              value={title}
              className="font-hand text-2xl leading-tight"
              onCommit={(next) =>
                updateMeta(cellId, { ...(cell.meta ?? {}), title: next })
              }
            />
          </div>
          {/* Only the Run button stays on the card — it's a per-cell
           *  action with no toolbar equivalent. Edit Callout and Delete
           *  have moved to the toolbar's selection action bar. */}
          <div className="flex gap-1 nodrag shrink-0">
            <button
              className="font-hand text-lg w-8 h-8 rounded-lg border-2 border-ink dark:border-white/70 bg-[#b2f2bb] dark:bg-[#2b8a3e] text-ink dark:text-white hover:translate-x-[1px] hover:translate-y-[1px] transition disabled:opacity-50"
              onPointerDown={(e) => e.stopPropagation()}
              onMouseDown={(e) => e.stopPropagation()}
              onClick={(e) => { e.stopPropagation(); run(); }}
              disabled={state?.running}
              title="Run cell"
            >
              {state?.running ? "…" : "▶"}
            </button>
          </div>
        </div>
        <div
          className="rounded-lg overflow-hidden border-2 border-ink/80 nowheel nodrag"
          style={{
            borderLeftWidth: 8,
            borderLeftColor: accent,
            background: "#1e1e1e",
          }}
        >
          <Editor
            height={editorHeight}
            defaultLanguage="python"
            value={cell.source}
            onChange={(v) => updateSource(cellId, v ?? "")}
            theme="vs-dark"
            options={{
              minimap: { enabled: false },
              fontFamily: "JetBrains Mono, ui-monospace, monospace",
              fontSize: 13,
              scrollBeyondLastLine: false,
              wordWrap: "on",
              padding: { top: 8, bottom: 8 },
              mouseWheelZoom: false,
            }}
          />
        </div>
        <ResizeHandle cellId={cellId} baseWidth={cardW} baseHeight={innerH} />
      </div>

      {(state?.running || state?.outputs) && (
        <div className="mt-2 nodrag nowheel">
          {state?.running && !state.outputs && (
            <div className="font-hand text-lg text-ink/70 dark:text-white/70 px-1">
              ↳ running…
            </div>
          )}
          <Outputs result={state?.outputs} />
        </div>
      )}

      <Handle type="source" position={Position.Right} />
    </div>
  );
}

