import { Handle, NodeProps, Position } from "reactflow";
import { DoodleBorder } from "./DoodleBorder";
import { useStore } from "../store";

const BUBBLE_W = 280;

/**
 * Speech-bubble node — ONE callout from a cell's `callouts` array.
 *
 * Editing happens in a modal (CalloutEditor) which can manage the
 * full list with text + image per bubble. The bubble itself is
 * read-only here; double-click anywhere opens the editor.
 *
 * Synthetic id format: `${cellId}::callout::${index}`.
 */
export function CalloutBubble({ data }: NodeProps<{ cellId: string; index: number }>) {
  const { cellId, index } = data;
  const cell = useStore((s) => s.cells.find((c) => c.id === cellId));
  const openEditor = useStore((s) => s.openCalloutEditor);
  const setSelected = useStore((s) => s.setSelected);

  const callout = cell?.callouts?.[index];
  if (!cell || !callout) return null;

  return (
    <div
      className="relative"
      style={{ width: BUBBLE_W }}
      onClickCapture={(e) => { e.stopPropagation(); setSelected(cellId); }}
      onDoubleClick={(e) => { e.stopPropagation(); openEditor(cellId); }}
      title="Double-click to edit callouts"
    >
      {/* Hidden ReactFlow handles. Without these, ReactFlow's
       *  EdgeRenderer rejects any edge with this node as a target
       *  (it checks `targetIsValid` which requires measured handle
       *  bounds). Visually hidden — we just need the DOM elements
       *  so the internal store records valid handle rects. */}
      <Handle type="target" position={Position.Left}  className="!opacity-0 !pointer-events-none" />
      <Handle type="source" position={Position.Right} className="!opacity-0 !pointer-events-none" />
      <div className="relative p-3 pt-2">
        <DoodleBorder
          stroke="var(--doodle-stroke, #2a2a2a)"
          fill="#fff3a3"
          strokeWidth={2.5}
          radius={14}
        />
        <div className="relative">
          {/* Header */}
          <div className="flex items-center justify-between mb-1 px-1 nodrag">
            <span className="font-hand text-base text-ink/80 select-none">
              💬 {cell.callouts && cell.callouts.length > 1 ? `${index + 1} / ${cell.callouts.length}` : "Callout"}
            </span>
          </div>

          {/* Image */}
          {callout.image && (
            <img
              src={callout.image}
              alt=""
              className="mb-1.5 rounded border-2 border-ink/60 max-w-full"
              style={{ maxHeight: 180, objectFit: "contain", background: "#fff" }}
            />
          )}

          {/* Text */}
          {callout.text.trim() ? (
            <div className="font-hand text-lg leading-snug px-1 text-ink whitespace-pre-wrap break-words">
              {callout.text}
            </div>
          ) : (
            <div className="font-hand text-base italic text-ink/50 px-1">
              (empty — double-click to edit)
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
