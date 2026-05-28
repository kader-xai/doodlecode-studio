import { useEffect, useMemo, useRef, useState } from "react";
import { Handle, NodeProps, Position } from "reactflow";
import { DoodleBorder } from "./DoodleBorder";
import { EditableTitle } from "./EditableTitle";
import { renderMarkdown } from "../lib/markdown";
import { useStore } from "../store";

const CARD_WIDTH = 560;

/**
 * Markdown cell.
 *
 * Two modes:
 *   - **view** (default) — renders headings/lists/bold/code via
 *     `renderMarkdown`. Click body to enter edit mode (Enter
 *     keyboard while selected also works).
 *   - **edit** — textarea sized to content. Esc or click outside
 *     commits and returns to view. The store is updated on every
 *     keystroke (matching code-cell live editing).
 *
 * No per-cell delete/edit buttons. Toolbar is the only place for
 * those (consistent with the v1 lesson learned the hard way).
 */
export function MarkdownCell({ data, selected }: NodeProps<{ cellId: string }>) {
  const cellId = data.cellId;
  const cell = useStore((s) => s.cells.find((c) => c.id === cellId));
  const setSource = useStore((s) => s.setSource);
  const setTitle = useStore((s) => s.setTitle);
  const setSelected = useStore((s) => s.setSelected);
  const toggleCollapse = useStore((s) => s.toggleCollapse);
  const theme = useStore((s) => s.theme);
  const renameTick = useStore((s) => s.renameTick[cellId] ?? 0);

  const [editing, setEditing] = useState(false);
  // Local draft state so typing in the textarea does NOT round-trip
  // through the store on every keystroke. Big stability win: prevents
  // the Canvas → ReactFlow → node re-render storm that was blurring
  // the textarea after a short delay. We commit to the store on blur,
  // Esc, ✓ Done, or when the user leaves edit mode any other way.
  const [draft, setDraft] = useState(cell?.source ?? "");
  const taRef = useRef<HTMLTextAreaElement>(null);

  // F2 → rename title (same bridge pattern as CodeCell).
  const [forceEditTitle, setForceEditTitle] = useState(false);
  useEffect(() => {
    if (renameTick > 0) {
      setForceEditTitle(true);
      const t = setTimeout(() => setForceEditTitle(false), 50);
      return () => clearTimeout(t);
    }
  }, [renameTick]);

  // Sync the draft from the store when entering edit mode OR when the
  // store source changes externally while we're NOT editing (e.g.,
  // Open file, undo from elsewhere).
  useEffect(() => {
    if (!editing) setDraft(cell?.source ?? "");
  }, [cell?.source, editing]);

  // Focus the textarea when entering edit mode + place caret at end.
  useEffect(() => {
    if (editing) {
      taRef.current?.focus();
      const ta = taRef.current;
      if (ta) ta.setSelectionRange(ta.value.length, ta.value.length);
    }
  }, [editing]);

  const rendered = useMemo(() => renderMarkdown(cell?.source ?? ""), [cell?.source]);
  if (!cell) return null;

  const enterEdit = () => {
    setDraft(cell.source);
    setEditing(true);
  };
  const commitAndClose = () => {
    if (draft !== cell.source) setSource(cellId, draft);
    setEditing(false);
  };

  const ringColor = selected ? "#c2255c" : "var(--doodle-stroke, #2a2a2a)";
  const ringWidth = selected ? 3.5 : 2.5;
  const fill = theme === "dark" ? "#262a31" : "#fff5e6";

  return (
    <div
      className="relative"
      style={{ width: CARD_WIDTH }}
      onClickCapture={() => setSelected(cellId)}
    >
      <Handle type="target" position={Position.Left} className="!bg-transparent !border-0" />

      <div className="relative p-3 pt-2">
        <DoodleBorder stroke={ringColor} fill={fill} strokeWidth={ringWidth} radius={16} />
        <div className="relative">
          {/* Title row — no `nodrag` so the title acts as a drag handle.
           *  Only the Edit button below carries `nodrag`. */}
          <div className="flex items-center justify-between mb-2 px-1 gap-2">
            {/* Iter 55: collapse chevron — mirrors CodeCell. Hides
             *  the rendered preview / textarea when collapsed. */}
            <button
              type="button"
              onClick={(e) => { e.stopPropagation(); toggleCollapse(cellId); }}
              onPointerDown={(e) => e.stopPropagation()}
              onMouseDown={(e) => e.stopPropagation()}
              className="font-mono text-sm w-5 h-5 leading-none rounded border-2 border-ink/30 dark:border-white/30 bg-white/60 dark:bg-black/40 text-ink/70 dark:text-white/70 hover:bg-marker-yellow/50 dark:hover:bg-amber-700/30 transition nodrag shrink-0"
              title={cell.collapsed ? "Expand cell" : "Collapse cell"}
            >
              {cell.collapsed ? "▸" : "▾"}
            </button>
            <EditableTitle
              value={cell.title}
              onCommit={(t) => setTitle(cellId, t)}
              forceEdit={forceEditTitle}
              className="font-hand text-2xl truncate text-ink dark:text-white flex-1 min-w-0"
            />
            <button
              // `preventDefault` on mousedown keeps the textarea focused
              // so onBlur doesn't fire BEFORE this click, which would
              // race and re-open edit mode. `nodrag` lets the click
              // through ReactFlow's drag detection.
              onMouseDown={(e) => { e.preventDefault(); e.stopPropagation(); }}
              onPointerDown={(e) => e.stopPropagation()}
              onClick={(e) => {
                e.stopPropagation();
                if (editing) commitAndClose();
                else enterEdit();
              }}
              className="nodrag font-hand text-base px-2 py-0.5 rounded-lg border-2 border-ink dark:border-white/70 bg-white/80 dark:bg-[#1f2228] text-ink dark:text-white shadow-sketch hover:translate-y-[1px] transition"
              title={editing ? "Stop editing (Esc)" : "Edit markdown"}
            >
              {editing ? "✓ Done" : "✏️ Edit"}
            </button>
          </div>

          {/* Iter 55: hide body when collapsed. Title strip stays. */}
          {cell.collapsed ? null : editing ? (
            <textarea
              ref={taRef}
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              onBlur={commitAndClose}
              onKeyDown={(e) => {
                // Don't let global shortcuts steal keys while typing.
                e.stopPropagation();
                if (e.key === "Escape") {
                  e.preventDefault();
                  commitAndClose();
                }
              }}
              onClick={(e) => e.stopPropagation()}
              onPointerDown={(e) => e.stopPropagation()}
              spellCheck={false}
              className="w-full font-mono text-sm leading-relaxed p-2 rounded-lg border-2 border-ink/60 dark:border-white/30 bg-white dark:bg-[#1f2228] text-ink dark:text-white nodrag nowheel"
              style={{ minHeight: 160, resize: "vertical" }}
            />
          ) : (
            <div
              className="px-1 nodrag"
              onDoubleClick={(e) => { e.stopPropagation(); enterEdit(); }}
              title="Double-click to edit"
            >
              {rendered.length ? rendered : (
                <p className="font-hand text-lg text-ink/50 dark:text-white/50 italic">
                  (empty — double-click to edit)
                </p>
              )}
            </div>
          )}
        </div>
      </div>

      <Handle type="source" position={Position.Right} className="!bg-transparent !border-0" />
    </div>
  );
}
