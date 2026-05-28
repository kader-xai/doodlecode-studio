import Editor from "@monaco-editor/react";
import { useState, useEffect } from "react";
import { Handle, NodeProps, Position } from "reactflow";
import { DoodleBorder } from "./DoodleBorder";
import { EditableTitle } from "./EditableTitle";
import { Outputs } from "./Outputs";
import { useStore } from "../store";

const CARD_WIDTH = 580;

/**
 * Code cell — Monaco editor + Run button + output panel.
 *
 * All state lives in the store. Local React state is forbidden here;
 * if you find yourself wanting useState, add the field to AppState
 * instead.
 */
export function CodeCell({ data, selected }: NodeProps<{ cellId: string }>) {
  const cellId = data.cellId;
  const cell = useStore((s) => s.cells.find((c) => c.id === cellId));
  const runtime = useStore((s) => s.runtimes[cellId]);
  const setSource = useStore((s) => s.setSource);
  const setTitle = useStore((s) => s.setTitle);
  const runCell = useStore((s) => s.runCell);
  const setSelected = useStore((s) => s.setSelected);
  const theme = useStore((s) => s.theme);
  const renameTick = useStore((s) => s.renameTick[cellId] ?? 0);

  // Bridge the store-level renameTick into EditableTitle's
  // `forceEdit` boolean: when the tick bumps, flip `forceEdit` true
  // for a frame so the title enters edit mode.
  const [forceEdit, setForceEdit] = useState(false);
  useEffect(() => {
    if (renameTick > 0) {
      setForceEdit(true);
      // Reset after the EditableTitle has had a chance to read it.
      const t = setTimeout(() => setForceEdit(false), 50);
      return () => clearTimeout(t);
    }
  }, [renameTick]);

  if (!cell) return null;

  const lines = Math.max(6, cell.source.split("\n").length + 2);
  const editorHeight = Math.min(420, Math.max(120, lines * 19));

  // Selection ring uses the doodle pink, dialed back when not selected
  // so the card has a subtle resting outline instead of jumping
  // visually on click.
  const ringColor = selected ? "#c2255c" : "var(--doodle-stroke, #2a2a2a)";
  const ringWidth = selected ? 3.5 : 2.5;

  return (
    <div
      className="relative"
      style={{ width: CARD_WIDTH }}
      onClickCapture={() => setSelected(cellId)}
    >
      <Handle type="target" position={Position.Left} className="!bg-transparent !border-0" />

      <div className="relative p-3 pt-2">
        <DoodleBorder
          stroke={ringColor}
          fill={theme === "dark" ? "#262a31" : "#fff8e1"}
          strokeWidth={ringWidth}
          radius={16}
        />
        <div className="relative">
          {/* Title row.
           *  IMPORTANT: no `nodrag` on this wrapper — the title is a
           *  drag handle for ReactFlow. `nodrag` lives ONLY on the
           *  interactive children (Run button + EditableTitle's input
           *  when editing) so they keep working without locking the
           *  whole row from moving the cell. */}
          <div className="flex items-center justify-between mb-2 px-1 gap-2">
            {/* Iter 37: Jupyter-style execution counter. Shows once
             *  the cell has run at least once; gray while running so
             *  the user knows the old number is stale. */}
            {runtime?.execCount !== undefined && (
              <span
                className={
                  "font-mono text-xs px-1.5 py-0.5 rounded border-2 select-none shrink-0 " +
                  (runtime.running
                    ? "border-ink/20 dark:border-white/20 text-ink/40 dark:text-white/40"
                    : "border-ink/40 dark:border-white/40 bg-white/60 dark:bg-black/40 text-ink/70 dark:text-white/70")
                }
                title="Execution count — bumps every time the cell runs"
              >
                [{runtime.execCount}]
              </span>
            )}
            <EditableTitle
              value={cell.title}
              onCommit={(t) => setTitle(cellId, t)}
              forceEdit={forceEdit}
              className="font-hand text-2xl truncate text-ink dark:text-white flex-1 min-w-0"
            />
            <button
              onClick={(e) => { e.stopPropagation(); runCell(cellId); }}
              onPointerDown={(e) => e.stopPropagation()}
              onMouseDown={(e) => e.stopPropagation()}
              disabled={runtime?.running}
              className="font-hand text-xl px-3 py-0.5 rounded-lg border-2 border-ink dark:border-white/70 bg-marker-mint dark:bg-[#2b8a3e] text-ink dark:text-white shadow-sketch hover:translate-y-[1px] transition disabled:opacity-50 nodrag"
              title="Run this cell"
            >
              {runtime?.running ? "…" : "▶ Run"}
            </button>
          </div>

          {/* Editor — nodrag/nowheel so ReactFlow doesn't hijack scroll/drag */}
          <div className="rounded-lg overflow-hidden border-2 border-ink/70 dark:border-white/40 nowheel nodrag">
            <Editor
              height={editorHeight}
              defaultLanguage="python"
              value={cell.source}
              onChange={(v) => setSource(cellId, v ?? "")}
              theme={theme === "dark" ? "vs-dark" : "light"}
              options={{
                minimap: { enabled: false },
                fontFamily: "JetBrains Mono, ui-monospace, monospace",
                fontSize: 13,
                scrollBeyondLastLine: false,
                wordWrap: "on",
                padding: { top: 8, bottom: 8 },
                mouseWheelZoom: false,
                lineNumbersMinChars: 3,
              }}
            />
          </div>

          {/* Outputs */}
          {(runtime?.running || runtime?.result) && (
            <div className="mt-2 nodrag nowheel">
              {runtime.running && !runtime.result && (
                <div className="font-hand text-lg text-ink/70 dark:text-white/70 px-1">
                  ↳ running…
                </div>
              )}
              <Outputs result={runtime.result} />
            </div>
          )}
        </div>
      </div>

      <Handle type="source" position={Position.Right} className="!bg-transparent !border-0" />
    </div>
  );
}
