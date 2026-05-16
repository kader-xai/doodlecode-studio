import { Handle, Position, NodeProps } from "reactflow";
import Editor from "@monaco-editor/react";
import { useEffect, useRef, useState } from "react";
import { DoodleBorder } from "./DoodleBorder";
import { Outputs } from "./Outputs";
import { CalloutEditor } from "./CalloutEditor";
import { useStore } from "../store";
import { executeCode, explainCode } from "../api";
import { colorFor } from "../lib/rough";

const CARD_W = 580;

export function CodeCellNode({ id, data }: NodeProps<{ cellId: string }>) {
  const cellId = data.cellId;
  const cell = useStore((s) => s.notebook.cells.find((c) => c.id === cellId));
  const state = useStore((s) => s.cellState[cellId]);
  const updateSource = useStore((s) => s.updateCellSource);
  const setExec = useStore((s) => s.setExecResult);
  const setExplain = useStore((s) => s.setExplain);
  const reportCellHeight = useStore((s) => s.reportCellHeight);
  const theme = useStore((s) => s.theme);
  const dark = theme === "dark";
  const [editing, setEditing] = useState(false);

  const wrapRef = useRef<HTMLDivElement>(null);

  // Sync the callout into the right-side bubble when meta/source changes.
  useEffect(() => {
    if (!cell) return;
    explainCode(cell.source, "beginner", cell.meta ?? undefined)
      .then((r) => setExplain(cellId, r))
      .catch(() => {});
  }, [cell?.meta, cellId, setExplain, cell?.source, cell]);

  // Measure the actual rendered height so the canvas can place the next
  // cell below this one without overlap when outputs grow.
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

  const lineCount = Math.max(6, cell.source.split("\n").length + 2);
  const editorHeight = Math.min(420, Math.max(120, lineCount * 19));
  // The doodle border now wraps ONLY the header + editor — fixed and
  // predictable. Outputs render BELOW the border, as a sibling card.
  const innerH = editorHeight + 90;

  const accent = colorFor({ color: cell.meta?.color, kind: cell.meta?.kind, dark });
  const title = cell.meta?.title;
  const kindLabel = cell.meta?.kind || null;

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
    <div ref={wrapRef} style={{ width: CARD_W, position: "relative" }}>
      <Handle type="target" position={Position.Left} />

      {/* The doodle-bordered card: just the editor and its header. */}
      <div className="doodle-card" style={{ minHeight: innerH, height: innerH }}>
        <DoodleBorder
          width={CARD_W + 8}
          height={innerH + 8}
          fill={dark ? "#1f2228" : "#ffffff"}
          stroke={dark ? "#ececec" : "#2a2a2a"}
          seed={hashSeed(id)}
        />
        <div
          className="rounded-t-lg -mx-3 -mt-3 px-3 py-1.5 mb-2 border-b-2 border-ink/80 flex items-center justify-between relative"
          style={{ background: accent }}
        >
          <div className="flex items-baseline gap-2">
            {kindLabel && (
              <span className="font-hand text-xs uppercase tracking-wider text-ink/60">
                {kindLabel}
              </span>
            )}
            {title && <span className="font-hand text-2xl leading-none">{title}</span>}
          </div>
          <div className="flex gap-1.5 nodrag">
            <button
              className="btn-sketch sky text-base px-2 py-0.5"
              onClick={(e) => {
                e.stopPropagation();
                setEditing((v) => !v);
              }}
              title="Edit callout"
            >
              ✎
            </button>
            <button
              className="btn-sketch mint"
              onClick={(e) => {
                e.stopPropagation();
                run();
              }}
              disabled={state?.running}
            >
              {state?.running ? "…" : "▶ Run"}
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
        {editing && (
          <CalloutEditor cellId={cellId} meta={cell.meta} onClose={() => setEditing(false)} />
        )}
      </div>

      {/* Outputs sit OUTSIDE the doodle border so they're always visible
          regardless of how tall they grow. ResizeObserver above measures
          the full wrapper and reports back so the next cell auto-shifts
          down. */}
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

function hashSeed(s: string): number {
  let h = 0;
  for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) | 0;
  return Math.abs(h) % 1000;
}
