import { useEffect, useMemo, useRef, useState } from "react";
import { Handle, NodeProps, Position } from "reactflow";
import { DoodleBorder } from "./DoodleBorder";
import { EditableTitle } from "./EditableTitle";
import { frameAt, normalizeTransition, parseFrames } from "../lib/animation";
import { useStore } from "../store";

const CARD_WIDTH = 560;

/**
 * Animation cell (iter 225). Holds an ordered list of frames (one per
 * line in `source`). During presentation each Space/→ advances
 * `revealStep[cellId]` and the cell transitions to the next frame
 * (transition style from `cell.transition`; wired fully in iter 227).
 *
 * - **present mode** — shows the single active frame, re-keyed by step so
 *   the entrance animation re-fires on each advance.
 * - **edit mode (default canvas)** — shows the whole numbered frame list
 *   so the author sees the sequence; ✏️ Edit opens an inline textarea
 *   (one frame per line). The dedicated authoring modal lands in iter 228.
 */
export function AnimationCell({ data, selected }: NodeProps<{ cellId: string }>) {
  const cellId = data.cellId;
  const cell = useStore((s) => s.cells.find((c) => c.id === cellId));
  const setSource = useStore((s) => s.setSource);
  const setTitle = useStore((s) => s.setTitle);
  const setSelected = useStore((s) => s.setSelected);
  const toggleCollapse = useStore((s) => s.toggleCollapse);
  const theme = useStore((s) => s.theme);
  const presenting = useStore((s) => s.presenting);
  const step = useStore((s) => s.revealStep[cellId] ?? 0);
  const renameTick = useStore((s) => s.renameTick[cellId] ?? 0);

  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(cell?.source ?? "");
  const taRef = useRef<HTMLTextAreaElement>(null);

  const [forceEditTitle, setForceEditTitle] = useState(false);
  useEffect(() => {
    if (renameTick > 0) {
      setForceEditTitle(true);
      const t = setTimeout(() => setForceEditTitle(false), 50);
      return () => clearTimeout(t);
    }
  }, [renameTick]);

  useEffect(() => {
    if (!editing) setDraft(cell?.source ?? "");
  }, [cell?.source, editing]);

  useEffect(() => {
    if (editing) {
      taRef.current?.focus();
      const ta = taRef.current;
      if (ta) ta.setSelectionRange(ta.value.length, ta.value.length);
    }
  }, [editing]);

  const frames = useMemo(() => parseFrames(cell?.source ?? ""), [cell?.source]);
  if (!cell) return null;

  const transition = normalizeTransition(cell.transition);
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

  const total = frames.length;
  const activeIdx = total ? Math.max(0, Math.min(step, total - 1)) : 0;

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
          <div className="flex items-center justify-between mb-2 px-1 gap-2">
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
            <span
              className="font-hand text-xs px-2 py-0.5 rounded-full border-2 border-ink/30 dark:border-white/30 text-ink/60 dark:text-white/60 shrink-0"
              title="Transition style"
            >
              🎞 {transition}
            </span>
            {!cell.collapsed && (
              <button
                onMouseDown={(e) => { e.preventDefault(); e.stopPropagation(); }}
                onPointerDown={(e) => e.stopPropagation()}
                onClick={(e) => {
                  e.stopPropagation();
                  if (editing) commitAndClose();
                  else enterEdit();
                }}
                className="nodrag font-hand text-base px-2 py-0.5 rounded-lg border-2 border-ink dark:border-white/70 bg-white/80 dark:bg-[#1f2228] text-ink dark:text-white shadow-sketch hover:translate-y-[1px] transition"
                title={editing ? "Stop editing (Esc)" : "Edit frames"}
              >
                {editing ? "✓ Done" : "✏️ Edit"}
              </button>
            )}
          </div>

          {cell.collapsed ? null : editing ? (
            <textarea
              ref={taRef}
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              onBlur={commitAndClose}
              onKeyDown={(e) => {
                e.stopPropagation();
                if (e.key === "Escape") {
                  e.preventDefault();
                  commitAndClose();
                }
              }}
              onClick={(e) => e.stopPropagation()}
              onPointerDown={(e) => e.stopPropagation()}
              spellCheck={false}
              placeholder="One frame per line…"
              className="w-full font-mono text-sm leading-relaxed p-2 rounded-lg border-2 border-ink/60 dark:border-white/30 bg-white dark:bg-[#1f2228] text-ink dark:text-white nodrag nowheel"
              style={{ minHeight: 140, resize: "vertical" }}
            />
          ) : total === 0 ? (
            <div
              className="px-1 nodrag"
              onDoubleClick={(e) => { e.stopPropagation(); enterEdit(); }}
              title="Double-click to edit"
            >
              <p className="font-hand text-lg text-ink/50 dark:text-white/50 italic">
                (no frames — double-click to add some)
              </p>
            </div>
          ) : presenting ? (
            // Present mode: just the active frame, re-keyed so the
            // entrance animation re-fires on every Space/→ advance.
            <div className="px-1 min-h-[120px] flex items-center justify-center">
              <div
                key={activeIdx}
                className={`anim-frame anim-${transition} font-hand text-3xl text-center text-ink dark:text-white`}
              >
                {frameAt(frames, step)}
              </div>
            </div>
          ) : (
            // Edit canvas: the whole numbered sequence so the author can
            // see (and reorder, in iter 228) every frame.
            <div
              className="px-1 nodrag space-y-1"
              onDoubleClick={(e) => { e.stopPropagation(); enterEdit(); }}
              title="Double-click to edit frames"
            >
              {frames.map((f, i) => (
                <div
                  key={i}
                  className="flex items-baseline gap-2 font-hand text-lg text-ink dark:text-white"
                >
                  <span className="font-mono text-xs text-ink/40 dark:text-white/40 shrink-0">
                    {i + 1}.
                  </span>
                  <span className="truncate">{f}</span>
                </div>
              ))}
            </div>
          )}

          {/* Frame position dots — shown when there's a sequence. */}
          {!cell.collapsed && !editing && total > 1 && (
            <div className="flex items-center justify-center gap-1.5 mt-2">
              {frames.map((_, i) => (
                <span
                  key={i}
                  className={`inline-block w-2 h-2 rounded-full border border-ink/40 dark:border-white/40 ${
                    presenting && i === activeIdx
                      ? "bg-marker-pink"
                      : "bg-transparent"
                  }`}
                />
              ))}
              <span className="font-mono text-[10px] text-ink/40 dark:text-white/40 ml-1">
                {presenting ? `${activeIdx + 1}/${total}` : `${total} frames`}
              </span>
            </div>
          )}
        </div>
      </div>

      <Handle type="source" position={Position.Right} className="!bg-transparent !border-0" />
    </div>
  );
}
